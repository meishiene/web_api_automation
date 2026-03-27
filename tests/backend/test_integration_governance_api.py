import json
import time

from app.models.audit_log import AuditLog
from app.models.integration_event import IntegrationEvent
from app.models.integration_governance_execution import IntegrationGovernanceExecution
from app.models.notification_delivery import NotificationDelivery
from app.models.notification_subscription import NotificationSubscription
from app.models.user import User


def _create_owner_project_and_identity_config(client, create_user_and_login, auth_headers, username: str, project_name: str):
    token = create_user_and_login(username, "pwd")
    headers = auth_headers(token)
    project_id = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": project_name, "description": "desc"},
    ).json()["id"]
    config_resp = client.post(
        f"/api/integrations/project/{project_id}",
        headers=headers,
        json={
            "name": "gov-webhook",
            "integration_type": "webhook",
            "provider": "generic_webhook",
            "credential_value": "secret",
            "config_json": {"max_attempts": 3},
            "is_enabled": True,
        },
    )
    assert config_resp.status_code == 200
    return token, headers, project_id, config_resp.json()["id"]


def test_governance_health_and_bulk_retry(client, create_user_and_login, auth_headers, db_session):
    _owner_token, owner_headers, project_id, config_id = _create_owner_project_and_identity_config(
        client,
        create_user_and_login,
        auth_headers,
        "owner_gov_health",
        "P-gov-health",
    )

    now = int(time.time())
    failed_event = IntegrationEvent(
        integration_config_id=config_id,
        project_id=project_id,
        event_type="governance.test",
        direction="inbound",
        status="failed",
        payload_json="{}",
        headers_json="{}",
        signature=None,
        idempotency_key="gov-event-1",
        attempt_count=0,
        max_attempts=3,
        next_retry_at=None,
        last_error="seed failure",
        last_processed_at=None,
        created_at=now,
        updated_at=now,
    )
    db_session.add(failed_event)

    subscription = NotificationSubscription(
        project_id=project_id,
        name="gov-notify",
        event_type="test_run.finished",
        channel_type="webhook",
        destination="mock://flaky",
        is_enabled=1,
        max_attempts=3,
        created_by=1,
        created_at=now,
        updated_at=now,
    )
    db_session.add(subscription)
    db_session.flush()

    dead_delivery = NotificationDelivery(
        subscription_id=subscription.id,
        project_id=project_id,
        event_type="test_run.finished",
        channel_type="webhook",
        destination="mock://flaky",
        payload_json='{"run_id": 1}',
        status="dead_letter",
        attempt_count=1,
        max_attempts=3,
        next_retry_at=None,
        last_error="seed dead letter",
        last_attempt_at=now,
        created_at=now,
        updated_at=now,
    )
    db_session.add(dead_delivery)
    db_session.commit()

    health_resp = client.get(
        f"/api/integrations/project/{project_id}/governance/health",
        headers=owner_headers,
    )
    assert health_resp.status_code == 200
    health = health_resp.json()
    assert health["retry_backlog"]["events"] >= 1
    assert health["retry_backlog"]["deliveries"] >= 1
    assert health["event_status_counts"].get("failed", 0) >= 1
    assert health["delivery_status_counts"].get("dead_letter", 0) >= 1

    retry_resp = client.post(
        f"/api/integrations/project/{project_id}/governance/retry-failed",
        headers=owner_headers,
        json={"max_events": 10, "max_deliveries": 10},
    )
    assert retry_resp.status_code == 200
    retry_data = retry_resp.json()
    assert retry_data["retried_events"] >= 1
    assert retry_data["retried_deliveries"] >= 1
    assert retry_data["execution"]["execution_type"] == "retry_failed"
    assert retry_data["idempotent_reused"] is False

    db_session.refresh(failed_event)
    db_session.refresh(dead_delivery)
    assert failed_event.status == "processed"
    assert dead_delivery.status in {"retry_pending", "sent"}


