from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class AuditGovernanceThresholds:
    max_candidate_archive_count: Optional[int] = None
    max_candidate_delete_archive_count: Optional[int] = None
    max_archived_count: Optional[int] = None
    max_deleted_archive_count: Optional[int] = None


def evaluate_audit_governance_alerts(
    summary: Dict[str, Any],
    thresholds: AuditGovernanceThresholds,
) -> List[str]:
    alerts: List[str] = []

    checks = [
        (
            "candidate_archive_count",
            thresholds.max_candidate_archive_count,
            "candidate_archive_count exceeded threshold",
        ),
        (
            "candidate_delete_archive_count",
            thresholds.max_candidate_delete_archive_count,
            "candidate_delete_archive_count exceeded threshold",
        ),
        (
            "archived_count",
            thresholds.max_archived_count,
            "archived_count exceeded threshold",
        ),
        (
            "deleted_archive_count",
            thresholds.max_deleted_archive_count,
            "deleted_archive_count exceeded threshold",
        ),
    ]

    for key, threshold, message in checks:
        if threshold is None:
            continue
        value = int(summary.get(key, 0))
        if value > threshold:
            alerts.append(f"{message}: value={value}, threshold={threshold}")

    return alerts
