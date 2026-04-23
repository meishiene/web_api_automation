from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship

from app.models.lifecycle import unix_timestamp
from app.models.user import Base


class WebBatchRun(Base):
    __tablename__ = "web_batch_runs"
    __table_args__ = (
        CheckConstraint("status IN ('queued', 'running', 'success', 'failed', 'error')", name="ck_web_batch_runs_status_allowed"),
        CheckConstraint("total_cases >= 0", name="ck_web_batch_runs_total_non_negative"),
        CheckConstraint("passed_cases >= 0", name="ck_web_batch_runs_passed_non_negative"),
        CheckConstraint("failed_cases >= 0", name="ck_web_batch_runs_failed_non_negative"),
        CheckConstraint("error_cases >= 0", name="ck_web_batch_runs_error_non_negative"),
        CheckConstraint("started_at IS NULL OR started_at >= 0", name="ck_web_batch_runs_started_at_non_negative"),
        CheckConstraint("finished_at IS NULL OR finished_at >= 0", name="ck_web_batch_runs_finished_at_non_negative"),
        CheckConstraint("created_at >= 0", name="ck_web_batch_runs_created_at_non_negative"),
        Index("ix_web_batch_runs_project_id_created_at", "project_id", "created_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    triggered_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(20), nullable=False, default="queued")
    total_cases = Column(Integer, nullable=False, default=0)
    passed_cases = Column(Integer, nullable=False, default=0)
    failed_cases = Column(Integer, nullable=False, default=0)
    error_cases = Column(Integer, nullable=False, default=0)
    started_at = Column(Integer, nullable=True)
    finished_at = Column(Integer, nullable=True)
    created_at = Column(Integer, nullable=False, default=unix_timestamp)

    project = relationship("Project", back_populates="web_batch_runs")
    trigger_user = relationship("User", back_populates="triggered_web_batch_runs")
    items = relationship("WebBatchRunItem", back_populates="batch_run", cascade="all, delete-orphan")
