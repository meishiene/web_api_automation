
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
    detail_body = batch_detail_resp.json()
    assert len(detail_body["items"]) == 2
    first_item = detail_body["items"][0]
    assert first_item["test_case_name"] == "case-login"
    assert first_item["test_case_method"] == "POST"
    assert first_item["actual_status"] == 200
    assert first_item["duration_ms"] == 10

    assert calls[0]["vars"]["base_url"] == "https://staging.example.com"
    assert calls[0]["vars"]["username"] == "owner"
    assert calls[1]["vars"]["auth_token"] == "abc-token"
def test_run_suite_retries_error_then_success(client, monkeypatch, create_user_and_login, auth_headers):
    token = create_user_and_login("owner_retry", "pwd")
    headers = auth_headers(token)

    project_resp = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P-retry", "description": "desc"},
    )
    project_id = project_resp.json()["id"]

    case_resp = client.post(
        f"/api/test-cases/project/{project_id}",
        headers=headers,
        json={
            "name": "case-retry",
            "method": "GET",
            "url": "https://example.com/retry",
            "expected_status": 200,
        },
    )
    case_id = case_resp.json()["id"]

    suite_resp = client.post(
        f"/api/test-suites/project/{project_id}",
        headers=headers,
        json={"name": "retry-suite", "description": "desc"},
    )
    suite_id = suite_resp.json()["id"]
    assert client.post(f"/api/test-suites/{suite_id}/cases/{case_id}", headers=headers, json={"order_index": 1}).status_code == 200

    calls = {"count": 0}

    async def fake_execute_test(test_case, runtime_variables=None):
        calls["count"] += 1
        if calls["count"] == 1:
            return {
                "status": "error",
                "actual_status": None,
                "actual_body": None,
                "error_message": "temporary network error",
                "duration_ms": 8,
                "extracted_variables": {},
            }
        return {
            "status": "success",
            "actual_status": 200,
            "actual_body": "{\"ok\":true}",
            "error_message": None,
            "duration_ms": 9,
            "extracted_variables": {},
        }

    monkeypatch.setattr("app.api.test_runs.execute_test", fake_execute_test)

    run_resp = client.post(
        f"/api/test-runs/suites/{suite_id}/run",
        headers=headers,
        json={"retry_count": 1, "retry_on": ["error"]},
    )
    assert run_resp.status_code == 200
    body = run_resp.json()
    assert body["status"] == "success"
    assert body["passed_cases"] == 1
    assert body["error_cases"] == 0
    assert calls["count"] == 2

    runs_resp = client.get(f"/api/test-runs/project/{project_id}", headers=headers)
    assert runs_resp.status_code == 200
    runs = runs_resp.json()
    assert len(runs) == 1
    assert runs[0]["status"] == "success"


def test_run_suite_with_same_idempotency_key_reuses_batch(client, monkeypatch, create_user_and_login, auth_headers):
    token = create_user_and_login("owner_idem", "pwd")
    headers = auth_headers(token)

    project_resp = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P-idem", "description": "desc"},
    )
    project_id = project_resp.json()["id"]

    case_resp = client.post(
        f"/api/test-cases/project/{project_id}",
        headers=headers,
        json={
            "name": "case-idem",
            "method": "GET",
            "url": "https://example.com/idem",
            "expected_status": 200,
        },
    )
    case_id = case_resp.json()["id"]

    suite_resp = client.post(
        f"/api/test-suites/project/{project_id}",
        headers=headers,
        json={"name": "idem-suite", "description": "desc"},
    )
    suite_id = suite_resp.json()["id"]
    assert client.post(f"/api/test-suites/{suite_id}/cases/{case_id}", headers=headers, json={"order_index": 1}).status_code == 200

    calls = {"count": 0}

    async def fake_execute_test(test_case, runtime_variables=None):
        calls["count"] += 1
        return {
            "status": "success",
            "actual_status": 200,
            "actual_body": "{\"ok\":true}",
            "error_message": None,
            "duration_ms": 7,
            "extracted_variables": {},
        }

    monkeypatch.setattr("app.api.test_runs.execute_test", fake_execute_test)

    first = client.post(
        f"/api/test-runs/suites/{suite_id}/run",
        headers=headers,
        json={"idempotency_key": "run-key-001"},
    )
    second = client.post(
        f"/api/test-runs/suites/{suite_id}/run",
        headers=headers,
        json={"idempotency_key": "run-key-001"},
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["id"] == second.json()["id"]
    assert calls["count"] == 1

    batches_resp = client.get(f"/api/test-runs/batches/project/{project_id}", headers=headers)
    assert batches_resp.status_code == 200
    assert len(batches_resp.json()) == 1
