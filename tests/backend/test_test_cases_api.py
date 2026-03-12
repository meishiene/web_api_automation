def test_create_test_case_normalizes_method_and_rejects_duplicate_name(
    client,
    create_user_and_login,
    auth_headers,
):
    token = create_user_and_login("owner", "pwd")
    headers = auth_headers(token)

    project_resp = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P1", "description": "desc"},
    )
    assert project_resp.status_code == 200
    project_id = project_resp.json()["id"]

    first_case = client.post(
        f"/api/test-cases/project/{project_id}",
        headers=headers,
        json={
            "name": "case-1",
            "method": "get",
            "url": "https://example.com",
            "expected_status": 200,
        },
    )
    assert first_case.status_code == 200
    assert first_case.json()["method"] == "GET"

    duplicate_case = client.post(
        f"/api/test-cases/project/{project_id}",
        headers=headers,
        json={
            "name": "case-1",
            "method": "GET",
            "url": "https://example.com",
            "expected_status": 200,
        },
    )
    assert duplicate_case.status_code == 400
    body = duplicate_case.json()
    assert body["error"]["code"] == "TEST_CASE_ALREADY_EXISTS"
    assert body["detail"] == "Test case name already exists"
