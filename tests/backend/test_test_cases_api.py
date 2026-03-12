from app.models.user import User


def test_create_test_case_normalizes_method_and_rejects_duplicate_name(
    client,
    create_user_and_login,
    auth_headers,
):
    token = create_user_and_login("owner", "pwd")
    headers = auth_headers(token)

    project_resp = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P1", "description": "desc"},
    )
    assert project_resp.status_code == 200
    project_id = project_resp.json()["id"]

    first_case = client.post(
        f"/api/test-cases/project/{project_id}",
        headers=headers,
        json={
            "name": "case-1",
            "method": "get",
            "url": "https://example.com",
            "expected_status": 200,
        },
    )
    assert first_case.status_code == 200
    assert first_case.json()["method"] == "GET"

    duplicate_case = client.post(
        f"/api/test-cases/project/{project_id}",
        headers=headers,
        json={
            "name": "case-1",
            "method": "GET",
            "url": "https://example.com",
            "expected_status": 200,
        },
    )
    assert duplicate_case.status_code == 400
    body = duplicate_case.json()
    assert body["error"]["code"] == "TEST_CASE_ALREADY_EXISTS"
    assert body["detail"] == "Test case name already exists"


def test_non_owner_cannot_create_test_case_on_foreign_project(client, create_user_and_login, auth_headers):
    owner_token = create_user_and_login("owner", "pwd")
    attacker_token = create_user_and_login("attacker", "pwd")

    project_resp = client.post(
        "/api/projects/",
        headers=auth_headers(owner_token),
        json={"name": "P1", "description": "desc"},
    )
    project_id = project_resp.json()["id"]

    create_resp = client.post(
        f"/api/test-cases/project/{project_id}",
        headers=auth_headers(attacker_token),
        json={
            "name": "hijack-case",
            "method": "GET",
            "url": "https://example.com",
            "expected_status": 200,
        },
    )
    assert create_resp.status_code == 403
    assert create_resp.json()["error"]["code"] == "FORBIDDEN"


def test_admin_can_manage_foreign_project_test_case(client, create_user_and_login, auth_headers, db_session):
    owner_token = create_user_and_login("owner", "pwd")
    admin_token = create_user_and_login("admin", "pwd")
    admin = db_session.query(User).filter(User.username == "admin").first()
    admin.role = "admin"
    db_session.commit()

    project_resp = client.post(
        "/api/projects/",
        headers=auth_headers(owner_token),
        json={"name": "P1", "description": "desc"},
    )
    project_id = project_resp.json()["id"]

    create_case_resp = client.post(
        f"/api/test-cases/project/{project_id}",
        headers=auth_headers(admin_token),
        json={
            "name": "admin-created",
            "method": "GET",
            "url": "https://example.com",
            "expected_status": 200,
        },
    )
    assert create_case_resp.status_code == 200
