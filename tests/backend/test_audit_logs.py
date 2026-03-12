from app.models.audit_log import AuditLog


def test_project_create_writes_audit_log(client, create_user_and_login, auth_headers, db_session):
    token = create_user_and_login("owner", "pwd")
    headers = auth_headers(token)

    create_resp = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "Project A", "description": "desc"},
    )
    assert create_resp.status_code == 200
    project_id = create_resp.json()["id"]

    audit = (
        db_session.query(AuditLog)
        .filter(AuditLog.action == "project.create", AuditLog.resource_id == str(project_id))
        .first()
    )
    assert audit is not None
    assert audit.result == "success"
    assert audit.user_id == 1
    assert audit.request_id is not None
    assert audit.path == "/api/projects/"

