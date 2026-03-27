import time

from app.models.integration_config import IntegrationConfig
from app.models.integration_event import IntegrationEvent
from app.models.integration_governance_execution import IntegrationGovernanceExecution
from app.models.notification_delivery import NotificationDelivery
from app.models.notification_subscription import NotificationSubscription
from app.models.run_queue import RunQueue
from app.models.user import User


def _create_project(client, headers, name: str) -> int:
    resp = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": name, "description": "desc"},
    )
    assert resp.status_code == 200
    return resp.json()["id"]


def _seed_project_signals(db_session, project_id: int, suffix: str, owner_user_id: int, now: int) -> None:
    config = IntegrationConfig(
        project_id=project_id,
        name=f"cfg-{suffix}",
        integration_type="webhook",
        provider="generic_webhook",
        credential_value="secret",
        config_json="{}",
        is_enabled=1,
        created_by=owner_user_id,
        created_at=now,
        updated_at=now,
    )
    db_session.add(config)

    subscription = NotificationSubscription(
        project_id=project_id,
        name=f"sub-{suffix}",
        event_type="test_run.finished",
        channel_type="webhook",
        destination="mock://always-fail",
        is_enabled=1,
        max_attempts=3,
        created_by=owner_user_id,
        created_at=now,
        updated_at=now,
    )
    db_session.add(subscription)
    db_session.flush()

    # failed backlog (run_queue)
    db_session.add(
        RunQueue(
            project_id=project_id,
            run_type="api",
            target_type="test_case",
            target_id=11,
            status="failed",
            priority=3,
            payload="{}",
            scheduled_by="manual",
            created_at=now,
        )
    )
    db_session.add(
        RunQueue(
            project_id=project_id,
            run_type="web",
            target_type="test_case",
            target_id=12,
            status="error",
            priority=4,
            payload="{}",
            scheduled_by="manual",
            created_at=now,
        )
    )
    db_session.add(
        RunQueue(
            project_id=project_id,
            run_type="api",
            target_type="test_case",
            target_id=13,
            status="success",
            priority=5,
            payload="{}",
            scheduled_by="manual",
            created_at=now,
        )
    )

    # retry trend + backlog (integration_events)
    db_session.add(
        IntegrationEvent(
            integration_config_id=config.id,
            project_id=project_id,
            event_type="seed.retry_pending",
            direction="inbound",
            status="retry_pending",
            payload_json="{}",
            headers_json="{}",
            signature=None,
            idempotency_key=f"evt-retry-{suffix}",
            attempt_count=1,
            max_attempts=3,
            next_retry_at=now + 60,
            last_error="retry",
            last_processed_at=now,
            created_at=now,
            updated_at=now,
        )
    )
    db_session.add(
        IntegrationEvent(
            integration_config_id=config.id,
            project_id=project_id,
            event_type="seed.failed",
            direction="inbound",
            status="failed",
            payload_json="{}",
            headers_json="{}",
            signature=None,
            idempotency_key=f"evt-failed-{suffix}",
            attempt_count=3,
            max_attempts=3,
            next_retry_at=None,
            last_error="failed",
            last_processed_at=now,
            created_at=now - 86400,
            updated_at=now - 86400,
        )
    )

    # dead-letter + retry trend
    db_session.add(
        NotificationDelivery(
            subscription_id=subscription.id,
            project_id=project_id,
            event_type="test_run.finished",
            channel_type="webhook",
            destination="mock://always-fail",
            payload_json="{}",
            status="dead_letter",
            attempt_count=3,
            max_attempts=3,
            next_retry_at=None,
            last_error="dead",
            last_attempt_at=now,
            created_at=now,
            updated_at=now,
        )
    )
    db_session.add(
        NotificationDelivery(
            subscription_id=subscription.id,
            project_id=project_id,
            event_type="test_run.finished",
            channel_type="webhook",
            destination="mock://always-fail",
            payload_json="{}",
            status="retry_pending",
            attempt_count=1,
            max_attempts=3,
            next_retry_at=now + 60,
            last_error="retry",
            last_attempt_at=now - 86400,
            created_at=now - 86400,
            updated_at=now - 86400,
        )
    )


def test_operations_overview_aggregates_cross_project_signals(client, create_user_and_login, auth_headers, db_session):
    owner_token = create_user_and_login("owner_ops_overview", "pwd")
    outsider_token = create_user_and_login("outsider_ops_overview", "pwd")
    owner_headers = auth_headers(owner_token)
    outsider_headers = auth_headers(outsider_token)

    owner_project_1 = _create_project(client, owner_headers, "P-ops-owner-1")
    owner_project_2 = _create_project(client, owner_headers, "P-ops-owner-2")
    outsider_project = _create_project(client, outsider_headers, "P-ops-outsider")

    now = int(time.time())
    owner_id = db_session.query(User).filter(User.username == "owner_ops_overview").first().id
    outsider_id = db_session.query(User).filter(User.username == "outsider_ops_overview").first().id

    _seed_project_signals(db_session, owner_project_1, "owner-1", owner_id, now)
    _seed_project_signals(db_session, owner_project_2, "owner-2", owner_id, now)
    _seed_project_signals(db_session, outsider_project, "outsider", outsider_id, now)
    db_session.commit()

    resp = client.get("/api/reports/operations/overview?days=2", headers=owner_headers)
    assert resp.status_code == 200
    body = resp.json()

    assert body["project_count"] == 2
    assert body["failed_backlog"] == 4
    assert body["dead_letter_backlog"] == 2
    assert body["retry_backlog"] == 8
    assert len(body["project_signals"]) == 2
    assert {item["project_id"] for item in body["project_signals"]} == {owner_project_1, owner_project_2}
    assert all(item["retry_backlog"] == 4 for item in body["project_signals"])

    trend = body["retry_trend"]
    assert len(trend) == 2
    latest_bucket = trend[-1]
    previous_bucket = trend[0]
    assert latest_bucket["retry_events"] == 2
    assert latest_bucket["retry_deliveries"] == 2
    assert previous_bucket["retry_events"] == 2
    assert previous_bucket["retry_deliveries"] == 2


