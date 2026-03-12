import json
import sqlite3

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
