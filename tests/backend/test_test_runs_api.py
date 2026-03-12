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
