import json
import sys
from typing import Optional

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from app.config import settings


def get_current_revision(database_url: str) -> Optional[str]:
    engine_kwargs = {}
    if database_url.startswith("sqlite"):
        engine_kwargs["connect_args"] = {"check_same_thread": False}
    else:
        engine_kwargs["pool_pre_ping"] = True

    engine = create_engine(database_url, **engine_kwargs)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version_num FROM alembic_version"))
        rows = [row[0] for row in result.fetchall()]

    if not rows:
        return None
    if len(rows) > 1:
        raise ValueError(f"Expected single alembic revision row, got {len(rows)}")
    return rows[0]


def run_check(database_url: str) -> int:
    try:
        current_revision = get_current_revision(database_url)
    except (SQLAlchemyError, ValueError) as exc:
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

    print(
        json.dumps(
            {
                "ok": True,
                "database_url": database_url,
                "current_revision": current_revision,
            },
            ensure_ascii=False,
        )
    )
    return 0


def main() -> None:
    sys.exit(run_check(settings.resolved_database_url))


if __name__ == "__main__":
    main()
