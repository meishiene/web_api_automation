from app.models.audit_log import AuditLog


def _create_api_case(client, headers, project_id, name="api-audit-case"):
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


def _create_web_case(client, headers, project_id, name="web-audit-case"):
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


def test_report_endpoints_write_audit_logs(client, db_session, monkeypatch, create_user_and_login, auth_headers):
    token = create_user_and_login("owner_report_audit", "pwd")
    headers = auth_headers(token)

    project_resp = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P-report-audit", "description": "desc"},
    )
    assert project_resp.status_code == 200
    project_id = project_resp.json()["id"]

    api_case_id = _create_api_case(client, headers, project_id)
    web_case_id = _create_web_case(client, headers, project_id)

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

    assert client.post(f"/api/test-runs/test-cases/{api_case_id}/run", headers=headers).status_code == 200
    assert client.post(f"/api/web-test-runs/web-test-cases/{web_case_id}/run", headers=headers).status_code == 200

    assert client.get(f"/api/reports/project/{project_id}/summary", headers=headers).status_code == 200
    assert client.get(f"/api/reports/project/{project_id}/trends?granularity=day", headers=headers).status_code == 200
    assert client.get(f"/api/reports/project/{project_id}/failures", headers=headers).status_code == 200

    summary_audit = (
        db_session.query(AuditLog)
        .filter(AuditLog.action == "report.summary.read", AuditLog.resource_id == str(project_id))
        .first()
    )
    trends_audit = (
        db_session.query(AuditLog)
        .filter(AuditLog.action == "report.trends.read", AuditLog.resource_id == str(project_id))
        .first()
    )
    failures_audit = (
        db_session.query(AuditLog)
        .filter(AuditLog.action == "report.failures.read", AuditLog.resource_id == str(project_id))
        .first()
    )

    assert summary_audit is not None
    assert trends_audit is not None
    assert failures_audit is not None
    assert summary_audit.result == "success"
    assert trends_audit.result == "success"
    assert failures_audit.result == "success"
    assert summary_audit.path == f"/api/reports/project/{project_id}/summary"
    assert trends_audit.path == f"/api/reports/project/{project_id}/trends"
    assert failures_audit.path == f"/api/reports/project/{project_id}/failures"
