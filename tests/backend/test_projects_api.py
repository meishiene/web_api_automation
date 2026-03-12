def test_project_crud_for_owner(client, create_user_and_login, auth_headers):
    token = create_user_and_login("owner", "pwd")
    headers = auth_headers(token)

    create_resp = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "Project A", "description": "desc"},
    )
    assert create_resp.status_code == 200
    project = create_resp.json()
    project_id = project["id"]
    assert project["name"] == "Project A"

    list_resp = client.get("/api/projects/", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    update_resp = client.put(
        f"/api/projects/{project_id}",
        headers=headers,
        json={"name": "Project B", "description": "desc2"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "Project B"

    delete_resp = client.delete(f"/api/projects/{project_id}", headers=headers)
    assert delete_resp.status_code == 200
    assert delete_resp.json()["message"] == "Project deleted"


def test_user_can_only_access_own_projects(client, create_user_and_login, auth_headers):
    owner_token = create_user_and_login("owner", "pwd")
    attacker_token = create_user_and_login("attacker", "pwd")

    create_resp = client.post(
        "/api/projects/",
        headers=auth_headers(owner_token),
        json={"name": "Private Project", "description": "desc"},
    )
    assert create_resp.status_code == 200
    project_id = create_resp.json()["id"]

    update_resp = client.put(
        f"/api/projects/{project_id}",
        headers=auth_headers(attacker_token),
        json={"name": "Hacked", "description": "desc"},
    )
    assert update_resp.status_code == 404
    assert update_resp.json()["detail"] == "Project not found"


def test_project_name_must_be_unique_per_owner(client, create_user_and_login, auth_headers):
    token = create_user_and_login("owner", "pwd")
    headers = auth_headers(token)

    first = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "Unique Name", "description": "desc"},
    )
    assert first.status_code == 200

    duplicate = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "Unique Name", "description": "desc"},
    )
    assert duplicate.status_code == 400
    body = duplicate.json()
    assert body["error"]["code"] == "PROJECT_ALREADY_EXISTS"
    assert body["detail"] == "Project name already exists"
