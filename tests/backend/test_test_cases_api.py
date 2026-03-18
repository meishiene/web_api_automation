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

def test_import_openapi_spec_creates_test_cases(client, create_user_and_login, auth_headers):
    token = create_user_and_login("owner_openapi", "pwd")
    headers = auth_headers(token)

    project_resp = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P-openapi", "description": "desc"},
    )
    assert project_resp.status_code == 200
    project_id = project_resp.json()["id"]

    spec = {
        "openapi": "3.0.3",
        "servers": [{"url": "https://api.example.com"}],
        "paths": {
            "/users": {
                "get": {
                    "operationId": "listUsers",
                    "responses": {"200": {"description": "ok"}},
                },
                "post": {
                    "responses": {"201": {"description": "created"}},
                },
            }
        },
    }

    resp = client.post(
        f"/api/test-cases/project/{project_id}/import/openapi",
        headers=headers,
        json={"spec": spec, "case_group": "openapi", "tags": ["imported"]},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["imported"] == 2
    assert body["skipped"] == 0
    assert len(body["created_case_ids"]) == 2

    cases_resp = client.get(f"/api/test-cases/project/{project_id}", headers=headers)
    assert cases_resp.status_code == 200
    cases = cases_resp.json()
    assert len(cases) == 2

    by_method = {item["method"]: item for item in cases}
    assert by_method["GET"]["name"] == "listUsers"
    assert by_method["GET"]["url"] == "https://api.example.com/users"
    assert by_method["GET"]["expected_status"] == 200
    assert by_method["GET"]["case_group"] == "openapi"
    assert by_method["GET"]["tags"] == ["imported"]

    assert by_method["POST"]["name"] == "POST /users"
    assert by_method["POST"]["url"] == "https://api.example.com/users"
    assert by_method["POST"]["expected_status"] == 201


def test_import_openapi_spec_skip_duplicates(client, create_user_and_login, auth_headers):
    token = create_user_and_login("owner_openapi_dup", "pwd")
    headers = auth_headers(token)

    project_id = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P-openapi-dup", "description": "desc"},
    ).json()["id"]

    spec = {
        "openapi": "3.0.0",
        "paths": {
            "/health": {
                "get": {
                    "responses": {"200": {"description": "ok"}},
                }
            }
        },
    }

    first = client.post(
        f"/api/test-cases/project/{project_id}/import/openapi",
        headers=headers,
        json={"spec": spec},
    )
    assert first.status_code == 200
    assert first.json()["imported"] == 1

    second = client.post(
        f"/api/test-cases/project/{project_id}/import/openapi",
        headers=headers,
        json={"spec": spec, "skip_duplicates": True},
    )
    assert second.status_code == 200
    assert second.json()["imported"] == 0
    assert second.json()["skipped"] == 1


def test_import_openapi_spec_invalid_payload_returns_400(client, create_user_and_login, auth_headers):
    token = create_user_and_login("owner_openapi_invalid", "pwd")
    headers = auth_headers(token)

    project_id = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P-openapi-invalid", "description": "desc"},
    ).json()["id"]

    resp = client.post(
        f"/api/test-cases/project/{project_id}/import/openapi",
        headers=headers,
        json={"spec": {"openapi": "3.0.0", "paths": {}}},
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


def test_non_owner_cannot_import_openapi_to_foreign_project(client, create_user_and_login, auth_headers):
    owner_token = create_user_and_login("owner_openapi_acl", "pwd")
    attacker_token = create_user_and_login("attacker_openapi_acl", "pwd")

    project_id = client.post(
        "/api/projects/",
        headers=auth_headers(owner_token),
        json={"name": "P-openapi-acl", "description": "desc"},
    ).json()["id"]

    spec = {
        "openapi": "3.0.0",
        "paths": {
            "/health": {
                "get": {
                    "responses": {"200": {"description": "ok"}},
                }
            }
        },
    }

    resp = client.post(
        f"/api/test-cases/project/{project_id}/import/openapi",
        headers=auth_headers(attacker_token),
        json={"spec": spec},
    )
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "FORBIDDEN"

def test_import_with_unknown_provider_returns_400(client, create_user_and_login, auth_headers):
    token = create_user_and_login("owner_provider_unknown", "pwd")
    headers = auth_headers(token)

    project_id = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P-provider-unknown", "description": "desc"},
    ).json()["id"]

    resp = client.post(
        f"/api/test-cases/project/{project_id}/import/provider",
        headers=headers,
        json={"provider": "missing-provider", "payload": {"foo": "bar"}},
    )
    assert resp.status_code == 400
    body = resp.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"


def test_import_provider_dispatch_and_fallback(client, create_user_and_login, auth_headers):
    token = create_user_and_login("owner_provider_dispatch", "pwd")
    headers = auth_headers(token)

    project_id = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P-provider-dispatch", "description": "desc"},
    ).json()["id"]

    spec = {
        "openapi": "3.0.3",
        "servers": [{"url": "https://api.provider.com"}],
        "paths": {
            "/ping": {
                "get": {
                    "operationId": "ping",
                    "responses": {"200": {"description": "ok"}},
                }
            }
        },
    }

    explicit = client.post(
        f"/api/test-cases/project/{project_id}/import/provider",
        headers=headers,
        json={
            "provider": "openapi",
            "payload": {"spec": spec, "case_group": "provider-explicit", "tags": ["provider"]},
        },
    )
    assert explicit.status_code == 200
    explicit_body = explicit.json()
    assert explicit_body["imported"] == 1

    fallback_project_id = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P-provider-fallback", "description": "desc"},
    ).json()["id"]

    fallback = client.post(
        f"/api/test-cases/project/{fallback_project_id}/import/provider",
        headers=headers,
        json={
            "payload": {"spec": spec, "case_group": "provider-fallback", "tags": ["auto"]},
        },
    )
    assert fallback.status_code == 200
    fallback_body = fallback.json()
    assert fallback_body["imported"] == 1

    list_resp = client.get(f"/api/test-cases/project/{fallback_project_id}", headers=headers)
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) == 1
    assert items[0]["name"] == "ping"
    assert items[0]["case_group"] == "provider-fallback"
    assert items[0]["tags"] == ["auto"]

