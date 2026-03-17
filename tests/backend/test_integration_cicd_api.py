import hashlib
import hmac
import json

from app.models.audit_log import AuditLog
from app.models.user import User


def _sign(secret: str, payload: bytes) -> str:
    return hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()


def _create_cicd_config(client, headers, project_id, secret="cicd-secret"):
    resp = client.post(
        f"/api/integrations/project/{project_id}",
        headers=headers,
        json={
            "name": "github-actions",
            "integration_type": "cicd",
            "provider": "github_actions",
            "credential_value": secret,
            "config_json": {"workflow": "regression.yml"},
            "is_enabled": True,
        },
    )
    assert resp.status_code == 200
    return resp.json()["id"]


def test_cicd_trigger_and_callback_converges_status(client, create_user_and_login, auth_headers):
    token = create_user_and_login("owner_cicd", "pwd")
    headers = auth_headers(token)

    project_id = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P-cicd", "description": "desc"},
    ).json()["id"]
    config_id = _create_cicd_config(client, headers, project_id, secret="gh-secret")

    trigger_resp = client.post(
        f"/api/integrations/{config_id}/cicd/trigger",
        headers=headers,
        json={
            "pipeline_name": "regression.yml",
            "ref": "main",
            "idempotency_key": "trigger-001",
            "inputs": {"suite": "smoke"},
        },
    )
    assert trigger_resp.status_code == 200
    trigger_body = trigger_resp.json()
    assert trigger_body["idempotent_reused"] is False
    trigger_event_id = trigger_body["event"]["id"]
    assert trigger_body["event"]["direction"] == "outbound"

    callback_payload = {
        "trigger_event_id": trigger_event_id,
        "status": "success",
        "external_run_id": "gha-123",
        "message": "workflow completed",
    }
    raw = json.dumps(callback_payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    callback_resp = client.post(
        f"/api/integrations/webhooks/{config_id}/cicd/callback",
        content=raw,
        headers={
            "X-Webhook-Signature": f"sha256={_sign('gh-secret', raw)}",
            "X-Idempotency-Key": "cb-001",
            "Content-Type": "application/json",
        },
    )
    assert callback_resp.status_code == 200
    callback_body = callback_resp.json()
    assert callback_body["idempotent_reused"] is False
    assert callback_body["trigger_event"]["id"] == trigger_event_id
    assert callback_body["trigger_event"]["status"] == "processed"

    runs_resp = client.get(f"/api/integrations/{config_id}/cicd/runs?page=1&page_size=20", headers=headers)
    assert runs_resp.status_code == 200
    assert runs_resp.json()["total"] == 1
    run_item = runs_resp.json()["items"][0]
    assert run_item["id"] == trigger_event_id
    assert run_item["status"] == "processed"
    assert run_item["payload_json"]["external_run_id"] == "gha-123"


def test_cicd_trigger_idempotency_reuses_existing_event(client, create_user_and_login, auth_headers):
    token = create_user_and_login("owner_cicd_idempotent", "pwd")
    headers = auth_headers(token)

    project_id = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P-cicd-idempotent", "description": "desc"},
    ).json()["id"]
    config_id = _create_cicd_config(client, headers, project_id)

    first = client.post(
        f"/api/integrations/{config_id}/cicd/trigger",
        headers=headers,
        json={"pipeline_name": "regression.yml", "idempotency_key": "same-key"},
    )
    assert first.status_code == 200
    second = client.post(
        f"/api/integrations/{config_id}/cicd/trigger",
        headers=headers,
        json={"pipeline_name": "regression.yml", "idempotency_key": "same-key"},
    )
    assert second.status_code == 200
    assert second.json()["idempotent_reused"] is True
    assert second.json()["event"]["id"] == first.json()["event"]["id"]


def test_cicd_callback_signature_and_permission_guard(client, create_user_and_login, auth_headers, db_session):
    owner_token = create_user_and_login("owner_cicd_guard", "pwd")
    attacker_token = create_user_and_login("attacker_cicd_guard", "pwd")
    admin_token = create_user_and_login("admin_cicd_guard", "pwd")

    admin = db_session.query(User).filter(User.username == "admin_cicd_guard").first()
    admin.role = "admin"
    db_session.commit()

    owner_headers = auth_headers(owner_token)
    project_id = client.post(
        "/api/projects/",
        headers=owner_headers,
        json={"name": "P-cicd-guard", "description": "desc"},
    ).json()["id"]
    config_id = _create_cicd_config(client, owner_headers, project_id, secret="guard-secret")

    forbidden_trigger = client.post(
        f"/api/integrations/{config_id}/cicd/trigger",
        headers=auth_headers(attacker_token),
        json={"pipeline_name": "regression.yml"},
    )
    assert forbidden_trigger.status_code == 403
    assert forbidden_trigger.json()["error"]["code"] == "FORBIDDEN"

    admin_trigger = client.post(
        f"/api/integrations/{config_id}/cicd/trigger",
        headers=auth_headers(admin_token),
        json={"pipeline_name": "regression.yml", "idempotency_key": "admin-trigger"},
    )
    assert admin_trigger.status_code == 200
    trigger_event_id = admin_trigger.json()["event"]["id"]

    bad_payload = {"trigger_event_id": trigger_event_id, "status": "failed"}
    bad_raw = json.dumps(bad_payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    bad_sig_resp = client.post(
        f"/api/integrations/webhooks/{config_id}/cicd/callback",
        content=bad_raw,
        headers={"X-Webhook-Signature": "sha256=bad", "Content-Type": "application/json"},
    )
    assert bad_sig_resp.status_code == 401
    assert bad_sig_resp.json()["error"]["code"] == "INVALID_WEBHOOK_SIGNATURE"


def test_cicd_actions_write_audit_logs(client, create_user_and_login, auth_headers, db_session):
    token = create_user_and_login("owner_cicd_audit", "pwd")
    headers = auth_headers(token)
    project_id = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P-cicd-audit", "description": "desc"},
    ).json()["id"]
    config_id = _create_cicd_config(client, headers, project_id, secret="audit-secret")

    trigger_resp = client.post(
        f"/api/integrations/{config_id}/cicd/trigger",
        headers=headers,
        json={"pipeline_name": "regression.yml", "idempotency_key": "audit-trigger"},
    )
    trigger_event_id = trigger_resp.json()["event"]["id"]

    callback_payload = {"trigger_event_id": trigger_event_id, "status": "failed", "message": "job failed"}
    raw = json.dumps(callback_payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    callback_resp = client.post(
        f"/api/integrations/webhooks/{config_id}/cicd/callback",
        content=raw,
        headers={"X-Webhook-Signature": _sign("audit-secret", raw), "Content-Type": "application/json"},
    )
    assert callback_resp.status_code == 200

    assert client.get(f"/api/integrations/{config_id}/cicd/runs?page=1&page_size=20", headers=headers).status_code == 200

    actions = {row.action for row in db_session.query(AuditLog).filter(AuditLog.resource_type.in_(["integration_event"])).all()}
    assert "integration_cicd.trigger" in actions
    assert "integration_cicd.callback" in actions
    assert "integration_cicd.run.list" in actions
