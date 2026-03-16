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
def test_test_case_group_tags_and_filters(client, create_user_and_login, auth_headers):
    token = create_user_and_login("owner_group", "pwd")
    headers = auth_headers(token)

    project_resp = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P-group", "description": "desc"},
    )
    assert project_resp.status_code == 200
    project_id = project_resp.json()["id"]

    first = client.post(
        f"/api/test-cases/project/{project_id}",
        headers=headers,
        json={
            "name": "login-success",
            "method": "GET",
            "url": "https://example.com/auth/login",
            "expected_status": 200,
            "case_group": "smoke",
            "tags": ["auth", "login"],
        },
    )
    assert first.status_code == 200
    assert first.json()["case_group"] == "smoke"
    assert first.json()["tags"] == ["auth", "login"]

    second = client.post(
        f"/api/test-cases/project/{project_id}",
        headers=headers,
        json={
            "name": "profile-query",
            "method": "GET",
            "url": "https://example.com/user/profile",
            "expected_status": 200,
            "case_group": "regression",
            "tags": ["user"],
        },
    )
    assert second.status_code == 200

    third = client.post(
        f"/api/test-cases/project/{project_id}",
        headers=headers,
        json={
            "name": "login-failed",
            "method": "POST",
            "url": "https://example.com/auth/login-failed",
            "expected_status": 401,
            "case_group": "smoke",
            "tags": ["auth", "negative"],
        },
    )
    assert third.status_code == 200

    list_keyword = client.get(
        f"/api/test-cases/project/{project_id}",
        headers=headers,
        params={"keyword": "login"},
    )
    assert list_keyword.status_code == 200
    assert len(list_keyword.json()) == 2

    list_group = client.get(
        f"/api/test-cases/project/{project_id}",
        headers=headers,
        params={"case_group": "smoke"},
    )
    assert list_group.status_code == 200
    assert len(list_group.json()) == 2

    list_tag = client.get(
        f"/api/test-cases/project/{project_id}",
        headers=headers,
        params={"tag": "auth"},
    )
    assert list_tag.status_code == 200
    assert len(list_tag.json()) == 2



def test_update_test_case_group_and_tags(client, create_user_and_login, auth_headers):
    token = create_user_and_login("owner_update_group", "pwd")
    headers = auth_headers(token)

    project_resp = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P-update-group", "description": "desc"},
    )
    project_id = project_resp.json()["id"]

    create_resp = client.post(
        f"/api/test-cases/project/{project_id}",
        headers=headers,
        json={
            "name": "case-origin",
            "method": "GET",
            "url": "https://example.com/origin",
            "expected_status": 200,
        },
    )
    case_id = create_resp.json()["id"]

    update_resp = client.put(
        f"/api/test-cases/{case_id}",
        headers=headers,
        json={
            "name": "case-origin",
            "method": "GET",
            "url": "https://example.com/origin",
            "expected_status": 200,
            "case_group": "smoke",
            "tags": ["core", "happy-path"],
        },
    )
    assert update_resp.status_code == 200
    body = update_resp.json()
    assert body["case_group"] == "smoke"
    assert body["tags"] == ["core", "happy-path"]
def test_copy_export_import_test_cases(client, create_user_and_login, auth_headers):
    token = create_user_and_login("owner_io", "pwd")
    headers = auth_headers(token)

    project_resp = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P-io", "description": "desc"},
    )
    project_id = project_resp.json()["id"]

    create_resp = client.post(
        f"/api/test-cases/project/{project_id}",
        headers=headers,
        json={
            "name": "case-a",
            "method": "GET",
            "url": "https://example.com/a",
            "expected_status": 200,
            "case_group": "smoke",
            "tags": ["core", "auth"],
        },
    )
    assert create_resp.status_code == 200
    case_id = create_resp.json()["id"]

    copy_resp = client.post(
        f"/api/test-cases/{case_id}/copy",
        headers=headers,
        json={"name": "case-a-copy"},
    )
    assert copy_resp.status_code == 200
    assert copy_resp.json()["name"] == "case-a-copy"
    assert copy_resp.json()["case_group"] == "smoke"
    assert copy_resp.json()["tags"] == ["core", "auth"]

    export_resp = client.get(f"/api/test-cases/project/{project_id}/export", headers=headers)
    assert export_resp.status_code == 200
    export_body = export_resp.json()
    assert export_body["project_id"] == project_id
    assert export_body["total_cases"] == 2
    assert len(export_body["cases"]) == 2

    import_project_resp = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P-import", "description": "desc"},
    )
    import_project_id = import_project_resp.json()["id"]

    import_resp = client.post(
        f"/api/test-cases/project/{import_project_id}/import",
        headers=headers,
        json={"cases": export_body["cases"]},
    )
    assert import_resp.status_code == 200
    import_body = import_resp.json()
    assert import_body["imported"] == 2
    assert import_body["skipped"] == 0

    duplicate_import_resp = client.post(
        f"/api/test-cases/project/{import_project_id}/import",
        headers=headers,
        json={"cases": export_body["cases"], "skip_duplicates": True},
    )
    assert duplicate_import_resp.status_code == 200
    assert duplicate_import_resp.json()["imported"] == 0
    assert duplicate_import_resp.json()["skipped"] == 2
