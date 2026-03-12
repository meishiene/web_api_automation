import time

from app.models.audit_log import AuditLog
from app.models.audit_log_archive import AuditLogArchive
from app.models.user import User
from app.services.audit_service import run_audit_retention


def test_query_audit_logs_only_returns_current_user_records(client, create_user_and_login, auth_headers, db_session):
    owner_token = create_user_and_login("owner", "pwd")
    other_token = create_user_and_login("other", "pwd")

    owner_headers = auth_headers(owner_token)
    other_headers = auth_headers(other_token)

    create_owner_project = client.post(
        "/api/projects/",
        headers=owner_headers,
        json={"name": "Owner Project", "description": "desc"},
    )
    assert create_owner_project.status_code == 200

    create_other_project = client.post(
        "/api/projects/",
        headers=other_headers,
        json={"name": "Other Project", "description": "desc"},
    )
    assert create_other_project.status_code == 200

    response = client.get("/api/audit-logs/?page=1&page_size=50", headers=owner_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert all(item["user_id"] == 1 for item in body["items"])

    # Ensure other user's action exists in DB but is not exposed to owner.
    other_count = db_session.query(AuditLog).filter(AuditLog.user_id == 2).count()
    assert other_count >= 1
    assert all(item["user_id"] != 2 for item in body["items"])


def test_query_audit_logs_can_include_archived_records(client, create_user_and_login, auth_headers, db_session):
    owner_token = create_user_and_login("owner", "pwd")
    headers = auth_headers(owner_token)

    archived = AuditLogArchive(
        original_id=99999,
        user_id=1,
        action="project.create",
        resource_type="project",
        resource_id="123",
        result="success",
        request_id="archived-request",
        client_ip="127.0.0.1",
        method="POST",
        path="/api/projects/",
        details='{"source":"archive"}',
        created_at=int(time.time()) - 86400,
        archived_at=int(time.time()),
    )
    db_session.add(archived)
    db_session.commit()

    without_archived = client.get("/api/audit-logs/?include_archived=false", headers=headers)
    assert without_archived.status_code == 200
    assert all(item["archived"] is False for item in without_archived.json()["items"])

    with_archived = client.get("/api/audit-logs/?include_archived=true&page_size=100", headers=headers)
    assert with_archived.status_code == 200
    items = with_archived.json()["items"]
    assert any(item["archived"] is True for item in items)
    assert any(item["request_id"] == "archived-request" for item in items)


def test_run_audit_retention_archives_and_purges(db_session):
    now = int(time.time())

    old_active = AuditLog(
        user_id=1,
        action="project.create",
        resource_type="project",
        resource_id="1",
        result="success",
        request_id="r1",
        client_ip="127.0.0.1",
        method="POST",
        path="/api/projects/",
        details=None,
        created_at=now - 40 * 24 * 3600,
    )
    db_session.add(old_active)

    old_archive = AuditLogArchive(
        original_id=12345,
        user_id=1,
        action="project.delete",
        resource_type="project",
        resource_id="2",
        result="success",
        request_id="r2",
        client_ip="127.0.0.1",
        method="DELETE",
        path="/api/projects/2",
        details=None,
        created_at=now - 300 * 24 * 3600,
        archived_at=now - 200 * 24 * 3600,
    )
    db_session.add(old_archive)
    db_session.commit()

    summary = run_audit_retention(
        db=db_session,
        active_retention_days=30,
        archive_retention_days=180,
        batch_size=100,
        dry_run=False,
    )
    assert summary["archived_count"] >= 1
    assert summary["deleted_archive_count"] >= 1

    assert db_session.query(AuditLog).filter(AuditLog.request_id == "r1").first() is None
    assert db_session.query(AuditLogArchive).filter(AuditLogArchive.request_id == "r1").first() is not None
    assert db_session.query(AuditLogArchive).filter(AuditLogArchive.request_id == "r2").first() is None


def test_non_admin_cannot_run_governance_api(client, create_user_and_login, auth_headers):
    token = create_user_and_login("normal-user", "pwd")
    response = client.post(
        "/api/audit-logs/governance/run",
        headers=auth_headers(token),
        json={"active_retention_days": 30, "archive_retention_days": 180, "dry_run": True},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"


def test_admin_can_run_governance_api(client, create_user_and_login, auth_headers, db_session):
    token = create_user_and_login("admin-user", "pwd")
    admin = db_session.query(User).filter(User.username == "admin-user").first()
    admin.role = "admin"
    db_session.commit()

    response = client.post(
        "/api/audit-logs/governance/run",
        headers=auth_headers(token),
        json={"active_retention_days": 30, "archive_retention_days": 180, "dry_run": True},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["dry_run"] is True
    assert "candidate_archive_count" in body


def test_admin_can_query_all_users_audit_logs(client, create_user_and_login, auth_headers, db_session):
    owner_token = create_user_and_login("owner", "pwd")
    other_token = create_user_and_login("other", "pwd")

    owner_headers = auth_headers(owner_token)
    other_headers = auth_headers(other_token)

    admin = db_session.query(User).filter(User.username == "owner").first()
    admin.role = "admin"
    db_session.commit()

    client.post("/api/projects/", headers=owner_headers, json={"name": "Owner P", "description": "desc"})
    client.post("/api/projects/", headers=other_headers, json={"name": "Other P", "description": "desc"})

    admin_view = client.get("/api/audit-logs/?page=1&page_size=100", headers=owner_headers)
    assert admin_view.status_code == 200
    user_ids = {item["user_id"] for item in admin_view.json()["items"]}
    assert 1 in user_ids
    assert 2 in user_ids
