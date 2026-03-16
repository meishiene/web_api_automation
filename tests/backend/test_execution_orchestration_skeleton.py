from app.models.execution_job import ExecutionJob
from app.models.execution_task import ExecutionTask


def _create_web_case(client, headers, project_id):
    create_resp = client.post(
        "/api/web-test-cases",
        headers=headers,
        json={
            "project_id": project_id,
            "name": "web-case-orchestration",
            "base_url": "https://example.com",
            "steps": [{"action": "open", "params": {"url": "/login"}}],
        },
    )
    assert create_resp.status_code == 200
    return create_resp.json()["id"]


def test_api_run_creates_execution_task_and_job(client, monkeypatch, create_user_and_login, auth_headers, db_session):
    token = create_user_and_login("owner_exec_api", "pwd")
    headers = auth_headers(token)

    project_resp = client.post("/api/projects/", headers=headers, json={"name": "P-exec-api", "description": "desc"})
    project_id = project_resp.json()["id"]

    case_resp = client.post(
        f"/api/test-cases/project/{project_id}",
        headers=headers,
        json={
            "name": "api-case-orchestration",
            "method": "GET",
            "url": "https://example.com/api",
            "expected_status": 200,
        },
    )
    case_id = case_resp.json()["id"]

    async def fake_execute_test(_test_case, runtime_variables=None):
        return {
            "status": "success",
            "actual_status": 200,
            "actual_body": "{\"ok\": true}",
            "error_message": None,
            "duration_ms": 9,
            "extracted_variables": {},
        }

    monkeypatch.setattr("app.api.test_runs.execute_test", fake_execute_test)

    run_resp = client.post(f"/api/test-runs/test-cases/{case_id}/run", headers=headers)
    assert run_resp.status_code == 200

    task = db_session.query(ExecutionTask).filter(ExecutionTask.project_id == project_id).one()
    assert task.run_type == "api"
    assert task.target_type == "test_case"
    assert task.target_id == case_id
    assert task.status == "success"
    assert task.error_code is None

    job = db_session.query(ExecutionJob).filter(ExecutionJob.task_id == task.id).one()
    assert job.executor_type == "api"
    assert job.status == "success"
    assert job.error_code is None


def test_web_run_creates_execution_task_and_job_with_error_code(
    client, monkeypatch, create_user_and_login, auth_headers, db_session
):
    token = create_user_and_login("owner_exec_web", "pwd")
    headers = auth_headers(token)

    project_resp = client.post("/api/projects/", headers=headers, json={"name": "P-exec-web", "description": "desc"})
    project_id = project_resp.json()["id"]
    case_id = _create_web_case(client, headers, project_id)

    async def fake_execute_web_test_case(_test_case, artifact_dir):
        return {
            "status": "failed",
            "duration_ms": 13,
            "error_message": "assert failed",
            "step_logs": [],
            "artifacts": [f"{artifact_dir}/failure.png"],
        }

    monkeypatch.setattr("app.api.web_test_runs.execute_web_test_case", fake_execute_web_test_case)

    run_resp = client.post(f"/api/web-test-runs/web-test-cases/{case_id}/run", headers=headers)
    assert run_resp.status_code == 200

    task = db_session.query(ExecutionTask).filter(ExecutionTask.project_id == project_id).one()
    assert task.run_type == "web"
    assert task.target_type == "test_case"
    assert task.target_id == case_id
    assert task.status == "failed"
    assert task.error_code == "ASSERTION_FAILED"

    job = db_session.query(ExecutionJob).filter(ExecutionJob.task_id == task.id).one()
    assert job.executor_type == "web"
    assert job.status == "failed"
    assert job.error_code == "ASSERTION_FAILED"
