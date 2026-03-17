from app.models.audit_log import AuditLog
from app.models.user import User


def _create_subscription(client, headers, project_id, *, destination="mock://success", max_attempts=3):
    resp = client.post(
        f"/api/integrations/project/{project_id}/notification-subscriptions",
        headers=headers,
        json={
            "name": "notify-default",
            "event_type": "test_run.finished",
            "channel_type": "webhook",
            "destination": destination,
            "max_attempts": max_attempts,
            "is_enabled": True,
        },
    )
    assert resp.status_code == 200
    return resp.json()["id"]


def test_notification_subscription_and_dispatch_success(client, create_user_and_login, auth_headers):
    token = create_user_and_login("owner_notify", "pwd")
    headers = auth_headers(token)
    project_id = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P-notify", "description": "desc"},
    ).json()["id"]

    subscription_id = _create_subscription(client, headers, project_id, destination="mock://success")

    subscriptions = client.get(f"/api/integrations/project/{project_id}/notification-subscriptions", headers=headers)
    assert subscriptions.status_code == 200
    assert subscriptions.json()["total"] == 1

    dispatch = client.post(
        f"/api/integrations/notification-subscriptions/{subscription_id}/dispatch",
        headers=headers,
        json={"event_type": "test_run.finished", "payload": {"run_id": 123, "status": "success"}},
    )
    assert dispatch.status_code == 200
    delivery = dispatch.json()
    assert delivery["status"] == "sent"
    assert delivery["attempt_count"] == 1
    assert delivery["next_retry_at"] is None

    deliveries = client.get(f"/api/integrations/project/{project_id}/notification-deliveries", headers=headers)
    assert deliveries.status_code == 200
    assert deliveries.json()["total"] == 1
    assert deliveries.json()["items"][0]["status"] == "sent"


def test_notification_dispatch_retry_pending_then_success(client, create_user_and_login, auth_headers):
    token = create_user_and_login("owner_notify_retry", "pwd")
    headers = auth_headers(token)
    project_id = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P-notify-retry", "description": "desc"},
    ).json()["id"]

    subscription_id = _create_subscription(client, headers, project_id, destination="mock://flaky", max_attempts=3)

    dispatch = client.post(
        f"/api/integrations/notification-subscriptions/{subscription_id}/dispatch",
        headers=headers,
        json={"event_type": "test_run.finished", "payload": {"run_id": 999, "status": "failed"}},
    )
    assert dispatch.status_code == 200
    first = dispatch.json()
    assert first["status"] == "retry_pending"
    assert first["attempt_count"] == 1
    assert first["next_retry_at"] is not None

    retry = client.post(
        f"/api/integrations/notification-deliveries/{first['id']}/retry",
        headers=headers,
    )
    assert retry.status_code == 200
    second = retry.json()
    assert second["status"] == "sent"
    assert second["attempt_count"] == 2
    assert second["next_retry_at"] is None


def test_notification_dispatch_dead_letter_when_exhausted(client, create_user_and_login, auth_headers):
    token = create_user_and_login("owner_notify_dead", "pwd")
    headers = auth_headers(token)
    project_id = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P-notify-dead", "description": "desc"},
    ).json()["id"]

    subscription_id = _create_subscription(client, headers, project_id, destination="mock://always-fail", max_attempts=2)
    dispatch = client.post(
        f"/api/integrations/notification-subscriptions/{subscription_id}/dispatch",
        headers=headers,
        json={"event_type": "test_run.finished", "payload": {"run_id": 1}},
    )
    assert dispatch.status_code == 200
    first = dispatch.json()
    assert first["status"] == "retry_pending"

    retry = client.post(f"/api/integrations/notification-deliveries/{first['id']}/retry", headers=headers)
    assert retry.status_code == 200
    second = retry.json()
    assert second["status"] == "dead_letter"
    assert second["attempt_count"] == 2
    assert second["last_error"] is not None


def test_notification_acl_and_audit(client, create_user_and_login, auth_headers, db_session):
    owner_token = create_user_and_login("owner_notify_acl", "pwd")
    attacker_token = create_user_and_login("attacker_notify_acl", "pwd")
    admin_token = create_user_and_login("admin_notify_acl", "pwd")

    admin = db_session.query(User).filter(User.username == "admin_notify_acl").first()
    admin.role = "admin"
    db_session.commit()

    owner_headers = auth_headers(owner_token)
    project_id = client.post(
        "/api/projects/",
        headers=owner_headers,
        json={"name": "P-notify-acl", "description": "desc"},
    ).json()["id"]

    subscription_id = _create_subscription(client, owner_headers, project_id, destination="mock://success")

    forbidden_list = client.get(
        f"/api/integrations/project/{project_id}/notification-subscriptions",
        headers=auth_headers(attacker_token),
    )
    assert forbidden_list.status_code == 403

    forbidden_dispatch = client.post(
        f"/api/integrations/notification-subscriptions/{subscription_id}/dispatch",
        headers=auth_headers(attacker_token),
        json={"event_type": "test_run.finished", "payload": {"run_id": 2}},
    )
    assert forbidden_dispatch.status_code == 403

    admin_dispatch = client.post(
        f"/api/integrations/notification-subscriptions/{subscription_id}/dispatch",
        headers=auth_headers(admin_token),
        json={"event_type": "test_run.finished", "payload": {"run_id": 2}},
    )
    assert admin_dispatch.status_code == 200
    delivery_id = admin_dispatch.json()["id"]

    admin_list_deliveries = client.get(
        f"/api/integrations/project/{project_id}/notification-deliveries",
        headers=auth_headers(admin_token),
    )
    assert admin_list_deliveries.status_code == 200
    assert admin_list_deliveries.json()["total"] >= 1

    actions = {
        row.action
        for row in db_session.query(AuditLog)
        .filter(AuditLog.resource_type.in_(["notification_subscription", "notification_delivery"]))
        .all()
    }
    assert "notification_subscription.create" in actions
    assert "notification_subscription.dispatch" in actions
    assert "notification_delivery.list" in actions
    assert delivery_id > 0
