import time

from app.models.test_run import TestRun as ApiTestRun
from app.models.web_test_run import WebTestRun


def _create_api_case(client, headers, project_id, name="api-perf-case"):
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


def _create_web_case(client, headers, project_id, name="web-perf-case"):
    resp = client.post(
        "/api/web-test-cases",
        headers=headers,
        json={
            "project_id": project_id,
            "name": name,
            "base_url": "https://example.com",
            "steps": [{"action": "open", "params": {"url": "/"}}],
        },
    )
    assert resp.status_code == 200
    return resp.json()["id"]


def test_report_endpoints_reject_too_wide_time_window(client, create_user_and_login, auth_headers):
    token = create_user_and_login("owner_report_window_guard", "pwd")
    headers = auth_headers(token)
    project_resp = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P-report-window-guard", "description": "desc"},
    )
    assert project_resp.status_code == 200
    project_id = project_resp.json()["id"]

    # Over 180 days window
    created_from = 1
    created_to = 1 + 181 * 24 * 3600

    summary_resp = client.get(
        f"/api/reports/project/{project_id}/summary?created_from={created_from}&created_to={created_to}",
        headers=headers,
    )
    trends_resp = client.get(
        f"/api/reports/project/{project_id}/trends?granularity=day&created_from={created_from}&created_to={created_to}",
        headers=headers,
    )
    failures_resp = client.get(
        f"/api/reports/project/{project_id}/failures?created_from={created_from}&created_to={created_to}",
        headers=headers,
    )

    assert summary_resp.status_code == 400
    assert trends_resp.status_code == 400
    assert failures_resp.status_code == 400
    assert summary_resp.json()["error"]["code"] == "VALIDATION_ERROR"
    assert trends_resp.json()["error"]["code"] == "VALIDATION_ERROR"
    assert failures_resp.json()["error"]["code"] == "VALIDATION_ERROR"


def test_report_endpoints_performance_baseline_on_mid_sized_dataset(
    client, db_session, create_user_and_login, auth_headers
):
    token = create_user_and_login("owner_report_perf_baseline", "pwd")
    headers = auth_headers(token)

    project_resp = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P-report-perf-baseline", "description": "desc"},
    )
    assert project_resp.status_code == 200
    project_id = project_resp.json()["id"]

    api_case_id = _create_api_case(client, headers, project_id)
    web_case_id = _create_web_case(client, headers, project_id)

    base_ts = 1711000000

    api_runs = []
    for i in range(300):
        status = "success" if i % 4 else "failed"
        api_runs.append(
            ApiTestRun(
                test_case_id=api_case_id,
                status=status,
                actual_status=200 if status == "success" else 500,
                actual_body="{\"ok\": true}" if status == "success" else "{\"ok\": false}",
                error_message=None if status == "success" else "Assertion failed",
                duration_ms=10 + (i % 7),
                created_at=base_ts + i * 60,
            )
        )
    db_session.add_all(api_runs)

    web_runs = []
    for i in range(300):
        status = "failed" if i % 3 == 0 else "success"
        web_runs.append(
            WebTestRun(
                project_id=project_id,
                web_test_case_id=web_case_id,
                triggered_by=1,
                status=status,
                error_message="timeout waiting for selector" if status == "failed" else None,
                duration_ms=15 + (i % 9),
                artifact_dir=f"artifacts/web-test-runs/{i}",
                artifacts_json="[]",
                step_logs_json="[]",
                started_at=base_ts + i * 60,
                finished_at=base_ts + i * 60 + 10,
                created_at=base_ts + i * 60,
            )
        )
    db_session.add_all(web_runs)
    db_session.commit()

    created_from = base_ts
    created_to = base_ts + 300 * 60

    start_summary = time.perf_counter()
    summary_resp = client.get(
        f"/api/reports/project/{project_id}/summary?created_from={created_from}&created_to={created_to}",
        headers=headers,
    )
    summary_elapsed = time.perf_counter() - start_summary

    start_trends = time.perf_counter()
    trends_resp = client.get(
        f"/api/reports/project/{project_id}/trends?granularity=day&created_from={created_from}&created_to={created_to}",
        headers=headers,
    )
    trends_elapsed = time.perf_counter() - start_trends

    start_failures = time.perf_counter()
    failures_resp = client.get(
        f"/api/reports/project/{project_id}/failures?created_from={created_from}&created_to={created_to}&page=1&page_size=20",
        headers=headers,
    )
    failures_elapsed = time.perf_counter() - start_failures

    assert summary_resp.status_code == 200
    assert trends_resp.status_code == 200
    assert failures_resp.status_code == 200
    # S5-06 baseline: mid-sized dataset should complete quickly in local test env.
    assert summary_elapsed < 3.0
    assert trends_elapsed < 3.0
    assert failures_elapsed < 3.0
