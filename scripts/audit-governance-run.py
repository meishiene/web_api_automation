import argparse
import json
import sys

from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.services.audit_service import run_audit_retention


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run audit log archive/retention governance")
    parser.add_argument("--active-retention-days", type=int, default=settings.AUDIT_LOG_ACTIVE_RETENTION_DAYS)
    parser.add_argument("--archive-retention-days", type=int, default=settings.AUDIT_LOG_ARCHIVE_RETENTION_DAYS)
    parser.add_argument("--batch-size", type=int, default=settings.AUDIT_LOG_RETENTION_BATCH_SIZE)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    db: Session = SessionLocal()
    try:
        result = run_audit_retention(
            db=db,
            active_retention_days=args.active_retention_days,
            archive_retention_days=args.archive_retention_days,
            batch_size=args.batch_size,
            dry_run=args.dry_run,
        )
        payload = {
            "ok": True,
            "active_retention_days": args.active_retention_days,
            "archive_retention_days": args.archive_retention_days,
            "batch_size": args.batch_size,
            "dry_run": args.dry_run,
            **result,
        }
        print(json.dumps(payload, ensure_ascii=False))
    finally:
        db.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - CLI guard
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        sys.exit(1)
