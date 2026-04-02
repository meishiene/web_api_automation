from app.models.user import User


def test_owner_can_add_member_and_member_can_view_project(client, create_user_and_login, auth_headers):
    owner_token = create_user_and_login("owner", "pwd")
    member_token = create_user_and_login("member", "pwd")

    project_resp = client.post(
        "/api/projects/",
        headers=auth_headers(owner_token),
        json={"name": "P1", "description": "desc"},
    )
    project_id = project_resp.json()["id"]

    add_resp = client.post(
        f"/api/projects/{project_id}/members",
        headers=auth_headers(owner_token),
        json={"user_id": 2, "role": "viewer"},
    )
    assert add_resp.status_code == 200
    assert add_resp.json()["role"] == "viewer"

    project_list_resp = client.get("/api/projects/", headers=auth_headers(member_token))
    assert project_list_resp.status_code == 200
    assert any(item["id"] == project_id for item in project_list_resp.json())

    members_resp = client.get(f"/api/projects/{project_id}/members", headers=auth_headers(member_token))
    assert members_resp.status_code == 200
    assert any(item["user_id"] == 2 and item["username"] == "member" for item in members_resp.json())


def test_authenticated_user_can_list_users(client, create_user_and_login, auth_headers):
    token = create_user_and_login("owner_user_list", "pwd")
    create_user_and_login("member_user_list", "pwd")

    resp = client.get("/api/users", headers=auth_headers(token))
    assert resp.status_code == 200
    users = resp.json()
    assert any(item["username"] == "owner_user_list" for item in users)
    assert any(item["username"] == "member_user_list" for item in users)


def test_viewer_cannot_create_test_case(client, create_user_and_login, auth_headers):
    owner_token = create_user_and_login("owner", "pwd")
    viewer_token = create_user_and_login("viewer", "pwd")

    project_resp = client.post(
        "/api/projects/",
        headers=auth_headers(owner_token),
        json={"name": "P1", "description": "desc"},
    )
    project_id = project_resp.json()["id"]
    client.post(
        f"/api/projects/{project_id}/members",
        headers=auth_headers(owner_token),
        json={"user_id": 2, "role": "viewer"},
    )

    create_case_resp = client.post(
        f"/api/test-cases/project/{project_id}",
        headers=auth_headers(viewer_token),
        json={
            "name": "viewer-case",
            "method": "GET",
            "url": "https://example.com",
            "expected_status": 200,
        },
    )
    assert create_case_resp.status_code == 403
    assert create_case_resp.json()["error"]["code"] == "FORBIDDEN"


def test_editor_can_create_test_case_and_run(client, create_user_and_login, auth_headers, monkeypatch):
    owner_token = create_user_and_login("owner", "pwd")
    editor_token = create_user_and_login("editor", "pwd")

    project_resp = client.post(
        "/api/projects/",
        headers=auth_headers(owner_token),
        json={"name": "P1", "description": "desc"},
    )
    project_id = project_resp.json()["id"]
    client.post(
        f"/api/projects/{project_id}/members",
        headers=auth_headers(owner_token),
        json={"user_id": 2, "role": "editor"},
    )

    create_case_resp = client.post(
        f"/api/test-cases/project/{project_id}",
        headers=auth_headers(editor_token),
        json={
            "name": "editor-case",
            "method": "GET",
            "url": "https://example.com",
            "expected_status": 200,
        },
    )
    assert create_case_resp.status_code == 200
    case_id = create_case_resp.json()["id"]

    async def fake_execute_test(_test_case):
        return {
            "status": "success",
            "actual_status": 200,
            "actual_body": "{\"ok\": true}",
            "error_message": None,
            "duration_ms": 12,
        }

    monkeypatch.setattr("app.api.test_runs.execute_test", fake_execute_test)

    run_resp = client.post(f"/api/test-runs/test-cases/{case_id}/run", headers=auth_headers(editor_token))
    assert run_resp.status_code == 200


def test_maintainer_can_manage_members(client, create_user_and_login, auth_headers):
    owner_token = create_user_and_login("owner", "pwd")
    maintainer_token = create_user_and_login("maintainer", "pwd")
    create_user_and_login("target", "pwd")

    project_resp = client.post(
        "/api/projects/",
        headers=auth_headers(owner_token),
        json={"name": "P1", "description": "desc"},
    )
    project_id = project_resp.json()["id"]

    client.post(
        f"/api/projects/{project_id}/members",
        headers=auth_headers(owner_token),
        json={"user_id": 2, "role": "maintainer"},
    )

    add_resp = client.post(
        f"/api/projects/{project_id}/members",
        headers=auth_headers(maintainer_token),
        json={"user_id": 3, "role": "viewer"},
    )
    assert add_resp.status_code == 200

    remove_resp = client.delete(
        f"/api/projects/{project_id}/members/3",
        headers=auth_headers(maintainer_token),
    )
    assert remove_resp.status_code == 200


def test_admin_can_manage_foreign_project_members(client, create_user_and_login, auth_headers, db_session):
    owner_token = create_user_and_login("owner", "pwd")
    admin_token = create_user_and_login("admin", "pwd")
    create_user_and_login("target", "pwd")

    admin = db_session.query(User).filter(User.username == "admin").first()
    admin.role = "admin"
    db_session.commit()

    project_resp = client.post(
        "/api/projects/",
        headers=auth_headers(owner_token),
        json={"name": "P1", "description": "desc"},
    )
    project_id = project_resp.json()["id"]

    add_resp = client.post(
        f"/api/projects/{project_id}/members",
        headers=auth_headers(admin_token),
        json={"user_id": 3, "role": "viewer"},
    )
    assert add_resp.status_code == 200
