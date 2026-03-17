def _create_api_case(client, headers, project_id, name="api-report-case"):
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


def _create_web_case(client, headers, project_id, name="web-report-case"):
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


def test_report_summary_contains_aggregates_and_top_failures(client, monkeypatch, create_user_and_login, auth_headers):
    token = create_user_and_login("owner_report_summary", "pwd")
    headers = auth_headers(token)

    project_resp = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P-report-summary", "description": "desc"},
    )
    assert project_resp.status_code == 200
    project_id = project_resp.json()["id"]

    api_case_id = _create_api_case(client, headers, project_id, name="api-failing-case")
    web_case_id = _create_web_case(client, headers, project_id, name="web-failing-case")

    async def fake_execute_test(_test_case, runtime_variables=None):
        return {
            "status": "failed",
            "actual_status": 500,
            "actual_body": "{\"ok\": false}",
            "error_message": "Assertion failed: status mismatch",
            "duration_ms": 12,
            "extracted_variables": {},
        }

    async def fake_execute_web_test_case(_test_case, artifact_dir):
        return {
            "status": "error",
            "duration_ms": 33,
            "error_message": "connection reset by peer",
            "step_logs": [{"step": 0, "action": "open", "status": "error"}],
            "artifacts": [f"{artifact_dir}/failure.png"],
        }

    monkeypatch.setattr("app.api.test_runs.execute_test", fake_execute_test)
    monkeypatch.setattr("app.api.web_test_runs.execute_web_test_case", fake_execute_web_test_case)

    # same API case run twice, used to verify Top failure aggregation count
    run1 = client.post(f"/api/test-runs/test-cases/{api_case_id}/run", headers=headers)
    run2 = client.post(f"/api/test-runs/test-cases/{api_case_id}/run", headers=headers)
    web_run = client.post(f"/api/web-test-runs/web-test-cases/{web_case_id}/run", headers=headers)
    assert run1.status_code == 200
    assert run2.status_code == 200
    assert web_run.status_code == 200

    summary_resp = client.get(f"/api/reports/project/{project_id}/summary", headers=headers)
    assert summary_resp.status_code == 200
    body = summary_resp.json()

    assert body["project_id"] == project_id
    assert body["total_count"] == 3
    assert body["completed_count"] == 3
    assert body["success_count"] == 0
    assert body["failed_count"] == 2
    assert body["error_count"] == 1
    assert body["running_count"] == 0
    assert body["pass_rate"] == 0
    assert body["fail_rate"] == 1
    assert len(body["top_failures"]) == 2

    top0 = body["top_failures"][0]
    assert top0["case_id"] == api_case_id
    assert top0["run_type"] == "api"
    assert top0["failure_category"] == "assertion_failure"
    assert top0["count"] == 2

    top1 = body["top_failures"][1]
    assert top1["case_id"] == web_case_id
    assert top1["run_type"] == "web"
    assert top1["failure_category"] == "execution_error"
    assert top1["count"] == 1


def test_report_summary_forbidden_for_non_member(client, create_user_and_login, auth_headers):
    owner_token = create_user_and_login("owner_report_summary_forbid", "pwd")
    attacker_token = create_user_and_login("attacker_report_summary_forbid", "pwd")

    project_resp = client.post(
        "/api/projects/",
        headers=auth_headers(owner_token),
        json={"name": "P-report-summary-forbid", "description": "desc"},
    )
    assert project_resp.status_code == 200
    project_id = project_resp.json()["id"]

    resp = client.get(
        f"/api/reports/project/{project_id}/summary",
        headers=auth_headers(attacker_token),
    )
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "FORBIDDEN"


def test_report_summary_supports_filters_and_validation(client, monkeypatch, create_user_and_login, auth_headers):
    token = create_user_and_login("owner_report_summary_filter", "pwd")
    headers = auth_headers(token)

    project_resp = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P-report-summary-filter", "description": "desc"},
    )
    assert project_resp.status_code == 200
    project_id = project_resp.json()["id"]

    api_case_id = _create_api_case(client, headers, project_id, name="api-report-filter")
    web_case_id = _create_web_case(client, headers, project_id, name="web-report-filter")

    async def fake_execute_test(_test_case, runtime_variables=None):
        return {
            "status": "success",
            "actual_status": 200,
            "actual_body": "{\"ok\": true}",
            "error_message": None,
            "duration_ms": 10,
            "extracted_variables": {},
        }

    async def fake_execute_web_test_case(_test_case, artifact_dir):
        return {
            "status": "failed",
            "duration_ms": 20,
            "error_message": "timeout waiting for selector",
            "step_logs": [],
            "artifacts": [f"{artifact_dir}/failure.png"],
        }

    monkeypatch.setattr("app.api.test_runs.execute_test", fake_execute_test)
    monkeypatch.setattr("app.api.web_test_runs.execute_web_test_case", fake_execute_web_test_case)

    api_run_resp = client.post(f"/api/test-runs/test-cases/{api_case_id}/run", headers=headers)
    web_run_resp = client.post(f"/api/web-test-runs/web-test-cases/{web_case_id}/run", headers=headers)
    assert api_run_resp.status_code == 200
    assert web_run_resp.status_code == 200
    api_created_at = api_run_resp.json()["created_at"]
    web_created_at = web_run_resp.json()["created_at"]

    only_web = client.get(
        f"/api/reports/project/{project_id}/summary?run_type=web&top_n=1",
        headers=headers,
    )
    assert only_web.status_code == 200
    only_web_body = only_web.json()
    assert only_web_body["total_count"] == 1
    assert only_web_body["failed_count"] == 1
    assert len(only_web_body["top_failures"]) == 1
    assert only_web_body["top_failures"][0]["run_type"] == "web"

    ranged = client.get(
        f"/api/reports/project/{project_id}/summary?created_from={api_created_at}&created_to={web_created_at}",
        headers=headers,
    )
    assert ranged.status_code == 200
    assert ranged.json()["total_count"] >= 1

    invalid_range = client.get(
        f"/api/reports/project/{project_id}/summary?created_from={web_created_at + 1}&created_to={api_created_at}",
        headers=headers,
    )
    assert invalid_range.status_code == 400
    assert invalid_range.json()["error"]["code"] == "VALIDATION_ERROR"
