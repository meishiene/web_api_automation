from app.models.audit_log import AuditLog
from app.models.user import User


def _create_defect_config(client, headers, project_id, *, provider="jira", is_enabled=True):
    resp = client.post(
        f"/api/integrations/project/{project_id}",
        headers=headers,
        json={
            "name": f"{provider}-defect-main",
            "integration_type": "defect",
            "provider": provider,
            "base_url": "https://jira.example.com",
            "credential_value": "jira-token",
            "config_json": {
                "project_key": "QA",
                "issue_type": "Bug",
                "issue_key_prefix": "QA",
                "labels": ["auto-test", "integration"],
            },
            "is_enabled": is_enabled,
        },
    )
    assert resp.status_code == 200
    return resp.json()["id"]


def test_defect_sync_create_then_update_by_fingerprint(client, create_user_and_login, auth_headers):
    token = create_user_and_login("owner_defect", "pwd")
    headers = auth_headers(token)
    project_id = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P-defect", "description": "desc"},
    ).json()["id"]
    config_id = _create_defect_config(client, headers, project_id)

    first = client.post(
        f"/api/integrations/{config_id}/defects/sync",
        headers=headers,
        json={
            "run_type": "api",
            "run_id": 101,
            "case_id": 11,
            "case_name": "login_should_return_200",
            "status": "failed",
            "failure_message": "expected 200 got 500",
            "failure_category": "assertion",
            "failure_fingerprint": "fp-login-500",
            "detail_api_path": "/api/test-runs/101",
            "tags": ["smoke"],
        },
    )
    assert first.status_code == 200
    first_body = first.json()
    assert first_body["mode"] == "created"
    assert first_body["record"]["occurrence_count"] == 1
    assert first_body["record"]["issue_key"].startswith("QA-")

    second = client.post(
        f"/api/integrations/{config_id}/defects/sync",
        headers=headers,
        json={
            "run_type": "api",
            "run_id": 102,
            "case_id": 11,
            "case_name": "login_should_return_200",
            "status": "failed",
            "failure_message": "expected 200 got 500",
            "failure_category": "assertion",
            "failure_fingerprint": "fp-login-500",
            "detail_api_path": "/api/test-runs/102",
            "tags": ["smoke"],
        },
    )
    assert second.status_code == 200
    second_body = second.json()
    assert second_body["mode"] == "updated"
    assert second_body["record"]["issue_key"] == first_body["record"]["issue_key"]
    assert second_body["record"]["occurrence_count"] == 2
    assert second_body["record"]["last_run_id"] == 102

    listed = client.get(f"/api/integrations/project/{project_id}/defects/records", headers=headers)
    assert listed.status_code == 200
    list_body = listed.json()
    assert list_body["total"] == 1
    assert list_body["items"][0]["failure_fingerprint"] == "fp-login-500"
    assert list_body["items"][0]["occurrence_count"] == 2


def test_defect_sync_requires_defect_config_and_enabled(client, create_user_and_login, auth_headers):
    token = create_user_and_login("owner_defect_guard", "pwd")
    headers = auth_headers(token)
    project_id = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P-defect-guard", "description": "desc"},
    ).json()["id"]

    cicd_resp = client.post(
        f"/api/integrations/project/{project_id}",
        headers=headers,
        json={
            "name": "gh-cicd",
            "integration_type": "cicd",
            "provider": "github_actions",
            "credential_value": "secret",
            "config_json": {"workflow": "regression.yml"},
            "is_enabled": True,
        },
    )
    assert cicd_resp.status_code == 200
    cicd_id = cicd_resp.json()["id"]

    not_defect = client.post(
        f"/api/integrations/{cicd_id}/defects/sync",
        headers=headers,
        json={
            "run_type": "api",
            "run_id": 1,
            "case_name": "case-a",
            "status": "failed",
            "failure_message": "boom",
        },
    )
    assert not_defect.status_code == 400
    assert not_defect.json()["error"]["code"] == "VALIDATION_ERROR"

    disabled_id = _create_defect_config(client, headers, project_id, provider="jira-disabled", is_enabled=False)
    disabled = client.post(
        f"/api/integrations/{disabled_id}/defects/sync",
        headers=headers,
        json={
            "run_type": "api",
            "run_id": 2,
            "case_name": "case-b",
            "status": "failed",
            "failure_message": "boom",
        },
    )
    assert disabled.status_code == 400
    assert disabled.json()["error"]["code"] == "INTEGRATION_CONFIG_DISABLED"


def test_defect_sync_acl_and_audit(client, create_user_and_login, auth_headers, db_session):
    owner_token = create_user_and_login("owner_defect_acl", "pwd")
    attacker_token = create_user_and_login("attacker_defect_acl", "pwd")
    admin_token = create_user_and_login("admin_defect_acl", "pwd")

    admin = db_session.query(User).filter(User.username == "admin_defect_acl").first()
    admin.role = "admin"
    db_session.commit()

    owner_headers = auth_headers(owner_token)
    project_id = client.post(
        "/api/projects/",
        headers=owner_headers,
        json={"name": "P-defect-acl", "description": "desc"},
    ).json()["id"]
    config_id = _create_defect_config(client, owner_headers, project_id)

    forbidden = client.post(
        f"/api/integrations/{config_id}/defects/sync",
        headers=auth_headers(attacker_token),
        json={
            "run_type": "api",
            "run_id": 10,
            "case_name": "acl-case",
            "status": "failed",
            "failure_message": "acl",
        },
    )
    assert forbidden.status_code == 403
    assert forbidden.json()["error"]["code"] == "FORBIDDEN"

    allowed = client.post(
        f"/api/integrations/{config_id}/defects/sync",
        headers=auth_headers(admin_token),
        json={
            "run_type": "api",
            "run_id": 11,
            "case_name": "acl-case",
            "status": "failed",
            "failure_message": "acl",
            "failure_fingerprint": "acl-fp",
        },
    )
    assert allowed.status_code == 200

    listed = client.get(
        f"/api/integrations/project/{project_id}/defects/records",
        headers=auth_headers(admin_token),
    )
    assert listed.status_code == 200

    actions = {
        row.action
        for row in db_session.query(AuditLog)
        .filter(AuditLog.resource_type.in_(["defect_sync_record", "integration_event"]))
        .all()
    }
    assert "integration_defect.sync" in actions
    assert "integration_defect.record.list" in actions
