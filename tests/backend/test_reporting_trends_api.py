from app.models.test_run import TestRun as ApiTestRun
from app.models.web_test_run import WebTestRun


def _create_api_case(client, headers, project_id, name="api-trend-case"):
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


def _create_web_case(client, headers, project_id, name="web-trend-case"):
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


def test_report_trends_support_day_and_week_consistently(
    client, db_session, monkeypatch, create_user_and_login, auth_headers
):
    token = create_user_and_login("owner_report_trend", "pwd")
    headers = auth_headers(token)

    project_resp = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P-report-trend", "description": "desc"},
    )
    assert project_resp.status_code == 200
    project_id = project_resp.json()["id"]

    api_case_id = _create_api_case(client, headers, project_id)
    web_case_id = _create_web_case(client, headers, project_id)

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

    api_run_1 = client.post(f"/api/test-runs/test-cases/{api_case_id}/run", headers=headers)
    api_run_2 = client.post(f"/api/test-runs/test-cases/{api_case_id}/run", headers=headers)
    web_run = client.post(f"/api/web-test-runs/web-test-cases/{web_case_id}/run", headers=headers)
    assert api_run_1.status_code == 200
    assert api_run_2.status_code == 200
    assert web_run.status_code == 200

    # Align timestamps to fixed buckets: two days in the same week.
    run1_id = api_run_1.json()["id"]
    run2_id = api_run_2.json()["id"]
    web_run_id = web_run.json()["id"]
    day1 = 1710115200  # 2024-03-11 00:00:00 UTC (Monday)
    day2 = 1710201600  # 2024-03-12 00:00:00 UTC (Tuesday)

    run1 = db_session.query(ApiTestRun).filter(ApiTestRun.id == run1_id).first()
    run2 = db_session.query(ApiTestRun).filter(ApiTestRun.id == run2_id).first()
    run_web = db_session.query(WebTestRun).filter(WebTestRun.id == web_run_id).first()
    run1.created_at = day1
    run2.created_at = day2
    run_web.created_at = day2
    db_session.commit()

    day_resp = client.get(
        f"/api/reports/project/{project_id}/trends?granularity=day",
        headers=headers,
    )
    assert day_resp.status_code == 200
    day_body = day_resp.json()
    assert day_body["project_id"] == project_id
    assert day_body["granularity"] == "day"
    assert len(day_body["items"]) == 2
    assert day_body["items"][0]["total_count"] == 1
    assert day_body["items"][1]["total_count"] == 2

    # Same query twice should be stable.
    day_resp_2 = client.get(
        f"/api/reports/project/{project_id}/trends?granularity=day",
        headers=headers,
    )
    assert day_resp_2.status_code == 200
    assert day_resp_2.json()["items"] == day_body["items"]

    week_resp = client.get(
        f"/api/reports/project/{project_id}/trends?granularity=week",
        headers=headers,
    )
    assert week_resp.status_code == 200
    week_body = week_resp.json()
    assert week_body["granularity"] == "week"
    assert len(week_body["items"]) == 1
    assert week_body["items"][0]["total_count"] == 3
    assert week_body["items"][0]["success_count"] == 2
    assert week_body["items"][0]["failed_count"] == 1


def test_report_trends_support_time_window_boundaries(
    client, db_session, monkeypatch, create_user_and_login, auth_headers
):
    token = create_user_and_login("owner_report_trend_window", "pwd")
    headers = auth_headers(token)

    project_resp = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P-report-trend-window", "description": "desc"},
    )
    assert project_resp.status_code == 200
    project_id = project_resp.json()["id"]

    api_case_id = _create_api_case(client, headers, project_id)

    async def fake_execute_test(_test_case, runtime_variables=None):
        return {
            "status": "success",
            "actual_status": 200,
            "actual_body": "{\"ok\": true}",
            "error_message": None,
            "duration_ms": 10,
            "extracted_variables": {},
        }

    monkeypatch.setattr("app.api.test_runs.execute_test", fake_execute_test)

    api_run = client.post(f"/api/test-runs/test-cases/{api_case_id}/run", headers=headers)
    assert api_run.status_code == 200
    run_id = api_run.json()["id"]
    created_at = 1710201600  # 2024-03-12 00:00:00 UTC

    run = db_session.query(ApiTestRun).filter(ApiTestRun.id == run_id).first()
    run.created_at = created_at
    db_session.commit()

    exact_range = client.get(
        f"/api/reports/project/{project_id}/trends?granularity=day&created_from={created_at}&created_to={created_at}",
        headers=headers,
    )
    assert exact_range.status_code == 200
    assert len(exact_range.json()["items"]) == 1
    assert exact_range.json()["items"][0]["total_count"] == 1

    out_of_range = client.get(
        f"/api/reports/project/{project_id}/trends?granularity=day&created_from={created_at + 1}&created_to={created_at + 100}",
        headers=headers,
    )
    assert out_of_range.status_code == 200
    assert out_of_range.json()["items"] == []

    invalid_range = client.get(
        f"/api/reports/project/{project_id}/trends?granularity=day&created_from={created_at + 1}&created_to={created_at}",
        headers=headers,
    )
    assert invalid_range.status_code == 400
    assert invalid_range.json()["error"]["code"] == "VALIDATION_ERROR"


def test_report_trends_forbidden_for_non_member(client, create_user_and_login, auth_headers):
    owner_token = create_user_and_login("owner_report_trend_forbid", "pwd")
    attacker_token = create_user_and_login("attacker_report_trend_forbid", "pwd")

    project_resp = client.post(
        "/api/projects/",
        headers=auth_headers(owner_token),
        json={"name": "P-report-trend-forbid", "description": "desc"},
    )
    assert project_resp.status_code == 200
    project_id = project_resp.json()["id"]

    resp = client.get(
        f"/api/reports/project/{project_id}/trends?granularity=day",
        headers=auth_headers(attacker_token),
    )
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "FORBIDDEN"
