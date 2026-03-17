from urllib.parse import parse_qs, urlparse

from app.models.user import User


def _create_identity_config(client, headers, project_id, *, is_enabled=True, auto_create_user=True, name="mock-oauth-main"):

    resp = client.post(
        f"/api/integrations/project/{project_id}",
        headers=headers,
        json={
            "name": name,
            "integration_type": "identity",
            "provider": "mock_oauth",
            "base_url": "https://idp.example.com",
            "credential_value": "oauth-client-secret",
            "config_json": {
                "client_id": "mock-client-id",
                "authorize_url": "https://idp.example.com/oauth/authorize",
                "redirect_uri": "https://platform.example.com/oauth/callback",
                "scope": "openid profile email",
                "auto_create_user": auto_create_user,
            },
            "is_enabled": is_enabled,
        },
    )
    assert resp.status_code == 200
    return resp.json()["id"]


def _parse_state(authorize_url: str) -> str:
    query = parse_qs(urlparse(authorize_url).query)
    return query["state"][0]


def test_identity_oauth_start_and_callback_auto_create_user(client, create_user_and_login, auth_headers):
    owner_token = create_user_and_login("owner_identity", "pwd")
    owner_headers = auth_headers(owner_token)

    project_id = client.post(
        "/api/projects/",
        headers=owner_headers,
        json={"name": "P-identity", "description": "desc"},
    ).json()["id"]
    config_id = _create_identity_config(client, owner_headers, project_id)

    start_resp = client.post(f"/api/integrations/{config_id}/identity/oauth2/start", json={})
    assert start_resp.status_code == 200
    start_body = start_resp.json()
    assert "authorize_url" in start_body
    state = _parse_state(start_body["authorize_url"])
    assert state == start_body["state"]

    callback_resp = client.post(
        f"/api/integrations/{config_id}/identity/oauth2/callback",
        json={
            "state": state,
            "code": "mock-code-001",
            "mock_userinfo": {
                "sub": "idp-user-001",
                "email": "alice@example.com",
                "preferred_username": "alice",
            },
        },
    )
    assert callback_resp.status_code == 200
    callback_body = callback_resp.json()
    assert callback_body["binding_mode"] == "created_user"
    assert callback_body["user"]["username"] == "alice"
    assert callback_body["token_type"] == "bearer"
    assert callback_body["access_token"]
    assert callback_body["refresh_token"]

    replay = client.post(
        f"/api/integrations/{config_id}/identity/oauth2/callback",
        json={
            "state": state,
            "code": "mock-code-002",
            "mock_userinfo": {"sub": "idp-user-001", "email": "alice@example.com"},
        },
    )
    assert replay.status_code == 400
    assert replay.json()["error"]["code"] == "VALIDATION_ERROR"


def test_identity_oauth_callback_links_existing_user_and_reuses_binding(client, create_user_and_login, auth_headers):
    owner_token = create_user_and_login("owner_identity_link", "pwd")
    owner_headers = auth_headers(owner_token)

    project_id = client.post(
        "/api/projects/",
        headers=owner_headers,
        json={"name": "P-identity-link", "description": "desc"},
    ).json()["id"]
    config_id = _create_identity_config(client, owner_headers, project_id)

    # Existing local user should be linked by username/email before creating a new one.
    create_user_and_login("bob", "pwd")

    start_1 = client.post(f"/api/integrations/{config_id}/identity/oauth2/start", json={}).json()
    callback_1 = client.post(
        f"/api/integrations/{config_id}/identity/oauth2/callback",
        json={
            "state": start_1["state"],
            "code": "mock-code-101",
            "mock_userinfo": {
                "sub": "idp-bob-001",
                "email": "bob@example.com",
                "preferred_username": "bob",
            },
        },
    )
    assert callback_1.status_code == 200
    body_1 = callback_1.json()
    assert body_1["binding_mode"] == "linked_existing_user"
    bob_id = body_1["user"]["id"]

    start_2 = client.post(f"/api/integrations/{config_id}/identity/oauth2/start", json={}).json()
    callback_2 = client.post(
        f"/api/integrations/{config_id}/identity/oauth2/callback",
        json={
            "state": start_2["state"],
            "code": "mock-code-102",
            "mock_userinfo": {
                "sub": "idp-bob-001",
                "email": "bob+new@example.com",
                "preferred_username": "bob_new",
            },
        },
    )
    assert callback_2.status_code == 200
    body_2 = callback_2.json()
    assert body_2["binding_mode"] == "reused_existing_binding"
    assert body_2["user"]["id"] == bob_id


def test_identity_oauth_config_guard_and_binding_acl(client, create_user_and_login, auth_headers, db_session):
    owner_token = create_user_and_login("owner_identity_guard", "pwd")
    attacker_token = create_user_and_login("attacker_identity_guard", "pwd")
    admin_token = create_user_and_login("admin_identity_guard", "pwd")

    admin = db_session.query(User).filter(User.username == "admin_identity_guard").first()
    admin.role = "admin"
    db_session.commit()

    owner_headers = auth_headers(owner_token)
    project_id = client.post(
        "/api/projects/",
        headers=owner_headers,
        json={"name": "P-identity-guard", "description": "desc"},
    ).json()["id"]

    cicd_resp = client.post(
        f"/api/integrations/project/{project_id}",
        headers=owner_headers,
        json={
            "name": "cicd-config",
            "integration_type": "cicd",
            "provider": "github_actions",
            "credential_value": "secret",
            "config_json": {"workflow": "regression.yml"},
            "is_enabled": True,
        },
    )
    cicd_id = cicd_resp.json()["id"]

    wrong_type = client.post(f"/api/integrations/{cicd_id}/identity/oauth2/start", json={})
    assert wrong_type.status_code == 400
    assert wrong_type.json()["error"]["code"] == "VALIDATION_ERROR"

    config_id = _create_identity_config(client, owner_headers, project_id, is_enabled=False, name="mock-oauth-disabled")
    disabled = client.post(f"/api/integrations/{config_id}/identity/oauth2/start", json={})
    assert disabled.status_code == 400
    assert disabled.json()["error"]["code"] == "INTEGRATION_CONFIG_DISABLED"

    enabled_id = _create_identity_config(client, owner_headers, project_id, is_enabled=True, name="mock-oauth-enabled")
    start = client.post(f"/api/integrations/{enabled_id}/identity/oauth2/start", json={}).json()
    callback = client.post(
        f"/api/integrations/{enabled_id}/identity/oauth2/callback",
        json={
            "state": start["state"],
            "code": "mock-code-admin",
            "mock_userinfo": {"sub": "idp-admin-001", "email": "guard@example.com"},
        },
    )
    assert callback.status_code == 200

    forbidden_list = client.get(
        f"/api/integrations/{enabled_id}/identity/bindings",
        headers=auth_headers(attacker_token),
    )
    assert forbidden_list.status_code == 403

    admin_list = client.get(
        f"/api/integrations/{enabled_id}/identity/bindings",
        headers=auth_headers(admin_token),
    )
    assert admin_list.status_code == 200
    assert admin_list.json()["total"] == 1


