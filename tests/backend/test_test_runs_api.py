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
