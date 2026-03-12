from app.models.user import User


def test_owner_can_create_organization_and_manage_members(client, create_user_and_login, auth_headers):
    owner_token = create_user_and_login("owner", "pwd")
    create_user_and_login("member", "pwd")

    create_org_resp = client.post(
        "/api/organizations/",
        headers=auth_headers(owner_token),
        json={"name": "Org-A"},
    )
    assert create_org_resp.status_code == 200
    org_id = create_org_resp.json()["id"]

    add_member_resp = client.post(
        f"/api/organizations/{org_id}/members",
        headers=auth_headers(owner_token),
        json={"user_id": 2, "role": "admin"},
    )
    assert add_member_resp.status_code == 200
    assert add_member_resp.json()["role"] == "admin"

    list_members_resp = client.get(
        f"/api/organizations/{org_id}/members",
        headers=auth_headers(owner_token),
    )
    assert list_members_resp.status_code == 200
    assert any(item["user_id"] == 2 for item in list_members_resp.json())


def test_org_admin_can_apply_cross_project_member_governance(
    client,
    create_user_and_login,
    auth_headers,
):
    owner_token = create_user_and_login("owner", "pwd")
    admin_token = create_user_and_login("org-admin", "pwd")
    target_token = create_user_and_login("target", "pwd")
    assert target_token

    org_resp = client.post(
        "/api/organizations/",
        headers=auth_headers(owner_token),
        json={"name": "Org-A"},
    )
    org_id = org_resp.json()["id"]

    client.post(
        f"/api/organizations/{org_id}/members",
        headers=auth_headers(owner_token),
        json={"user_id": 2, "role": "admin"},
    )

    p1 = client.post(
        "/api/projects/",
        headers=auth_headers(owner_token),
        json={"name": "P1", "description": "d"},
    ).json()["id"]
    p2 = client.post(
        "/api/projects/",
        headers=auth_headers(owner_token),
        json={"name": "P2", "description": "d"},
    ).json()["id"]

    attach1 = client.post(
        f"/api/organizations/{org_id}/projects/attach",
        headers=auth_headers(owner_token),
        json={"project_id": p1},
    )
    attach2 = client.post(
        f"/api/organizations/{org_id}/projects/attach",
        headers=auth_headers(owner_token),
        json={"project_id": p2},
    )
    assert attach1.status_code == 200
    assert attach2.status_code == 200

    governance_resp = client.post(
        f"/api/organizations/{org_id}/members/governance/cross-project",
        headers=auth_headers(admin_token),
        json={"user_id": 3, "project_role": "editor"},
    )
    assert governance_resp.status_code == 200
    assert governance_resp.json()["affected_projects"] == 2

    target_projects_resp = client.get("/api/projects/", headers=auth_headers(target_token))
    assert target_projects_resp.status_code == 200
    project_ids = {item["id"] for item in target_projects_resp.json()}
    assert p1 in project_ids
    assert p2 in project_ids


def test_non_org_admin_cannot_apply_cross_project_governance(client, create_user_and_login, auth_headers):
    owner_token = create_user_and_login("owner", "pwd")
    normal_token = create_user_and_login("normal", "pwd")
    create_user_and_login("target", "pwd")

    org_resp = client.post(
        "/api/organizations/",
        headers=auth_headers(owner_token),
        json={"name": "Org-A"},
    )
    org_id = org_resp.json()["id"]

    forbidden_resp = client.post(
        f"/api/organizations/{org_id}/members/governance/cross-project",
        headers=auth_headers(normal_token),
        json={"user_id": 3, "project_role": "viewer"},
    )
    assert forbidden_resp.status_code == 403
    assert forbidden_resp.json()["error"]["code"] == "FORBIDDEN"


def test_platform_admin_can_manage_any_organization(client, create_user_and_login, auth_headers, db_session):
    owner_token = create_user_and_login("owner", "pwd")
    platform_admin_token = create_user_and_login("platform-admin", "pwd")
    create_user_and_login("member", "pwd")

    platform_admin = db_session.query(User).filter(User.username == "platform-admin").first()
    platform_admin.role = "admin"
    db_session.commit()

    org_resp = client.post(
        "/api/organizations/",
        headers=auth_headers(owner_token),
        json={"name": "Org-A"},
    )
    org_id = org_resp.json()["id"]

    add_member_resp = client.post(
        f"/api/organizations/{org_id}/members",
        headers=auth_headers(platform_admin_token),
        json={"user_id": 3, "role": "member"},
    )
    assert add_member_resp.status_code == 200
