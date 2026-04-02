def test_web_test_case_crud_for_owner(client, create_user_and_login, auth_headers):
    token = create_user_and_login("owner_web", "pwd")
    headers = auth_headers(token)

    project_resp = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P-web", "description": "desc"},
    )
    assert project_resp.status_code == 200
    project_id = project_resp.json()["id"]

    create_resp = client.post(
        "/api/web-test-cases",
        headers=headers,
        json={
            "project_id": project_id,
            "name": "login-smoke",
            "description": "basic login flow",
            "base_url": "https://example.com",
            "browser_name": "firefox",
            "viewport_width": 1366,
            "viewport_height": 768,
            "timeout_ms": 45000,
            "headless": False,
            "capture_on_failure": True,
            "record_video": True,
            "steps": [
                {"action": "open", "params": {"url": "/login"}},
                {"action": "click", "params": {"selector": "#submit"}},
            ],
        },
    )
    assert create_resp.status_code == 200
    created = create_resp.json()
    assert created["project_id"] == project_id
    assert created["name"] == "login-smoke"
    assert created["browser_name"] == "firefox"
    assert created["viewport_width"] == 1366
    assert created["viewport_height"] == 768
    assert created["timeout_ms"] == 45000
    assert created["headless"] is False
    assert created["capture_on_failure"] is True
    assert created["record_video"] is True
    assert len(created["steps"]) == 2
    assert created["steps"][0]["order_index"] == 0
    assert created["steps"][1]["order_index"] == 1

    case_id = created["id"]

    list_resp = client.get(f"/api/web-test-cases/project/{project_id}", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    detail_resp = client.get(f"/api/web-test-cases/{case_id}", headers=headers)
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert detail["id"] == case_id
    assert detail["name"] == "login-smoke"
    assert len(detail["steps"]) == 2

    update_resp = client.put(
        f"/api/web-test-cases/{case_id}",
        headers=headers,
        json={
            "name": "login-smoke-updated",
            "description": "updated",
            "base_url": "https://example.com",
            "browser_name": "webkit",
            "viewport_width": 375,
            "viewport_height": 667,
            "timeout_ms": 15000,
            "headless": True,
            "capture_on_failure": False,
            "record_video": False,
            "steps": [
                {"action": "open", "params": {"url": "/login"}},
                {"action": "input", "params": {"selector": "#username", "value": "demo"}},
                {"action": "click", "params": {"selector": "#submit"}},
            ],
        },
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["name"] == "login-smoke-updated"
    assert updated["browser_name"] == "webkit"
    assert updated["viewport_width"] == 375
    assert updated["viewport_height"] == 667
    assert updated["timeout_ms"] == 15000
    assert updated["headless"] is True
    assert updated["capture_on_failure"] is False
    assert updated["record_video"] is False
    assert len(updated["steps"]) == 3
    assert updated["steps"][2]["order_index"] == 2

    delete_resp = client.delete(f"/api/web-test-cases/{case_id}", headers=headers)
    assert delete_resp.status_code == 200
    assert delete_resp.json()["message"] == "Web test case deleted"


def test_web_test_case_duplicate_name_rejected(client, create_user_and_login, auth_headers):
    token = create_user_and_login("owner_web_dup", "pwd")
    headers = auth_headers(token)

    project_resp = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P-web-dup", "description": "desc"},
    )
    project_id = project_resp.json()["id"]

    first = client.post(
        "/api/web-test-cases",
        headers=headers,
        json={"project_id": project_id, "name": "dup", "steps": [{"action": "open", "params": {"url": "/"}}]},
    )
    assert first.status_code == 200

    duplicate = client.post(
        "/api/web-test-cases",
        headers=headers,
        json={"project_id": project_id, "name": "dup", "steps": [{"action": "open", "params": {"url": "/"}}]},
    )
    assert duplicate.status_code == 400
    body = duplicate.json()
    assert body["error"]["code"] == "WEB_TEST_CASE_ALREADY_EXISTS"


def test_non_owner_cannot_create_web_test_case_on_foreign_project(client, create_user_and_login, auth_headers):
    owner_token = create_user_and_login("owner_web_foreign", "pwd")
    attacker_token = create_user_and_login("attacker_web_foreign", "pwd")

    project_resp = client.post(
        "/api/projects/",
        headers=auth_headers(owner_token),
        json={"name": "P-foreign-web", "description": "desc"},
    )
    project_id = project_resp.json()["id"]

    create_resp = client.post(
        "/api/web-test-cases",
        headers=auth_headers(attacker_token),
        json={"project_id": project_id, "name": "steal", "steps": [{"action": "open", "params": {"url": "/"}}]},
    )
    assert create_resp.status_code == 403
    assert create_resp.json()["error"]["code"] == "FORBIDDEN"
