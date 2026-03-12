from sqlalchemy import create_engine
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
    from app.models.api_test_case import ApiTestCase
    from app.models.test_run import TestRun
    from app.models.schedule_task import ScheduleTask
    from app.models.run_queue import RunQueue
    Base.metadata.create_all(bind=engine)
