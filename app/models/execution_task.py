from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.lifecycle import unix_timestamp
from app.models.user import Base


class ExecutionTask(Base):
    __tablename__ = "execution_tasks"
    __table_args__ = (
        CheckConstraint("run_type IN ('api', 'web')", name="ck_execution_tasks_run_type_allowed"),
        CheckConstraint(
            "target_type IN ('test_case', 'test_suite')",
            name="ck_execution_tasks_target_type_allowed",
        ),
        CheckConstraint(
            "status IN ('queued', 'running', 'success', 'failed', 'error', 'canceled')",
            name="ck_execution_tasks_status_allowed",
        ),
        CheckConstraint(
            "trigger_mode IN ('manual', 'scheduler', 'ci')",
            name="ck_execution_tasks_trigger_mode_allowed",
        ),
        CheckConstraint(
            "started_at IS NULL OR started_at >= 0",
            name="ck_execution_tasks_started_at_non_negative",
        ),
        CheckConstraint(
            "finished_at IS NULL OR finished_at >= 0",
            name="ck_execution_tasks_finished_at_non_negative",
        ),
        CheckConstraint("created_at >= 0", name="ck_execution_tasks_created_at_non_negative"),
        CheckConstraint("updated_at >= 0", name="ck_execution_tasks_updated_at_non_negative"),
        CheckConstraint(
            "finished_at IS NULL OR started_at IS NULL OR finished_at >= started_at",
            name="ck_execution_tasks_finished_after_started",
        ),
        Index("ix_execution_tasks_project_status_created_at", "project_id", "status", "created_at"),
        Index("ix_execution_tasks_project_run_type", "project_id", "run_type"),
        Index("ix_execution_tasks_target", "target_type", "target_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    run_type = Column(String(20), nullable=False, index=True)
    target_type = Column(String(50), nullable=False)
    target_id = Column(Integer, nullable=False, index=True)
    status = Column(String(20), nullable=False, default="queued", index=True)
    trigger_mode = Column(String(20), nullable=False, default="manual")
    queue_item_id = Column(Integer, ForeignKey("run_queue.id", ondelete="SET NULL"), nullable=True, index=True)
    context_json = Column(Text, nullable=True)
    error_code = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(Integer, nullable=True)
    finished_at = Column(Integer, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(Integer, nullable=False, default=unix_timestamp)
    updated_at = Column(Integer, nullable=False, default=unix_timestamp, onupdate=unix_timestamp)

    project = relationship("Project", back_populates="execution_tasks")
    jobs = relationship("ExecutionJob", back_populates="task", cascade="all, delete-orphan")
    creator = relationship("User", back_populates="execution_tasks_created")
