from app.models.user import User


def test_owner_can_crud_suite_and_manage_cases(client, create_user_and_login, auth_headers):
    token = create_user_and_login("owner", "pwd")
    headers = auth_headers(token)

    project_resp = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P1", "description": "desc"},
    )
    assert project_resp.status_code == 200
    project_id = project_resp.json()["id"]

    case1_resp = client.post(
        f"/api/test-cases/project/{project_id}",
        headers=headers,
        json={
            "name": "Case 1",
            "method": "GET",
            "url": "https://example.com/1",
            "expected_status": 200,
        },
    )
    assert case1_resp.status_code == 200
    case1_id = case1_resp.json()["id"]

    case2_resp = client.post(
        f"/api/test-cases/project/{project_id}",
        headers=headers,
        json={
            "name": "Case 2",
            "method": "GET",
            "url": "https://example.com/2",
            "expected_status": 200,
        },
    )
    assert case2_resp.status_code == 200
    case2_id = case2_resp.json()["id"]

    suite_resp = client.post(
        f"/api/test-suites/project/{project_id}",
        headers=headers,
        json={"name": "Smoke", "description": "smoke suite"},
    )
    assert suite_resp.status_code == 200
    suite_id = suite_resp.json()["id"]

    add_case1 = client.post(f"/api/test-suites/{suite_id}/cases/{case1_id}", headers=headers, json={"order_index": 2})
    add_case2 = client.post(f"/api/test-suites/{suite_id}/cases/{case2_id}", headers=headers, json={"order_index": 1})
    assert add_case1.status_code == 200
    assert add_case2.status_code == 200

    list_suites = client.get(f"/api/test-suites/project/{project_id}", headers=headers)
    assert list_suites.status_code == 200
    suites = list_suites.json()
    assert len(suites) == 1
    assert suites[0]["name"] == "Smoke"
    assert suites[0]["case_count"] == 2

    list_cases = client.get(f"/api/test-suites/{suite_id}/cases", headers=headers)
    assert list_cases.status_code == 200
    ordered_case_ids = [item["test_case_id"] for item in list_cases.json()]
    assert ordered_case_ids == [case2_id, case1_id]

    update_resp = client.put(
        f"/api/test-suites/{suite_id}",
        headers=headers,
        json={"name": "Smoke Updated", "description": "updated"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "Smoke Updated"

    del_case_resp = client.delete(f"/api/test-suites/{suite_id}/cases/{case1_id}", headers=headers)
    assert del_case_resp.status_code == 200

    delete_suite = client.delete(f"/api/test-suites/{suite_id}", headers=headers)
    assert delete_suite.status_code == 200
    assert delete_suite.json()["message"] == "Test suite deleted"


def test_non_owner_cannot_manage_foreign_suite(client, create_user_and_login, auth_headers):
    owner_token = create_user_and_login("owner", "pwd")
    attacker_token = create_user_and_login("attacker", "pwd")

    project_resp = client.post(
        "/api/projects/",
        headers=auth_headers(owner_token),
        json={"name": "P1", "description": "desc"},
    )
    project_id = project_resp.json()["id"]

    suite_resp = client.post(
        f"/api/test-suites/project/{project_id}",
        headers=auth_headers(owner_token),
        json={"name": "Smoke", "description": "smoke suite"},
    )
    suite_id = suite_resp.json()["id"]

    foreign_update = client.put(
        f"/api/test-suites/{suite_id}",
        headers=auth_headers(attacker_token),
        json={"name": "hacked", "description": "x"},
    )
    assert foreign_update.status_code == 403
    assert foreign_update.json()["error"]["code"] == "FORBIDDEN"


def test_admin_can_manage_foreign_suite(client, create_user_and_login, auth_headers, db_session):
    owner_token = create_user_and_login("owner", "pwd")
    admin_token = create_user_and_login("admin", "pwd")
    admin = db_session.query(User).filter(User.username == "admin").first()
    admin.role = "admin"
    db_session.commit()

    project_resp = client.post(
        "/api/projects/",
        headers=auth_headers(owner_token),
        json={"name": "P1", "description": "desc"},
    )
    project_id = project_resp.json()["id"]

    suite_resp = client.post(
        f"/api/test-suites/project/{project_id}",
        headers=auth_headers(owner_token),
        json={"name": "Smoke", "description": "smoke suite"},
    )
    suite_id = suite_resp.json()["id"]

    admin_update = client.put(
        f"/api/test-suites/{suite_id}",
        headers=auth_headers(admin_token),
        json={"name": "admin-updated", "description": "ok"},
    )
    assert admin_update.status_code == 200
    assert admin_update.json()["name"] == "admin-updated"
