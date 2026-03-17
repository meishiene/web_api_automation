def _create_api_case(client, headers, project_id, name="api-failure-case"):
    resp = client.post(
        f"/api/test-cases/project/{project_id}",
        headers=headers,
        json={
            "name": name,
            "method": "GET",
            "url": "https://example.com/api",
            "expected_status": 200,
        },
    )
    assert resp.status_code == 200
    return resp.json()["id"]


def _create_web_case(client, headers, project_id, name="web-failure-case"):
    resp = client.post(
        "/api/web-test-cases",
        headers=headers,
        json={
            "project_id": project_id,
            "name": name,
            "base_url": "https://example.com",
            "steps": [
                {"action": "open", "params": {"url": "/login"}},
            ],
        },
    )
    assert resp.status_code == 200
    return resp.json()["id"]


def test_report_failures_supports_filters_and_traceability(client, monkeypatch, create_user_and_login, auth_headers):
    token = create_user_and_login("owner_report_failures", "pwd")
    headers = auth_headers(token)

    project_resp = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P-report-failures", "description": "desc"},
    )
    assert project_resp.status_code == 200
    project_id = project_resp.json()["id"]

    api_case_id = _create_api_case(client, headers, project_id, name="api-failure-assertion")
    web_case_id = _create_web_case(client, headers, project_id, name="web-failure-timeout")

    async def fake_execute_test(_test_case, runtime_variables=None):
        return {
            "status": "failed",
            "actual_status": 500,
            "actual_body": "{\"ok\": false}",
            "error_message": "Assertion failed: status mismatch",
            "duration_ms": 11,
            "extracted_variables": {},
        }

    async def fake_execute_web_test_case(_test_case, artifact_dir):
        return {
            "status": "failed",
            "duration_ms": 21,
            "error_message": "timeout waiting for selector",
            "step_logs": [],
            "artifacts": [f"{artifact_dir}/failure.png"],
        }

    monkeypatch.setattr("app.api.test_runs.execute_test", fake_execute_test)
    monkeypatch.setattr("app.api.web_test_runs.execute_web_test_case", fake_execute_web_test_case)

    api_run = client.post(f"/api/test-runs/test-cases/{api_case_id}/run", headers=headers)
    web_run = client.post(f"/api/web-test-runs/web-test-cases/{web_case_id}/run", headers=headers)
    assert api_run.status_code == 200
    assert web_run.status_code == 200

    all_failures = client.get(
        f"/api/reports/project/{project_id}/failures",
        headers=headers,
    )
    assert all_failures.status_code == 200
    body = all_failures.json()
    assert body["total"] == 2
    assert body["page"] == 1
    assert body["page_size"] == 20
    assert len(body["items"]) == 2

    first = body["items"][0]
    assert first["status"] in {"failed", "error"}
    assert first["failure_category"] in {"assertion_failure", "timeout"}
    assert first["detail_api_path"].startswith("/api/")
    assert first["run_id"] > 0
    assert first["case_id"] > 0

    only_timeout = client.get(
        f"/api/reports/project/{project_id}/failures?failure_category=timeout",
        headers=headers,
    )
    assert only_timeout.status_code == 200
    timeout_items = only_timeout.json()["items"]
    assert len(timeout_items) == 1
    assert timeout_items[0]["run_type"] == "web"
    assert timeout_items[0]["failure_category"] == "timeout"

    only_api = client.get(
        f"/api/reports/project/{project_id}/failures?run_type=api",
        headers=headers,
    )
    assert only_api.status_code == 200
    api_items = only_api.json()["items"]
    assert len(api_items) == 1
    assert api_items[0]["run_type"] == "api"
    assert api_items[0]["failure_category"] == "assertion_failure"

    paged = client.get(
        f"/api/reports/project/{project_id}/failures?page=1&page_size=1",
        headers=headers,
    )
    assert paged.status_code == 200
    paged_body = paged.json()
    assert paged_body["total"] == 2
    assert len(paged_body["items"]) == 1


def test_report_failures_forbidden_for_non_member(client, create_user_and_login, auth_headers):
    owner_token = create_user_and_login("owner_report_failures_forbid", "pwd")
    attacker_token = create_user_and_login("attacker_report_failures_forbid", "pwd")

    project_resp = client.post(
        "/api/projects/",
        headers=auth_headers(owner_token),
        json={"name": "P-report-failures-forbid", "description": "desc"},
    )
    assert project_resp.status_code == 200
    project_id = project_resp.json()["id"]

    resp = client.get(
        f"/api/reports/project/{project_id}/failures",
        headers=auth_headers(attacker_token),
    )
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "FORBIDDEN"
