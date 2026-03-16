from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.lifecycle import unix_timestamp
from app.models.user import Base


class WebTestRun(Base):
    __tablename__ = "web_test_runs"
    __table_args__ = (
        CheckConstraint(
            "status IN ('running', 'success', 'failed', 'error')",
            name="ck_web_test_runs_status_allowed",
        ),
        CheckConstraint(
            "duration_ms IS NULL OR duration_ms >= 0",
            name="ck_web_test_runs_duration_non_negative",
        ),
        CheckConstraint(
            "started_at IS NULL OR started_at >= 0",
            name="ck_web_test_runs_started_at_non_negative",
        ),
        CheckConstraint(
            "finished_at IS NULL OR finished_at >= 0",
            name="ck_web_test_runs_finished_at_non_negative",
        ),
        CheckConstraint("created_at >= 0", name="ck_web_test_runs_created_at_non_negative"),
        Index("ix_web_test_runs_project_id", "project_id"),
        Index("ix_web_test_runs_web_test_case_id", "web_test_case_id"),
        Index("ix_web_test_runs_project_id_created_at", "project_id", "created_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    web_test_case_id = Column(Integer, ForeignKey("web_test_cases.id", ondelete="CASCADE"), nullable=False)
    triggered_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(20), nullable=False, default="running")
    error_message = Column(Text, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    artifact_dir = Column(String(500), nullable=True)
    artifacts_json = Column(Text, nullable=True)
    step_logs_json = Column(Text, nullable=True)
    started_at = Column(Integer, nullable=True)
    finished_at = Column(Integer, nullable=True)
    created_at = Column(Integer, nullable=False, default=unix_timestamp)

    project = relationship("Project", back_populates="web_test_runs")
    web_test_case = relationship("WebTestCase", back_populates="web_test_runs")
    triggered_user = relationship("User")

