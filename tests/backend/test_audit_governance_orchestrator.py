from app.services.audit_governance_orchestrator import (
    AuditGovernanceThresholds,
    evaluate_audit_governance_alerts,
)


def test_evaluate_alerts_returns_empty_when_within_thresholds():
    summary = {
        "candidate_archive_count": 10,
        "candidate_delete_archive_count": 5,
        "archived_count": 8,
        "deleted_archive_count": 3,
    }
    thresholds = AuditGovernanceThresholds(
        max_candidate_archive_count=10,
        max_candidate_delete_archive_count=5,
        max_archived_count=8,
        max_deleted_archive_count=3,
    )

    alerts = evaluate_audit_governance_alerts(summary, thresholds)

    assert alerts == []


def test_evaluate_alerts_returns_messages_for_exceeded_thresholds():
    summary = {
        "candidate_archive_count": 11,
        "candidate_delete_archive_count": 6,
        "archived_count": 9,
        "deleted_archive_count": 4,
    }
    thresholds = AuditGovernanceThresholds(
        max_candidate_archive_count=10,
        max_candidate_delete_archive_count=5,
        max_archived_count=8,
        max_deleted_archive_count=3,
    )

    alerts = evaluate_audit_governance_alerts(summary, thresholds)

    assert len(alerts) == 4
    assert "candidate_archive_count exceeded threshold" in alerts[0]
    assert "candidate_delete_archive_count exceeded threshold" in alerts[1]
    assert "archived_count exceeded threshold" in alerts[2]
    assert "deleted_archive_count exceeded threshold" in alerts[3]
