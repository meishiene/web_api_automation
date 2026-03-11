from sqlalchemy import Column, Integer, String, ForeignKey, Text
from app.models.user import Base


class RunQueue(Base):
    __tablename__ = "run_queue"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)

    # run_type: api | web
    run_type = Column(String(20), nullable=False, index=True)

    # target_type: test_case | test_suite
    target_type = Column(String(50), nullable=False)
    target_id = Column(Integer, nullable=False, index=True)

    # status: queued | running | success | failed | error
    status = Column(String(20), nullable=False, index=True, default="queued")
    priority = Column(Integer, nullable=False, default=5)

    # payload: JSON string for run parameters (env, dataset, overrides, etc.)
    payload = Column(Text, nullable=True)

    # scheduled_by: manual | scheduler | ci
    scheduled_by = Column(String(20), nullable=False, default="manual")

    worker_id = Column(String(100), nullable=True, index=True)
    started_at = Column(Integer, nullable=True)
    finished_at = Column(Integer, nullable=True)
    created_at = Column(Integer, nullable=False)
