from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.lifecycle import unix_timestamp
from app.models.user import Base


class ExecutionJob(Base):
    __tablename__ = "execution_jobs"
    __table_args__ = (
        CheckConstraint("attempt_no >= 1", name="ck_execution_jobs_attempt_no_positive"),
        CheckConstraint("executor_type IN ('api', 'web')", name="ck_execution_jobs_executor_type_allowed"),
        CheckConstraint(
            "status IN ('running', 'success', 'failed', 'error', 'canceled')",
            name="ck_execution_jobs_status_allowed",
        ),
        CheckConstraint(
            "started_at IS NULL OR started_at >= 0",
            name="ck_execution_jobs_started_at_non_negative",
        ),
        CheckConstraint(
            "finished_at IS NULL OR finished_at >= 0",
            name="ck_execution_jobs_finished_at_non_negative",
        ),
        CheckConstraint("created_at >= 0", name="ck_execution_jobs_created_at_non_negative"),
        CheckConstraint(
            "finished_at IS NULL OR started_at IS NULL OR finished_at >= started_at",
            name="ck_execution_jobs_finished_after_started",
        ),
        Index("ix_execution_jobs_task_status", "task_id", "status"),
    )

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("execution_tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    attempt_no = Column(Integer, nullable=False, default=1)
    executor_type = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, default="running")
    output_json = Column(Text, nullable=True)
    error_code = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(Integer, nullable=True)
    finished_at = Column(Integer, nullable=True)
    created_at = Column(Integer, nullable=False, default=unix_timestamp)

    task = relationship("ExecutionTask", back_populates="jobs")