def test_governance_single_event_retry_acl_and_audit(client, create_user_and_login, auth_headers, db_session):
    _owner_token, owner_headers, project_id, config_id = _create_owner_project_and_identity_config(
        client,
        create_user_and_login,
        auth_headers,
        "owner_gov_event",
        "P-gov-event",
    )
    attacker_token = create_user_and_login("attacker_gov_event", "pwd")

    now = int(time.time())
    event = IntegrationEvent(
        integration_config_id=config_id,
        project_id=project_id,
        event_type="governance.single.retry",
        direction="inbound",
        status="failed",
        payload_json="{}",
        headers_json="{}",
        signature=None,
        idempotency_key="gov-event-single",
        attempt_count=0,
        max_attempts=2,
        next_retry_at=None,
        last_error="seed failure",
        last_processed_at=None,
        created_at=now,
        updated_at=now,
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)

    forbidden = client.post(
        f"/api/integrations/events/{event.id}/governance/retry",
        headers=auth_headers(attacker_token),
    )
    assert forbidden.status_code == 403

    ok = client.post(
        f"/api/integrations/events/{event.id}/governance/retry",
        headers=owner_headers,
    )
    assert ok.status_code == 200
    assert ok.json()["event"]["status"] == "processed"

    audit_row = (
        db_session.query(AuditLog)
        .filter(AuditLog.action == "integration_governance.event.retry")
        .order_by(AuditLog.id.desc())
        .first()
    )
    assert audit_row is not None
    details = json.loads(audit_row.details)
    assert details["project_id"] == project_id
    assert details["governance_scope"] == "single_event"
    assert details["governance_target_type"] == "integration_event"
    assert details["governance_target_id"] == event.id


def test_governance_health_admin_can_view_foreign_project(client, create_user_and_login, auth_headers, db_session):
    _owner_token, _owner_headers, project_id, _config_id = _create_owner_project_and_identity_config(
        client,
        create_user_and_login,
        auth_headers,
        "owner_gov_admin",
        "P-gov-admin",
    )
    attacker_token = create_user_and_login("attacker_gov_admin", "pwd")
    admin_token = create_user_and_login("admin_gov_admin", "pwd")

    admin = db_session.query(User).filter(User.username == "admin_gov_admin").first()
    admin.role = "admin"
    db_session.commit()

    forbidden = client.get(
        f"/api/integrations/project/{project_id}/governance/health",
        headers=auth_headers(attacker_token),
    )
    assert forbidden.status_code == 403

    ok = client.get(
        f"/api/integrations/project/{project_id}/governance/health",
        headers=auth_headers(admin_token),
    )
    assert ok.status_code == 200
    assert ok.json()["project_id"] == project_id


