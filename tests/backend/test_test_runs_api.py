from app.models.user import User


def test_run_test_case_and_query_runs(client, monkeypatch, create_user_and_login, auth_headers):
    token = create_user_and_login("owner", "pwd")
    headers = auth_headers(token)

    project_resp = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P1", "description": "desc"},
    )
    assert project_resp.status_code == 200
    project_id = project_resp.json()["id"]

    case_resp = client.post(
        f"/api/test-cases/project/{project_id}",
        headers=headers,
        json={
            "name": "Case 1",
            "method": "GET",
            "url": "https://example.com",
            "expected_status": 200,
        },
    )
    assert case_resp.status_code == 200
    case_id = case_resp.json()["id"]

    async def fake_execute_test(_test_case):
        return {
            "status": "success",
            "actual_status": 200,
            "actual_body": "{\"ok\": true}",
            "error_message": None,
            "duration_ms": 12,
        }

    monkeypatch.setattr("app.api.test_runs.execute_test", fake_execute_test)

    run_resp = client.post(f"/api/test-runs/test-cases/{case_id}/run", headers=headers)
    assert run_resp.status_code == 200
    run_body = run_resp.json()
    assert run_body["status"] == "success"
    assert run_body["actual_status"] == 200

    list_resp = client.get(f"/api/test-runs/project/{project_id}", headers=headers)
    assert list_resp.status_code == 200
    runs = list_resp.json()
    assert len(runs) == 1
    assert runs[0]["test_case_id"] == case_id


def test_non_owner_cannot_run_foreign_test_case(client, monkeypatch, create_user_and_login, auth_headers):
    owner_token = create_user_and_login("owner", "pwd")
    attacker_token = create_user_and_login("attacker", "pwd")

    project_resp = client.post(
        "/api/projects/",
        headers=auth_headers(owner_token),
        json={"name": "P1", "description": "desc"},
    )
    project_id = project_resp.json()["id"]

    case_resp = client.post(
        f"/api/test-cases/project/{project_id}",
        headers=auth_headers(owner_token),
        json={
            "name": "Case 1",
            "method": "GET",
            "url": "https://example.com",
            "expected_status": 200,
        },
    )
    case_id = case_resp.json()["id"]

    async def fake_execute_test(_test_case):
        return {
            "status": "success",
            "actual_status": 200,
            "actual_body": "{\"ok\": true}",
            "error_message": None,
            "duration_ms": 12,
        }

    monkeypatch.setattr("app.api.test_runs.execute_test", fake_execute_test)
    run_resp = client.post(f"/api/test-runs/test-cases/{case_id}/run", headers=auth_headers(attacker_token))
    assert run_resp.status_code == 403
    assert run_resp.json()["error"]["code"] == "FORBIDDEN"


def test_admin_can_view_foreign_project_runs(client, monkeypatch, create_user_and_login, auth_headers, db_session):
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

    case_resp = client.post(
        f"/api/test-cases/project/{project_id}",
        headers=auth_headers(owner_token),
        json={
            "name": "Case 1",
            "method": "GET",
            "url": "https://example.com",
            "expected_status": 200,
        },
    )
    case_id = case_resp.json()["id"]

    async def fake_execute_test(_test_case):
        return {
            "status": "success",
            "actual_status": 200,
            "actual_body": "{\"ok\": true}",
            "error_message": None,
            "duration_ms": 12,
        }

    monkeypatch.setattr("app.api.test_runs.execute_test", fake_execute_test)
    client.post(f"/api/test-runs/test-cases/{case_id}/run", headers=auth_headers(owner_token))

    list_resp = client.get(f"/api/test-runs/project/{project_id}", headers=auth_headers(admin_token))
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1
def test_get_test_run_detail_returns_case_metadata(client, monkeypatch, create_user_and_login, auth_headers):
    token = create_user_and_login("owner2", "pwd")
    headers = auth_headers(token)

    project_resp = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P2", "description": "desc"},
    )
    project_id = project_resp.json()["id"]

    case_resp = client.post(
        f"/api/test-cases/project/{project_id}",
        headers=headers,
        json={
            "name": "Case Detail",
            "method": "GET",
            "url": "https://example.com/profile",
            "expected_status": 200,
        },
    )
    case_id = case_resp.json()["id"]

    async def fake_execute_test(_test_case):
        return {
            "status": "success",
            "actual_status": 200,
            "actual_body": "{\"ok\": true}",
            "error_message": None,
            "duration_ms": 18,
        }

    monkeypatch.setattr("app.api.test_runs.execute_test", fake_execute_test)

    run_resp = client.post(f"/api/test-runs/test-cases/{case_id}/run", headers=headers)
    run_id = run_resp.json()["id"]

    detail_resp = client.get(f"/api/test-runs/{run_id}", headers=headers)
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert detail["id"] == run_id
    assert detail["test_case_id"] == case_id
    assert detail["test_case_name"] == "Case Detail"
    assert detail["test_case_method"] == "GET"
    assert detail["test_case_url"] == "https://example.com/profile"
    assert detail["test_case_expected_status"] == 200


