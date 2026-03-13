
def test_project_environment_and_variables_crud(client, create_user_and_login, auth_headers):
    token = create_user_and_login("owner", "pwd")
    headers = auth_headers(token)

    project_resp = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P1", "description": "desc"},
    )
    project_id = project_resp.json()["id"]

    env_resp = client.post(
        f"/api/environments/project/{project_id}",
        headers=headers,
        json={"name": "staging", "description": "staging env"},
    )
    assert env_resp.status_code == 200
    env_id = env_resp.json()["id"]

    project_var_resp = client.post(
        f"/api/environments/project/{project_id}/variables",
        headers=headers,
        json={"key": "base_url", "value": "https://project.example.com", "is_secret": False},
    )
    assert project_var_resp.status_code == 200
    assert project_var_resp.json()["key"] == "base_url"

    env_var_resp = client.post(
        f"/api/environments/{env_id}/variables",
        headers=headers,
        json={"key": "token", "value": "super-secret", "is_secret": True},
    )
    assert env_var_resp.status_code == 200
    assert env_var_resp.json()["is_secret"] is True

    list_envs = client.get(f"/api/environments/project/{project_id}", headers=headers)
    assert list_envs.status_code == 200
    assert len(list_envs.json()) == 1

    list_project_vars = client.get(f"/api/environments/project/{project_id}/variables", headers=headers)
    assert list_project_vars.status_code == 200
    assert list_project_vars.json()[0]["value"] == "https://project.example.com"

    list_env_vars = client.get(f"/api/environments/{env_id}/variables", headers=headers)
    assert list_env_vars.status_code == 200
    masked_value = list_env_vars.json()[0]["value"]
    assert masked_value == "******"


def test_non_owner_cannot_manage_foreign_environment(client, create_user_and_login, auth_headers):
    owner_token = create_user_and_login("owner", "pwd")
    attacker_token = create_user_and_login("attacker", "pwd")

    project_resp = client.post(
        "/api/projects/",
        headers=auth_headers(owner_token),
        json={"name": "P1", "description": "desc"},
    )
    project_id = project_resp.json()["id"]

    env_resp = client.post(
        f"/api/environments/project/{project_id}",
        headers=auth_headers(owner_token),
        json={"name": "staging", "description": "staging env"},
    )
    env_id = env_resp.json()["id"]

    foreign_write = client.post(
        f"/api/environments/{env_id}/variables",
        headers=auth_headers(attacker_token),
        json={"key": "k", "value": "v", "is_secret": False},
    )
    assert foreign_write.status_code == 403
    assert foreign_write.json()["error"]["code"] == "FORBIDDEN"
