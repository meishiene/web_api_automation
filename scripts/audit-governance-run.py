import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app import models  # noqa: F401
from app.services.audit_governance_orchestrator import (
    AuditGovernanceThresholds,
    evaluate_audit_governance_alerts,
)
from app.services.audit_service import run_audit_retention


ALERT_EXIT_CODE = 2


class LockAcquisitionError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run audit log archive/retention governance")
    parser.add_argument("--active-retention-days", type=int, default=settings.AUDIT_LOG_ACTIVE_RETENTION_DAYS)
    parser.add_argument("--archive-retention-days", type=int, default=settings.AUDIT_LOG_ARCHIVE_RETENTION_DAYS)
    parser.add_argument("--batch-size", type=int, default=settings.AUDIT_LOG_RETENTION_BATCH_SIZE)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--lock-file", type=str, default=settings.AUDIT_GOVERNANCE_LOCK_FILE)
    parser.add_argument("--manifest-dir", type=str, default=settings.AUDIT_GOVERNANCE_MANIFEST_DIR)
    parser.add_argument(
        "--max-candidate-archive-count",
        type=int,
        default=settings.AUDIT_GOVERNANCE_MAX_CANDIDATE_ARCHIVE_COUNT,
    )
    parser.add_argument(
        "--max-candidate-delete-archive-count",
        type=int,
        default=settings.AUDIT_GOVERNANCE_MAX_CANDIDATE_DELETE_ARCHIVE_COUNT,
    )
    parser.add_argument("--max-archived-count", type=int, default=settings.AUDIT_GOVERNANCE_MAX_ARCHIVED_COUNT)
    parser.add_argument(
        "--max-deleted-archive-count",
        type=int,
        default=settings.AUDIT_GOVERNANCE_MAX_DELETED_ARCHIVE_COUNT,
    )
    parser.add_argument("--fail-on-alert", action="store_true", default=settings.AUDIT_GOVERNANCE_FAIL_ON_ALERT)
    parser.add_argument("--alert-output", type=str, default=settings.AUDIT_GOVERNANCE_ALERT_OUTPUT or "")
    return parser.parse_args()


def _acquire_lock(lock_file: str) -> int:
    lock_dir = os.path.dirname(lock_file)
    if lock_dir:
        os.makedirs(lock_dir, exist_ok=True)
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    try:
        fd = os.open(lock_file, flags)
    except FileExistsError as exc:
        raise LockAcquisitionError(f"Lock file already exists: {lock_file}") from exc
    return fd


def _release_lock(fd: int, lock_file: str) -> None:
    try:
        os.close(fd)
    finally:
        if os.path.exists(lock_file):
            os.remove(lock_file)


def _build_thresholds(args: argparse.Namespace) -> AuditGovernanceThresholds:
    return AuditGovernanceThresholds(
        max_candidate_archive_count=args.max_candidate_archive_count,
        max_candidate_delete_archive_count=args.max_candidate_delete_archive_count,
        max_archived_count=args.max_archived_count,
        max_deleted_archive_count=args.max_deleted_archive_count,
    )


def main() -> int:
    args = parse_args()
    started_at = datetime.now(timezone.utc)
    started_ts = time.time()
    lock_fd = None
    db: Session | None = None
    try:
        lock_fd = _acquire_lock(args.lock_file)
        db = SessionLocal()
        thresholds = _build_thresholds(args)
        result = run_audit_retention(
            db=db,
            active_retention_days=args.active_retention_days,
            archive_retention_days=args.archive_retention_days,
            batch_size=args.batch_size,
            dry_run=args.dry_run,
        )
        alerts = evaluate_audit_governance_alerts(result, thresholds)
        ended_at = datetime.now(timezone.utc)
        duration_ms = int((time.time() - started_ts) * 1000)
        status = "alert" if alerts else "ok"
        payload = {
            "ok": True,
            "status": status,
            "active_retention_days": args.active_retention_days,
            "archive_retention_days": args.archive_retention_days,
            "batch_size": args.batch_size,
            "dry_run": args.dry_run,
            "alerts": alerts,
            "started_at": started_at.isoformat(),
            "ended_at": ended_at.isoformat(),
            "duration_ms": duration_ms,
            "lock_file": os.path.abspath(args.lock_file),
            **result,
        }

        os.makedirs(args.manifest_dir, exist_ok=True)
        manifest_name = f"audit-governance-{started_at.strftime('%Y%m%d_%H%M%S')}.json"
        manifest_path = os.path.join(args.manifest_dir, manifest_name)
        payload["manifest_path"] = os.path.abspath(manifest_path)
        with open(manifest_path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False)

        if alerts and args.alert_output:
            alert_payload = {
                "ok": False,
                "status": "alert",
                "alerts": alerts,
                "manifest_path": payload["manifest_path"],
            }
            with open(args.alert_output, "w", encoding="utf-8") as fh:
                json.dump(alert_payload, fh, ensure_ascii=False)

        print(json.dumps(payload, ensure_ascii=False))
        if alerts and args.fail_on_alert:
            return ALERT_EXIT_CODE
        return 0
    except LockAcquisitionError as exc:
        print(json.dumps({"ok": False, "status": "locked", "error": str(exc)}, ensure_ascii=False))
        return 1
    finally:
        if db is not None:
            db.close()
        if lock_fd is not None:
            _release_lock(lock_fd, args.lock_file)


if __name__ == "__main__":
    try:
        exit_code = main()
    except Exception as exc:  # pragma: no cover - CLI guard
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        exit_code = 1
    sys.exit(exit_code)
