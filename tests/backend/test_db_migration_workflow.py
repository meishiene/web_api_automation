import json
import sqlite3

from sqlalchemy import create_engine, text

import app.database as database_module
from scripts.db_revision_check import get_current_revision, run_check


def test_get_current_revision_returns_version(tmp_path):
    database_path = tmp_path / "migration.db"
    connection = sqlite3.connect(database_path)
    connection.execute("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)")
    connection.execute("INSERT INTO alembic_version (version_num) VALUES (?)", ("fcf57b5ad65c",))
    connection.commit()
    connection.close()

    revision = get_current_revision(f"sqlite:///{database_path.as_posix()}")

    assert revision == "fcf57b5ad65c"


def test_run_check_returns_error_when_version_table_missing(tmp_path, capsys):
    database_path = tmp_path / "migration.db"
    sqlite3.connect(database_path).close()

    exit_code = run_check(f"sqlite:///{database_path.as_posix()}")

    assert exit_code == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False
    assert "alembic_version" in payload["error"]


def test_repair_legacy_sqlite_schema_adds_missing_columns(tmp_path, monkeypatch):
    database_path = tmp_path / "legacy.db"
    legacy_engine = create_engine(f"sqlite:///{database_path.as_posix()}")
    with legacy_engine.begin() as connection:
        connection.execute(text("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, created_at INTEGER)"))
        connection.execute(text("CREATE TABLE projects (id INTEGER PRIMARY KEY, name TEXT, description TEXT, owner_id INTEGER, created_at INTEGER)"))

    class _DummySettings:
        resolved_database_url = f"sqlite:///{database_path.as_posix()}"

    monkeypatch.setattr(database_module, "engine", legacy_engine)
    monkeypatch.setattr(database_module, "settings", _DummySettings())

    assert database_module._is_legacy_sqlite_schema() is True
    database_module._repair_legacy_sqlite_schema()

    with legacy_engine.connect() as connection:
        users_columns = [row[1] for row in connection.execute(text("PRAGMA table_info(users)"))]
        projects_columns = [row[1] for row in connection.execute(text("PRAGMA table_info(projects)"))]

    assert "role" in users_columns
    assert "organization_id" in projects_columns