def test_operations_overview_rejects_forbidden_project_filter(client, create_user_and_login, auth_headers):
    owner_token = create_user_and_login("owner_ops_filter", "pwd")
    outsider_token = create_user_and_login("outsider_ops_filter", "pwd")
    owner_headers = auth_headers(owner_token)
    outsider_headers = auth_headers(outsider_token)

    owner_project = _create_project(client, owner_headers, "P-ops-filter-owner")
    outsider_project = _create_project(client, outsider_headers, "P-ops-filter-outsider")

    ok = client.get(
        "/api/reports/operations/overview",
        headers=owner_headers,
        params={"project_ids": [owner_project]},
    )
    assert ok.status_code == 200
    assert ok.json()["project_count"] == 1

    forbidden = client.get(
        "/api/reports/operations/overview",
        headers=owner_headers,
        params={"project_ids": [owner_project, outsider_project]},
    )
    assert forbidden.status_code == 403
    assert forbidden.json()["error"]["code"] == "FORBIDDEN"


def test_operations_overview_returns_guardrails_for_alerts_and_truncation(
    client, create_user_and_login, auth_headers, db_session
):
    owner_token = create_user_and_login("owner_ops_guardrails", "pwd")
    owner_headers = auth_headers(owner_token)
    owner_id = db_session.query(User).filter(User.username == "owner_ops_guardrails").first().id
    now = int(time.time())

    project_ids = []
    for idx in range(25):
        project_id = _create_project(client, owner_headers, f"P-ops-guardrails-{idx}")
        project_ids.append(project_id)
        _seed_project_signals(db_session, project_id, f"guardrails-{idx}", owner_id, now)
    db_session.commit()

    resp = client.get("/api/reports/operations/overview?days=2", headers=owner_headers)
    assert resp.status_code == 200
    body = resp.json()

    assert body["project_count"] == 25
    assert len(body["project_signals"]) == 20
    assert body["guardrails"]["degraded"] is True
    assert "project_signals_truncated" in body["guardrails"]["degradation_reasons"]
    assert body["guardrails"]["project_signal_limit"] == 20
    assert body["guardrails"]["project_signal_returned"] == 20
    alert_codes = {item["code"] for item in body["guardrails"]["alerts"]}
    assert "retry_backlog.critical" in alert_codes
    assert "dead_letter_backlog.critical" in alert_codes
    assert "failed_backlog.warning" in alert_codes


def test_stage7_stability_baseline_for_operations_and_governance_lists(
    client, create_user_and_login, auth_headers, db_session
):
    owner_token = create_user_and_login("owner_ops_perf", "pwd")
    owner_headers = auth_headers(owner_token)
    owner_id = db_session.query(User).filter(User.username == "owner_ops_perf").first().id
    now = int(time.time())

    project_id = _create_project(client, owner_headers, "P-ops-perf")
    for idx in range(18):
        suffix = f"perf-{idx}"
        _seed_project_signals(db_session, project_id, suffix, owner_id, now - idx * 3600)

    for idx in range(500):
        db_session.add(
            IntegrationGovernanceExecution(
                project_id=project_id,
                execution_type="retry_failed",
                status="completed",
                idempotency_key=f"perf-key-{idx}",
                request_json='{"max_deliveries": 20, "max_events": 20}',
                result_json='{"retried_deliveries": 2, "retried_events": 2, "skipped_deliveries": 18, "skipped_events": 18}',
                requested_by=owner_id,
                completed_at=now - idx,
                created_at=now - idx,
                updated_at=now - idx,
            )
        )
    db_session.commit()

    start_overview = time.perf_counter()
    overview_resp = client.get(
        f"/api/reports/operations/overview?project_ids={project_id}&days=14",
        headers=owner_headers,
    )
    overview_elapsed = time.perf_counter() - start_overview

    start_executions = time.perf_counter()
    executions_resp = client.get(
        f"/api/integrations/project/{project_id}/governance/executions?page=1&page_size=50",
        headers=owner_headers,
    )
    executions_elapsed = time.perf_counter() - start_executions

    assert overview_resp.status_code == 200
    assert executions_resp.status_code == 200
    assert overview_elapsed < 3.0
    assert executions_elapsed < 3.0
    assert executions_resp.json()["total"] == 500
    assert len(executions_resp.json()["items"]) == 50