def test_governance_bulk_retry_is_idempotent_and_trackable(client, create_user_and_login, auth_headers, db_session):
    _owner_token, owner_headers, project_id, config_id = _create_owner_project_and_identity_config(
        client,
        create_user_and_login,
        auth_headers,
        "owner_gov_idempotent",
        "P-gov-idempotent",
    )

    now = int(time.time())
    failed_event = IntegrationEvent(
        integration_config_id=config_id,
        project_id=project_id,
        event_type="governance.idempotent.event",
        direction="inbound",
        status="failed",
        payload_json="{}",
        headers_json="{}",
        signature=None,
        idempotency_key="gov-event-idempotent",
        attempt_count=0,
        max_attempts=3,
        next_retry_at=None,
        last_error="seed failure",
        last_processed_at=None,
        created_at=now,
        updated_at=now,
    )
    db_session.add(failed_event)

    subscription = NotificationSubscription(
        project_id=project_id,
        name="gov-idempotent-notify",
        event_type="test_run.finished",
        channel_type="webhook",
        destination="mock://flaky",
        is_enabled=1,
        max_attempts=3,
        created_by=1,
        created_at=now,
        updated_at=now,
    )
    db_session.add(subscription)
    db_session.flush()

    retry_delivery = NotificationDelivery(
        subscription_id=subscription.id,
        project_id=project_id,
        event_type="test_run.finished",
        channel_type="webhook",
        destination="mock://flaky",
        payload_json='{"run_id": 2}',
        status="retry_pending",
        attempt_count=1,
        max_attempts=3,
        next_retry_at=now + 60,
        last_error="seed retry",
        last_attempt_at=now,
        created_at=now,
        updated_at=now,
    )
    db_session.add(retry_delivery)
    db_session.commit()

    first = client.post(
        f"/api/integrations/project/{project_id}/governance/retry-failed",
        headers=owner_headers,
        json={"max_events": 10, "max_deliveries": 10, "idempotency_key": "retry-batch-001"},
    )
    assert first.status_code == 200
    first_body = first.json()
    assert first_body["idempotent_reused"] is False
    assert first_body["retried_events"] == 1
    assert first_body["retried_deliveries"] == 1
    assert first_body["execution"]["execution_type"] == "retry_failed"
    execution_id = first_body["execution"]["id"]

    db_session.refresh(failed_event)
    db_session.refresh(retry_delivery)
    assert failed_event.attempt_count == 1
    assert retry_delivery.attempt_count == 2

    second = client.post(
        f"/api/integrations/project/{project_id}/governance/retry-failed",
        headers=owner_headers,
        json={"max_events": 10, "max_deliveries": 10, "idempotency_key": "retry-batch-001"},
    )
    assert second.status_code == 200
    second_body = second.json()
    assert second_body["idempotent_reused"] is True
    assert second_body["execution"]["id"] == execution_id
    assert second_body["retried_events"] == 1
    assert second_body["retried_deliveries"] == 1

    db_session.refresh(failed_event)
    db_session.refresh(retry_delivery)
    assert failed_event.attempt_count == 1
    assert retry_delivery.attempt_count == 2

    executions = client.get(
        f"/api/integrations/project/{project_id}/governance/executions",
        headers=owner_headers,
    )
    assert executions.status_code == 200
    executions_body = executions.json()
    assert executions_body["total"] == 1
    assert executions_body["items"][0]["id"] == execution_id
    assert executions_body["items"][0]["idempotency_key"] == "retry-batch-001"

    execution_record = (
        db_session.query(IntegrationGovernanceExecution)
        .filter(IntegrationGovernanceExecution.id == execution_id)
        .first()
    )
    assert execution_record is not None
    assert execution_record.execution_type == "retry_failed"


def test_governance_bulk_retry_audit_fields_and_execution_acl(client, create_user_and_login, auth_headers, db_session):
    attacker_token = create_user_and_login("attacker_gov_execution", "pwd")
    _owner_token, owner_headers, project_id, config_id = _create_owner_project_and_identity_config(
        client,
        create_user_and_login,
        auth_headers,
        "owner_gov_execution",
        "P-gov-execution",
    )

    now = int(time.time())
    failed_event = IntegrationEvent(
        integration_config_id=config_id,
        project_id=project_id,
        event_type="governance.audit.event",
        direction="inbound",
        status="failed",
        payload_json="{}",
        headers_json="{}",
        signature=None,
        idempotency_key="gov-event-audit",
        attempt_count=0,
        max_attempts=2,
        next_retry_at=None,
        last_error="seed failure",
        last_processed_at=None,
        created_at=now,
        updated_at=now,
    )
    db_session.add(failed_event)
    db_session.commit()

    retry_resp = client.post(
        f"/api/integrations/project/{project_id}/governance/retry-failed",
        headers=owner_headers,
        json={"max_events": 5, "max_deliveries": 5, "idempotency_key": "audit-batch-001"},
    )
    assert retry_resp.status_code == 200
    execution_id = retry_resp.json()["execution"]["id"]

    forbidden = client.get(
        f"/api/integrations/project/{project_id}/governance/executions",
        headers=auth_headers(attacker_token),
    )
    assert forbidden.status_code == 403

    audit_row = (
        db_session.query(AuditLog)
        .filter(
            AuditLog.action == "integration_governance.retry_failed",
            AuditLog.resource_type == "integration_governance_execution",
            AuditLog.resource_id == str(execution_id),
        )
        .order_by(AuditLog.id.desc())
        .first()
    )
    assert audit_row is not None
    details = json.loads(audit_row.details)
    assert details["project_id"] == project_id
    assert details["governance_execution_id"] == execution_id
    assert details["execution_type"] == "retry_failed"
    assert details["idempotency_key"] == "audit-batch-001"
    assert details["idempotent_reused"] is False
