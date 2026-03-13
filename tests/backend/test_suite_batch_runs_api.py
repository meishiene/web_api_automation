
def test_run_suite_generates_batch_and_uses_env_variables(client, monkeypatch, create_user_and_login, auth_headers):
    token = create_user_and_login("owner", "pwd")
    headers = auth_headers(token)

    project_resp = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P1", "description": "desc"},
    )
    project_id = project_resp.json()["id"]

    case1_resp = client.post(
        f"/api/test-cases/project/{project_id}",
        headers=headers,
        json={
            "name": "case-login",
            "method": "POST",
            "url": "{{base_url}}/login",
            "body": '{"user":"{{username}}"}',
            "expected_status": 200,
            "extraction_rules": '[{"name":"auth_token","path":"$.token"}]',
        },
    )
    assert case1_resp.status_code == 200
    case1_id = case1_resp.json()["id"]

    case2_resp = client.post(
        f"/api/test-cases/project/{project_id}",
        headers=headers,
        json={
            "name": "case-profile",
            "method": "GET",
            "url": "{{base_url}}/profile",
            "headers": '{"Authorization":"Bearer {{auth_token}}"}',
            "expected_status": 200,
        },
    )
    assert case2_resp.status_code == 200
    case2_id = case2_resp.json()["id"]

    suite_resp = client.post(
        f"/api/test-suites/project/{project_id}",
        headers=headers,
        json={"name": "regression", "description": "desc"},
    )
    suite_id = suite_resp.json()["id"]

    assert client.post(f"/api/test-suites/{suite_id}/cases/{case1_id}", headers=headers, json={"order_index": 1}).status_code == 200
    assert client.post(f"/api/test-suites/{suite_id}/cases/{case2_id}", headers=headers, json={"order_index": 2}).status_code == 200

    env_resp = client.post(
        f"/api/environments/project/{project_id}",
        headers=headers,
        json={"name": "staging", "description": "staging env"},
    )
    env_id = env_resp.json()["id"]

    assert client.post(
        f"/api/environments/project/{project_id}/variables",
        headers=headers,
        json={"key": "base_url", "value": "https://project.example.com", "is_secret": False},
    ).status_code == 200
    assert client.post(
        f"/api/environments/project/{project_id}/variables",
        headers=headers,
        json={"key": "username", "value": "owner", "is_secret": False},
    ).status_code == 200
    assert client.post(
        f"/api/environments/{env_id}/variables",
        headers=headers,
        json={"key": "base_url", "value": "https://staging.example.com", "is_secret": False},
    ).status_code == 200

    calls = []

    async def fake_execute_test(test_case, runtime_variables=None):
        calls.append({"case_id": test_case.id, "vars": dict(runtime_variables or {})})
        if test_case.name == "case-login":
            return {
                "status": "success",
                "actual_status": 200,
                "actual_body": '{"token":"abc-token"}',
                "error_message": None,
                "duration_ms": 10,
                "extracted_variables": {"auth_token": "abc-token"},
            }
        return {
            "status": "success",
            "actual_status": 200,
            "actual_body": '{"ok":true}',
            "error_message": None,
            "duration_ms": 11,
            "extracted_variables": {},
        }

    monkeypatch.setattr("app.api.test_runs.execute_test", fake_execute_test)

    run_resp = client.post(
        f"/api/test-runs/suites/{suite_id}/run",
        headers=headers,
        json={"environment_id": env_id},
    )
    assert run_resp.status_code == 200
    run_body = run_resp.json()
    assert run_body["status"] == "success"
    assert run_body["total_cases"] == 2
    assert run_body["passed_cases"] == 2

    batches_resp = client.get(f"/api/test-runs/batches/project/{project_id}", headers=headers)
    assert batches_resp.status_code == 200
    assert len(batches_resp.json()) == 1

    batch_id = batches_resp.json()[0]["id"]
    batch_detail_resp = client.get(f"/api/test-runs/batches/{batch_id}", headers=headers)
    assert batch_detail_resp.status_code == 200
    assert len(batch_detail_resp.json()["items"]) == 2

    assert calls[0]["vars"]["base_url"] == "https://staging.example.com"
    assert calls[0]["vars"]["username"] == "owner"
    assert calls[1]["vars"]["auth_token"] == "abc-token"
