import argparse
import json
import sys
from typing import Set

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError

from app.config import settings

REQUIRED_TABLES: Set[str] = {
    "users",
    "projects",
    "api_test_cases",
    "test_runs",
    "schedule_tasks",
    "run_queue",
    "audit_logs",
    "alembic_version",
}


def run_check() -> int:
    database_url = settings.resolved_database_url
    engine_kwargs = {}
    if database_url.startswith("sqlite"):
        engine_kwargs["connect_args"] = {"check_same_thread": False}
    else:
        engine_kwargs["pool_pre_ping"] = True

    try:
        engine = create_engine(database_url, **engine_kwargs)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            table_names = set(inspect(connection).get_table_names())
    except SQLAlchemyError as exc:
        print(
            json.dumps(
                {
                    "ok": False,
                    "database_url": database_url,
                    "error": str(exc),
                },
                ensure_ascii=False,
            )
        )
        return 1

    missing = sorted(REQUIRED_TABLES - table_names)
    payload = {
        "ok": len(missing) == 0,
        "database_url": database_url,
        "tables": sorted(table_names),
        "missing_required_tables": missing,
    }
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if payload["ok"] else 2


def main() -> None:
    parser = argparse.ArgumentParser(description="Database connectivity and schema check")
    parser.parse_args()
    sys.exit(run_check())


if __name__ == "__main__":
    main()

