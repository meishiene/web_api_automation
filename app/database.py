import logging
import os
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from app.config import settings

database_url = settings.resolved_database_url
engine_kwargs = {}
if database_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["pool_pre_ping"] = True

engine = create_engine(database_url, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
logger = logging.getLogger("app.database")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from app.models.user import Base
    from app.models.audit_log import AuditLog
    from app.models.audit_log_archive import AuditLogArchive
    from app.models.project import Project
    from app.models.project_member import ProjectMember
    from app.models.organization import Organization
    from app.models.organization_member import OrganizationMember
    from app.models.api_test_case import ApiTestCase
    from app.models.test_run import TestRun
    from app.models.schedule_task import ScheduleTask
    from app.models.run_queue import RunQueue
    Base.metadata.create_all(bind=engine)


def auto_migrate_db() -> None:
    if not settings.AUTO_DB_MIGRATE_ON_STARTUP:
        return
    if settings.APP_ENV == "prod":
        return
    if os.getenv("PYTEST_CURRENT_TEST"):
        return

    if _is_legacy_sqlite_schema():
        _repair_legacy_sqlite_schema()
        return

    repo_root = Path(__file__).resolve().parent.parent
    alembic_ini = repo_root / "alembic.ini"
    if not alembic_ini.exists():
        logger.warning("skip_auto_migrate_missing_alembic_ini")
        return

    alembic_cfg = Config(str(alembic_ini))
    alembic_cfg.set_main_option("sqlalchemy.url", settings.resolved_database_url)
    try:
        command.upgrade(alembic_cfg, "head")
    except Exception:
        if settings.resolved_database_url.startswith("sqlite"):
            logger.warning("auto_migrate_failed_fallback_legacy_repair")
            _repair_legacy_sqlite_schema()
            return
        raise


def _is_legacy_sqlite_schema() -> bool:
    if not settings.resolved_database_url.startswith("sqlite"):
        return False

    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    if "users" not in tables:
        return False
    if "alembic_version" in tables:
        return False
    return True


def _repair_legacy_sqlite_schema() -> None:
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())

    if "users" not in tables:
        return

    users_columns = {column["name"] for column in inspector.get_columns("users")}
    projects_columns = {column["name"] for column in inspector.get_columns("projects")} if "projects" in tables else set()

    with engine.begin() as connection:
        if "role" not in users_columns:
            connection.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'user'"))
            logger.warning("legacy_sqlite_patched_users_role")

        if "projects" in tables and "organization_id" not in projects_columns:
            connection.execute(text("ALTER TABLE projects ADD COLUMN organization_id INTEGER"))
            logger.warning("legacy_sqlite_patched_projects_organization_id")