def test_non_owner_cannot_view_foreign_test_run_detail(client, monkeypatch, create_user_and_login, auth_headers):
    owner_token = create_user_and_login("owner3", "pwd")
    attacker_token = create_user_and_login("attacker3", "pwd")

    project_resp = client.post(
        "/api/projects/",
        headers=auth_headers(owner_token),
        json={"name": "P3", "description": "desc"},
    )
    project_id = project_resp.json()["id"]

    case_resp = client.post(
        f"/api/test-cases/project/{project_id}",
        headers=auth_headers(owner_token),
        json={
            "name": "Case 3",
            "method": "GET",
            "url": "https://example.com",
            "expected_status": 200,
        },
    )
    case_id = case_resp.json()["id"]

    async def fake_execute_test(_test_case):
        return {
            "status": "success",
            "actual_status": 200,
            "actual_body": "{\"ok\": true}",
            "error_message": None,
            "duration_ms": 12,
        }

    monkeypatch.setattr("app.api.test_runs.execute_test", fake_execute_test)

    run_resp = client.post(f"/api/test-runs/test-cases/{case_id}/run", headers=auth_headers(owner_token))
    run_id = run_resp.json()["id"]

    detail_resp = client.get(f"/api/test-runs/{run_id}", headers=auth_headers(attacker_token))
    assert detail_resp.status_code == 403
    assert detail_resp.json()["error"]["code"] == "FORBIDDEN"


def test_run_detail_contains_runtime_variable_snapshot(client, monkeypatch, create_user_and_login, auth_headers):
    token = create_user_and_login("owner_runtime", "pwd")
    headers = auth_headers(token)

    project_resp = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P-runtime", "description": "desc"},
    )
    project_id = project_resp.json()["id"]

    assert client.post(
        f"/api/environments/project/{project_id}/variables",
        headers=headers,
        json={"key": "base_url", "value": "https://project.example.com", "is_secret": False},
    ).status_code == 200
    assert client.post(
        f"/api/environments/project/{project_id}/variables",
        headers=headers,
        json={"key": "api_key", "value": "project-secret", "is_secret": True},
    ).status_code == 200

    case_resp = client.post(
        f"/api/test-cases/project/{project_id}",
        headers=headers,
        json={
            "name": "Case runtime detail",
            "method": "GET",
            "url": "{{base_url}}/profile?key={{api_key}}",
            "expected_status": 200,
        },
    )
    case_id = case_resp.json()["id"]

    async def fake_execute_test(_test_case, runtime_variables=None):
        assert runtime_variables is not None
        assert runtime_variables["base_url"] == "https://project.example.com"
        assert runtime_variables["api_key"] == "project-secret"
        return {
            "status": "success",
            "actual_status": 200,
            "actual_body": "{\"ok\": true}",
            "error_message": None,
            "duration_ms": 19,
            "extracted_variables": {},
        }

    monkeypatch.setattr("app.api.test_runs.execute_test", fake_execute_test)

    run_resp = client.post(f"/api/test-runs/test-cases/{case_id}/run", headers=headers)
    assert run_resp.status_code == 200
    run_id = run_resp.json()["id"]

    detail_resp = client.get(f"/api/test-runs/{run_id}", headers=headers)
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert detail["runtime_variables"]["base_url"] == "https://project.example.com"
    assert detail["runtime_variables"]["api_key"] == "******"
    assert detail["variable_sources"]["base_url"] == "project"
    assert detail["variable_sources"]["api_key"] == "project"
