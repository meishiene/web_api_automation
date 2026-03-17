from app.models.audit_log import AuditLog
from app.models.user import User


def test_integration_config_crud_and_masking(client, create_user_and_login, auth_headers):
    token = create_user_and_login("owner_integration", "pwd")
    headers = auth_headers(token)

    project_resp = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P-integration", "description": "desc"},
    )
    assert project_resp.status_code == 200
    project_id = project_resp.json()["id"]

    create_resp = client.post(
        f"/api/integrations/project/{project_id}",
        headers=headers,
        json={
            "name": "github-actions-main",
            "integration_type": "cicd",
            "provider": "github_actions",
            "base_url": "https://api.github.com",
            "credential_ref": "vault://ci/github/token",
            "credential_value": "ghp-super-secret",
            "config_json": {"workflow": "regression.yml", "repo": "org/repo"},
            "is_enabled": True,
        },
    )
    assert create_resp.status_code == 200
    created = create_resp.json()
    assert created["name"] == "github-actions-main"
    assert created["credential_value"] == "******"
    assert created["has_credential_value"] is True
    assert created["config_json"]["workflow"] == "regression.yml"
    config_id = created["id"]

    list_resp = client.get(f"/api/integrations/project/{project_id}", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1
    assert list_resp.json()[0]["credential_value"] == "******"

    get_resp = client.get(f"/api/integrations/{config_id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["provider"] == "github_actions"

    reveal_resp = client.get(f"/api/integrations/{config_id}/credential-value", headers=headers)
    assert reveal_resp.status_code == 200
    assert reveal_resp.json()["value"] == "ghp-super-secret"

    update_resp = client.put(
        f"/api/integrations/{config_id}",
        headers=headers,
        json={
            "name": "github-actions-main-v2",
            "integration_type": "cicd",
            "provider": "github_actions",
            "base_url": "https://api.github.com",
            "credential_ref": "vault://ci/github/token-v2",
            "credential_value": "ghp-next-secret",
            "config_json": {"workflow": "nightly.yml", "repo": "org/repo"},
            "is_enabled": False,
        },
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["name"] == "github-actions-main-v2"
    assert updated["is_enabled"] is False
    assert updated["credential_value"] == "******"
    assert updated["has_credential_value"] is True

    delete_resp = client.delete(f"/api/integrations/{config_id}", headers=headers)
    assert delete_resp.status_code == 200

    list_after_delete = client.get(f"/api/integrations/project/{project_id}", headers=headers)
    assert list_after_delete.status_code == 200
    assert list_after_delete.json() == []


def test_non_owner_cannot_manage_foreign_integration(client, create_user_and_login, auth_headers):
    owner_token = create_user_and_login("owner_integration_acl", "pwd")
    attacker_token = create_user_and_login("attacker_integration_acl", "pwd")

    project_resp = client.post(
        "/api/projects/",
        headers=auth_headers(owner_token),
        json={"name": "P-integration-acl", "description": "desc"},
    )
    assert project_resp.status_code == 200
    project_id = project_resp.json()["id"]

    create_resp = client.post(
        f"/api/integrations/project/{project_id}",
        headers=auth_headers(owner_token),
        json={
            "name": "webhook-default",
            "integration_type": "webhook",
            "provider": "generic_webhook",
            "credential_value": "secret",
            "config_json": {"path": "/callback"},
        },
    )
    assert create_resp.status_code == 200
    config_id = create_resp.json()["id"]

    list_resp = client.get(
        f"/api/integrations/project/{project_id}",
        headers=auth_headers(attacker_token),
    )
    assert list_resp.status_code == 403
    assert list_resp.json()["error"]["code"] == "FORBIDDEN"

    update_resp = client.put(
        f"/api/integrations/{config_id}",
        headers=auth_headers(attacker_token),
        json={
            "name": "webhook-default",
            "integration_type": "webhook",
            "provider": "generic_webhook",
            "credential_value": "secret-2",
            "config_json": {"path": "/callback"},
            "is_enabled": True,
        },
    )
    assert update_resp.status_code == 403
    assert update_resp.json()["error"]["code"] == "FORBIDDEN"

    reveal_resp = client.get(
        f"/api/integrations/{config_id}/credential-value",
        headers=auth_headers(attacker_token),
    )
    assert reveal_resp.status_code == 403
    assert reveal_resp.json()["error"]["code"] == "FORBIDDEN"


def test_admin_can_manage_foreign_integration(client, create_user_and_login, auth_headers, db_session):
    owner_token = create_user_and_login("owner_integration_admin", "pwd")
    admin_token = create_user_and_login("admin_integration_admin", "pwd")

    admin = db_session.query(User).filter(User.username == "admin_integration_admin").first()
    admin.role = "admin"
    db_session.commit()

    project_resp = client.post(
        "/api/projects/",
        headers=auth_headers(owner_token),
        json={"name": "P-integration-admin", "description": "desc"},
    )
    project_id = project_resp.json()["id"]

    create_resp = client.post(
        f"/api/integrations/project/{project_id}",
        headers=auth_headers(admin_token),
        json={
            "name": "jira-default",
            "integration_type": "defect",
            "provider": "jira",
            "credential_value": "jira-token",
            "config_json": {"project_key": "QA"},
        },
    )
    assert create_resp.status_code == 200
    config_id = create_resp.json()["id"]

    delete_resp = client.delete(
        f"/api/integrations/{config_id}",
        headers=auth_headers(admin_token),
    )
    assert delete_resp.status_code == 200


def test_integration_config_write_audit_logs(client, create_user_and_login, auth_headers, db_session):
    token = create_user_and_login("owner_integration_audit", "pwd")
    headers = auth_headers(token)

    project_resp = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P-integration-audit", "description": "desc"},
    )
    project_id = project_resp.json()["id"]

    create_resp = client.post(
        f"/api/integrations/project/{project_id}",
        headers=headers,
        json={
            "name": "mail-default",
            "integration_type": "notification",
            "provider": "smtp",
            "credential_value": "smtp-secret",
            "config_json": {"host": "smtp.example.com"},
        },
    )
    config_id = create_resp.json()["id"]

    assert client.get(f"/api/integrations/project/{project_id}", headers=headers).status_code == 200
    assert client.get(f"/api/integrations/{config_id}", headers=headers).status_code == 200
    assert client.get(f"/api/integrations/{config_id}/credential-value", headers=headers).status_code == 200

    assert client.put(
        f"/api/integrations/{config_id}",
        headers=headers,
        json={
            "name": "mail-default-v2",
            "integration_type": "notification",
            "provider": "smtp",
            "credential_ref": "vault://smtp/token-v2",
            "credential_value": "smtp-secret-2",
            "config_json": {"host": "smtp2.example.com"},
            "is_enabled": True,
        },
    ).status_code == 200
    assert client.delete(f"/api/integrations/{config_id}", headers=headers).status_code == 200

    expected_actions = {
        "integration_config.create",
        "integration_config.list",
        "integration_config.get",
        "integration_config.reveal_credential",
        "integration_config.update",
        "integration_config.delete",
    }
    logged_actions = {
        row.action
        for row in db_session.query(AuditLog)
        .filter(AuditLog.resource_type == "integration_config")
        .all()
    }
    assert expected_actions.issubset(logged_actions)
