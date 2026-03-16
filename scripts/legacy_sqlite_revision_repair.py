#!/usr/bin/env python
"""Repair legacy SQLite Alembic revision drift by schema fingerprint."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path
from typing import Iterable


REV_BASE = "8daac485a5f7"
REV_01FCC = "01fcc228897e"
REV_802 = "802c16c9f78e"
REV_FCF = "fcf57b5ad65c"
REV_9B1 = "9b1f0b38d7d2"
REV_D1F = "d1f8902c4b61"
REV_E2B = "e2b4c6a8d901"
REV_A7C = "a7c3d9e1f2b4"
REV_B8F = "b8f56e6e43f1"
REV_C3E = "c3e8a6b1d2f4"
REV_ADE = "adeb808fa0e9"
REV_11E = "11eb5f289eaf"
REV_F2A = "f2a1c4d8b9e3"
REV_2C1 = "2c1b7f9a4d10"


def _table_names(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    return {row[0] for row in rows}


def _column_names(conn: sqlite3.Connection, table: str) -> set[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return {row[1] for row in rows}


def _has_table(tables: set[str], *names: str) -> bool:
    return all(name in tables for name in names)


def _has_columns(conn: sqlite3.Connection, table: str, columns: Iterable[str]) -> bool:
    if table not in _table_names(conn):
        return False
    current = _column_names(conn, table)
    return all(col in current for col in columns)


def infer_revision(conn: sqlite3.Connection) -> str:
    tables = _table_names(conn)

    # Latest first: pick the highest revision whose signature exists.
    if _has_table(tables, "worker_heartbeats"):
        return REV_2C1
    if _has_table(tables, "execution_tasks", "execution_jobs"):
        return REV_F2A
    if _has_table(tables, "web_test_runs"):
        return REV_11E
    if _has_table(tables, "web_test_cases", "web_steps", "web_locators"):
        return REV_ADE
    if _has_table(tables, "environment_variable_group_bindings") or _has_columns(
        conn,
        "project_variables",
        ["group_name"],
    ):
        return REV_C3E
    if _has_columns(conn, "organization_members", ["department", "workspace"]):
        return REV_B8F
    if _has_columns(conn, "api_test_cases", ["case_group", "tags"]):
        return REV_A7C
    if _has_table(
        tables,
        "api_test_suites",
        "api_test_suite_cases",
        "api_batch_runs",
        "api_batch_run_items",
        "project_environments",
        "project_variables",
        "environment_variables",
    ):
        return REV_E2B
    if _has_table(tables, "organizations", "organization_members"):
        return REV_D1F
    if _has_table(tables, "project_members"):
        return REV_9B1
    if _has_columns(conn, "users", ["role"]):
        return REV_FCF
    if _has_table(tables, "audit_logs_archive"):
        return REV_802
    if _has_columns(conn, "projects", ["organization_id"]):
        return REV_01FCC
    return REV_BASE


def current_revision(conn: sqlite3.Connection) -> str | None:
    tables = _table_names(conn)
    if "alembic_version" not in tables:
        return None
    row = conn.execute("SELECT version_num FROM alembic_version LIMIT 1").fetchone()
    return row[0] if row else None


def apply_revision(conn: sqlite3.Connection, revision: str) -> None:
    tables = _table_names(conn)
    if "alembic_version" not in tables:
        conn.execute("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)")
        conn.execute("CREATE UNIQUE INDEX ix_alembic_version_num ON alembic_version (version_num)")
        conn.execute("INSERT INTO alembic_version (version_num) VALUES (?)", (revision,))
        return

    rows = conn.execute("SELECT version_num FROM alembic_version").fetchall()
    if not rows:
        conn.execute("INSERT INTO alembic_version (version_num) VALUES (?)", (revision,))
        return

    conn.execute("UPDATE alembic_version SET version_num = ?", (revision,))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Repair legacy SQLite alembic revision drift by schema fingerprint."
    )
    parser.add_argument(
        "--db",
        default="test_platform.db",
        help="Path to SQLite database file. Default: test_platform.db",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply repair; without this flag script only prints diagnosis.",
    )
    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"[repair] database not found: {db_path}")
        return 1

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        current = current_revision(conn)
        inferred = infer_revision(conn)
        print(f"[repair] db={db_path}")
        print(f"[repair] current_revision={current}")
        print(f"[repair] inferred_revision={inferred}")

        if current == inferred:
            print("[repair] no action needed")
            return 0

        if not args.apply:
            print("[repair] drift detected; run with --apply to repair")
            return 2

        apply_revision(conn, inferred)
        conn.commit()
        updated = current_revision(conn)
        print(f"[repair] repaired_revision={updated}")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
