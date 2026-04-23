from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.lifecycle import unix_timestamp
from app.models.user import Base


class RunQueue(Base):
    __tablename__ = "run_queue"
    __table_args__ = (
        CheckConstraint("run_type IN ('api', 'web')", name="ck_run_queue_run_type_allowed"),
        CheckConstraint(
            "target_type IN ('test_case', 'test_suite')",
            name="ck_run_queue_target_type_allowed",
        ),
        CheckConstraint(
            "status IN ('queued', 'running', 'success', 'failed', 'error', 'canceled')",
            name="ck_run_queue_status_allowed",
        ),
        CheckConstraint("priority >= 1 AND priority <= 10", name="ck_run_queue_priority_range"),
        CheckConstraint(
            "scheduled_by IN ('manual', 'scheduler', 'ci')",
            name="ck_run_queue_scheduled_by_allowed",
        ),
        CheckConstraint(
            "started_at IS NULL OR started_at >= 0",
            name="ck_run_queue_started_at_non_negative",
        ),
        CheckConstraint(
            "finished_at IS NULL OR finished_at >= 0",
            name="ck_run_queue_finished_at_non_negative",
        ),
        CheckConstraint("created_at >= 0", name="ck_run_queue_created_at_non_negative"),
        CheckConstraint(
            "finished_at IS NULL OR started_at IS NULL OR finished_at >= started_at",
            name="ck_run_queue_finished_after_started",
        ),
        Index("ix_run_queue_project_status_created_at", "project_id", "status", "created_at"),
        Index("ix_run_queue_project_run_type", "project_id", "run_type"),
    )

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)

    # run_type: api | web
    run_type = Column(String(20), nullable=False, index=True)

    # target_type: test_case | test_suite
    target_type = Column(String(50), nullable=False)
    target_id = Column(Integer, nullable=False, index=True)

    # status: queued | running | success | failed | error | canceled
    status = Column(String(20), nullable=False, index=True, default="queued")
    priority = Column(Integer, nullable=False, default=5)

    # payload: JSON string for run parameters (env, dataset, overrides, etc.)
    payload = Column(Text, nullable=True)

    # scheduled_by: manual | scheduler | ci
    scheduled_by = Column(String(20), nullable=False, default="manual")

    worker_id = Column(String(100), nullable=True, index=True)
    started_at = Column(Integer, nullable=True)
    finished_at = Column(Integer, nullable=True)
    created_at = Column(Integer, nullable=False, default=unix_timestamp)

    project = relationship("Project", back_populates="run_queue_items")
