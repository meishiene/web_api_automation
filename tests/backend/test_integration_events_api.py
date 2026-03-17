import hashlib
import hmac
import json

from app.models.integration_event import IntegrationEvent
from app.models.user import User


def _sign(secret: str, payload: bytes) -> str:
    return hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()


def _create_config(client, headers, project_id, secret="webhook-secret", max_attempts=3):
    resp = client.post(
        f"/api/integrations/project/{project_id}",
        headers=headers,
        json={
            "name": "webhook-ingest",
            "integration_type": "webhook",
            "provider": "generic_webhook",
            "credential_value": secret,
            "config_json": {"max_attempts": max_attempts},
            "is_enabled": True,
        },
    )
    assert resp.status_code == 200
    return resp.json()["id"]


def test_webhook_signature_validation_and_idempotency(client, create_user_and_login, auth_headers):
    token = create_user_and_login("owner_events", "pwd")
    headers = auth_headers(token)
    project_id = client.post("/api/projects/", headers=headers, json={"name": "P-events", "description": "desc"}).json()["id"]
    config_id = _create_config(client, headers, project_id, secret="s6-secret")

    payload = {"build_id": "b-1", "status": "success"}
    raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

    ingest_headers = {
        "X-Webhook-Signature": f"sha256={_sign('s6-secret', raw)}",
        "X-Idempotency-Key": "event-key-1",
        "Content-Type": "application/json",
    }
    first = client.post(f"/api/integrations/webhooks/{config_id}/events/pipeline.finished", content=raw, headers=ingest_headers)
    assert first.status_code == 200
    assert first.json()["idempotent_reused"] is False
    assert first.json()["event"]["status"] == "processed"
    event_id = first.json()["event"]["id"]

    second = client.post(f"/api/integrations/webhooks/{config_id}/events/pipeline.finished", content=raw, headers=ingest_headers)
    assert second.status_code == 200
    assert second.json()["idempotent_reused"] is True
    assert second.json()["event"]["id"] == event_id

    bad_sig = client.post(
        f"/api/integrations/webhooks/{config_id}/events/pipeline.finished",
        content=raw,
        headers={"X-Webhook-Signature": "sha256=deadbeef", "Content-Type": "application/json"},
    )
    assert bad_sig.status_code == 401
    assert bad_sig.json()["error"]["code"] == "INVALID_WEBHOOK_SIGNATURE"


def test_webhook_retry_pending_and_replay_to_failed(client, create_user_and_login, auth_headers):
    token = create_user_and_login("owner_events_retry", "pwd")
    headers = auth_headers(token)
    project_id = client.post("/api/projects/", headers=headers, json={"name": "P-events-retry", "description": "desc"}).json()["id"]
    config_id = _create_config(client, headers, project_id, secret="retry-secret", max_attempts=2)

    payload = {"force_fail": True}
    raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ingest_headers = {"X-Webhook-Signature": _sign("retry-secret", raw), "Content-Type": "application/json"}

    ingest = client.post(f"/api/integrations/webhooks/{config_id}/events/pipeline.failed", content=raw, headers=ingest_headers)
    assert ingest.status_code == 200
    event = ingest.json()["event"]
    assert event["status"] == "retry_pending"
    assert event["attempt_count"] == 1
    assert event["next_retry_at"] is not None

    replay = client.post(f"/api/integrations/events/{event['id']}/replay", headers=headers)
    assert replay.status_code == 200
    replay_event = replay.json()
    assert replay_event["status"] == "failed"
    assert replay_event["attempt_count"] == 2
    assert replay_event["next_retry_at"] is None


def test_event_access_control_and_listing(client, create_user_and_login, auth_headers, db_session):
    owner_token = create_user_and_login("owner_events_acl", "pwd")
    attacker_token = create_user_and_login("attacker_events_acl", "pwd")
    admin_token = create_user_and_login("admin_events_acl", "pwd")

    admin = db_session.query(User).filter(User.username == "admin_events_acl").first()
    admin.role = "admin"
    db_session.commit()

    owner_headers = auth_headers(owner_token)
    project_id = client.post("/api/projects/", headers=owner_headers, json={"name": "P-events-acl", "description": "desc"}).json()["id"]
    config_id = _create_config(client, owner_headers, project_id, secret="acl-secret")

    raw = json.dumps({"k": "v"}).encode("utf-8")
    sig = _sign("acl-secret", raw)
    ingest = client.post(
        f"/api/integrations/webhooks/{config_id}/events/deploy.done",
        content=raw,
        headers={"X-Webhook-Signature": sig, "Content-Type": "application/json"},
    )
    assert ingest.status_code == 200
    event_id = ingest.json()["event"]["id"]

    list_owner = client.get(f"/api/integrations/project/{project_id}/events?page=1&page_size=20", headers=owner_headers)
    assert list_owner.status_code == 200
    assert list_owner.json()["total"] == 1

    list_attacker = client.get(
        f"/api/integrations/project/{project_id}/events?page=1&page_size=20",
        headers=auth_headers(attacker_token),
    )
    assert list_attacker.status_code == 403
    assert list_attacker.json()["error"]["code"] == "FORBIDDEN"

    replay_attacker = client.post(f"/api/integrations/events/{event_id}/replay", headers=auth_headers(attacker_token))
    assert replay_attacker.status_code == 403
    assert replay_attacker.json()["error"]["code"] == "FORBIDDEN"

    get_admin = client.get(f"/api/integrations/events/{event_id}", headers=auth_headers(admin_token))
    assert get_admin.status_code == 200
    assert get_admin.json()["event_type"] == "deploy.done"


def test_ingest_writes_event_row(client, create_user_and_login, auth_headers, db_session):
    token = create_user_and_login("owner_events_db", "pwd")
    headers = auth_headers(token)
    project_id = client.post("/api/projects/", headers=headers, json={"name": "P-events-db", "description": "desc"}).json()["id"]
    config_id = _create_config(client, headers, project_id, secret="db-secret")

    raw = b'{"job":"n1"}'
    response = client.post(
        f"/api/integrations/webhooks/{config_id}/events/job.finished",
        content=raw,
        headers={"X-Webhook-Signature": _sign("db-secret", raw), "Content-Type": "application/json"},
    )
    assert response.status_code == 200

    row = db_session.query(IntegrationEvent).filter(IntegrationEvent.integration_config_id == config_id).first()
    assert row is not None
    assert row.project_id == project_id
    assert row.status in {"processed", "retry_pending", "failed"}
