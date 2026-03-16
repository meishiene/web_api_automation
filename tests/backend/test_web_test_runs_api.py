def _create_web_case(client, headers, project_id):
    create_resp = client.post(
        "/api/web-test-cases",
        headers=headers,
        json={
            "project_id": project_id,
            "name": "web-case-1",
            "base_url": "https://example.com",
            "steps": [
                {"action": "open", "params": {"url": "/login"}},
                {"action": "click", "params": {"selector": "#submit"}},
            ],
        },
    )
    assert create_resp.status_code == 200
    return create_resp.json()["id"]


def test_run_web_test_case_and_query_runs(client, monkeypatch, create_user_and_login, auth_headers):
    token = create_user_and_login("owner_web_run", "pwd")
    headers = auth_headers(token)

    project_resp = client.post("/api/projects/", headers=headers, json={"name": "P-web-run", "description": "desc"})
    assert project_resp.status_code == 200
    project_id = project_resp.json()["id"]

    case_id = _create_web_case(client, headers, project_id)

    async def fake_execute_web_test_case(_test_case, artifact_dir):
        assert artifact_dir
        return {
            "status": "success",
            "duration_ms": 88,
            "error_message": None,
            "step_logs": [{"step": 0, "action": "open", "status": "success"}],
            "artifacts": [f"{artifact_dir}/final.png"],
        }

    monkeypatch.setattr("app.api.web_test_runs.execute_web_test_case", fake_execute_web_test_case)

    run_resp = client.post(f"/api/web-test-runs/web-test-cases/{case_id}/run", headers=headers)
    assert run_resp.status_code == 200
    run_body = run_resp.json()
    assert run_body["status"] == "success"
    assert run_body["duration_ms"] == 88
    assert len(run_body["artifacts"]) == 1

    list_resp = client.get(f"/api/web-test-runs/project/{project_id}", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    detail_resp = client.get(f"/api/web-test-runs/{run_body['id']}", headers=headers)
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert detail["id"] == run_body["id"]
    assert detail["web_test_case_id"] == case_id
    assert detail["web_test_case_name"] == "web-case-1"
    assert detail["step_logs"][0]["action"] == "open"


def test_non_owner_cannot_run_foreign_web_test_case(client, monkeypatch, create_user_and_login, auth_headers):
    owner_token = create_user_and_login("owner_web_run_forbid", "pwd")
    attacker_token = create_user_and_login("attacker_web_run_forbid", "pwd")

    project_resp = client.post(
        "/api/projects/",
        headers=auth_headers(owner_token),
        json={"name": "P-web-run-forbid", "description": "desc"},
    )
    project_id = project_resp.json()["id"]
    case_id = _create_web_case(client, auth_headers(owner_token), project_id)

    async def fake_execute_web_test_case(_test_case, artifact_dir):
        return {
            "status": "success",
            "duration_ms": 10,
            "error_message": None,
            "step_logs": [],
            "artifacts": [f"{artifact_dir}/ok.png"],
        }

    monkeypatch.setattr("app.api.web_test_runs.execute_web_test_case", fake_execute_web_test_case)

    run_resp = client.post(
        f"/api/web-test-runs/web-test-cases/{case_id}/run",
        headers=auth_headers(attacker_token),
    )
    assert run_resp.status_code == 403
    assert run_resp.json()["error"]["code"] == "FORBIDDEN"


def test_web_run_persists_error_result_when_executor_fails(client, monkeypatch, create_user_and_login, auth_headers):
    token = create_user_and_login("owner_web_run_error", "pwd")
    headers = auth_headers(token)

    project_resp = client.post("/api/projects/", headers=headers, json={"name": "P-web-run-error", "description": "desc"})
    project_id = project_resp.json()["id"]
    case_id = _create_web_case(client, headers, project_id)

    async def fake_execute_web_test_case(_test_case, artifact_dir):
        return {
            "status": "error",
            "duration_ms": 21,
            "error_message": "browser launch failed",
            "step_logs": [{"step": 0, "action": "open", "status": "error"}],
            "artifacts": [f"{artifact_dir}/failure.png"],
        }

    monkeypatch.setattr("app.api.web_test_runs.execute_web_test_case", fake_execute_web_test_case)

    run_resp = client.post(f"/api/web-test-runs/web-test-cases/{case_id}/run", headers=headers)
    assert run_resp.status_code == 200
    body = run_resp.json()
    assert body["status"] == "error"
    assert body["error_message"] == "browser launch failed"
    assert body["artifacts"][0].endswith("failure.png")

