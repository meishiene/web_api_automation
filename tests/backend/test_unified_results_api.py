def _create_api_case(client, headers, project_id):
    resp = client.post(
        f"/api/test-cases/project/{project_id}",
        headers=headers,
        json={
            "name": "api-case-unified",
            "method": "GET",
            "url": "https://example.com/api",
            "expected_status": 200,
        },
    )
    assert resp.status_code == 200
    return resp.json()["id"]


def _create_web_case(client, headers, project_id):
    resp = client.post(
        "/api/web-test-cases",
        headers=headers,
        json={
            "project_id": project_id,
            "name": "web-case-unified",
            "base_url": "https://example.com",
            "steps": [
                {"action": "open", "params": {"url": "/login"}},
            ],
        },
    )
    assert resp.status_code == 200
    return resp.json()["id"]


def test_unified_results_contains_api_and_web_runs(client, monkeypatch, create_user_and_login, auth_headers):
    token = create_user_and_login("owner_unified", "pwd")
    headers = auth_headers(token)

    project_resp = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P-unified", "description": "desc"},
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
            "duration_ms": 11,
            "extracted_variables": {},
        }

    async def fake_execute_web_test_case(_test_case, artifact_dir):
        return {
            "status": "failed",
            "duration_ms": 33,
            "error_message": "assert failed",
            "step_logs": [{"step": 0, "action": "open", "status": "success"}],
            "artifacts": [f"{artifact_dir}/failure.png"],
        }

    monkeypatch.setattr("app.api.test_runs.execute_test", fake_execute_test)
    monkeypatch.setattr("app.api.web_test_runs.execute_web_test_case", fake_execute_web_test_case)

    api_run_resp = client.post(f"/api/test-runs/test-cases/{api_case_id}/run", headers=headers)
    assert api_run_resp.status_code == 200
    web_run_resp = client.post(f"/api/web-test-runs/web-test-cases/{web_case_id}/run", headers=headers)
    assert web_run_resp.status_code == 200

    unified_resp = client.get(f"/api/test-runs/project/{project_id}/unified-results", headers=headers)
    assert unified_resp.status_code == 200
    body = unified_resp.json()
    assert body["total"] == 2
    assert body["page"] == 1
    assert body["page_size"] == 20
    unified = body["items"]
    assert len(unified) == 2

    api_item = next(item for item in unified if item["run_type"] == "api")
    web_item = next(item for item in unified if item["run_type"] == "web")

    assert api_item["project_id"] == project_id
    assert api_item["case_id"] == api_case_id
    assert api_item["case_name"] == "api-case-unified"
    assert api_item["status"] == "success"
    assert api_item["detail_api_path"] == f"/api/test-runs/{api_item['run_id']}"
    assert api_item["artifact_dir"] is None
    assert api_item["artifacts"] is None

    assert web_item["project_id"] == project_id
    assert web_item["case_id"] == web_case_id
    assert web_item["case_name"] == "web-case-unified"
    assert web_item["status"] == "failed"
    assert web_item["detail_api_path"] == f"/api/web-test-runs/{web_item['run_id']}"
    assert web_item["artifact_dir"].endswith(str(web_item["run_id"]))
    assert web_item["artifacts"][0].endswith("failure.png")
    assert web_item["started_at"] is not None
    assert web_item["finished_at"] is not None


def test_unified_results_forbidden_for_non_member(client, create_user_and_login, auth_headers):
    owner_token = create_user_and_login("owner_unified_forbid", "pwd")
    attacker_token = create_user_and_login("attacker_unified_forbid", "pwd")

    project_resp = client.post(
        "/api/projects/",
        headers=auth_headers(owner_token),
        json={"name": "P-unified-forbid", "description": "desc"},
    )
    assert project_resp.status_code == 200
    project_id = project_resp.json()["id"]

    resp = client.get(
        f"/api/test-runs/project/{project_id}/unified-results",
        headers=auth_headers(attacker_token),
    )
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "FORBIDDEN"


def test_unified_results_support_filters_and_pagination(client, monkeypatch, create_user_and_login, auth_headers):
    token = create_user_and_login("owner_unified_filter", "pwd")
    headers = auth_headers(token)

    project_resp = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P-unified-filter", "description": "desc"},
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
            "error_message": "assert failed",
            "step_logs": [],
            "artifacts": [f"{artifact_dir}/failure.png"],
        }

    monkeypatch.setattr("app.api.test_runs.execute_test", fake_execute_test)
    monkeypatch.setattr("app.api.web_test_runs.execute_web_test_case", fake_execute_web_test_case)

    api_run_resp = client.post(f"/api/test-runs/test-cases/{api_case_id}/run", headers=headers)
    assert api_run_resp.status_code == 200
    api_created_at = api_run_resp.json()["created_at"]
    web_run_resp = client.post(f"/api/web-test-runs/web-test-cases/{web_case_id}/run", headers=headers)
    assert web_run_resp.status_code == 200
    web_created_at = web_run_resp.json()["created_at"]

    only_web = client.get(
        f"/api/test-runs/project/{project_id}/unified-results?run_type=web",
        headers=headers,
    )
    assert only_web.status_code == 200
    only_web_items = only_web.json()["items"]
    assert len(only_web_items) == 1
    assert only_web_items[0]["run_type"] == "web"

    only_failed = client.get(
        f"/api/test-runs/project/{project_id}/unified-results?status=failed",
        headers=headers,
    )
    assert only_failed.status_code == 200
    only_failed_items = only_failed.json()["items"]
    assert len(only_failed_items) == 1
    assert only_failed_items[0]["status"] == "failed"
    assert only_failed_items[0]["run_type"] == "web"

    paged = client.get(
        f"/api/test-runs/project/{project_id}/unified-results?page=1&page_size=1",
        headers=headers,
    )
    assert paged.status_code == 200
    paged_body = paged.json()
    assert paged_body["total"] == 2
    assert len(paged_body["items"]) == 1

    ranged = client.get(
        f"/api/test-runs/project/{project_id}/unified-results?created_from={api_created_at}&created_to={web_created_at}",
        headers=headers,
    )
    assert ranged.status_code == 200
    ranged_body = ranged.json()
    assert ranged_body["total"] >= 1
    assert all(api_created_at <= item["created_at"] <= web_created_at for item in ranged_body["items"])

    invalid_range = client.get(
        f"/api/test-runs/project/{project_id}/unified-results?created_from={web_created_at + 1}&created_to={api_created_at}",
        headers=headers,
    )
    assert invalid_range.status_code == 400
    assert invalid_range.json()["error"]["code"] == "VALIDATION_ERROR"
