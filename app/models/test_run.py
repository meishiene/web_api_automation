from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.lifecycle import unix_timestamp
from app.models.user import Base


class TestRun(Base):
    __tablename__ = "test_runs"
    __table_args__ = (
        CheckConstraint(
            "status IN ('success', 'failed', 'error')",
            name="ck_test_runs_status_allowed",
        ),
        CheckConstraint(
            "actual_status IS NULL OR (actual_status >= 100 AND actual_status < 600)",
            name="ck_test_runs_actual_status_range",
        ),
        CheckConstraint(
            "duration_ms IS NULL OR duration_ms >= 0",
            name="ck_test_runs_duration_non_negative",
        ),
        CheckConstraint("created_at >= 0", name="ck_test_runs_created_at_non_negative"),
        Index("ix_test_runs_test_case_id", "test_case_id"),
        Index("ix_test_runs_test_case_id_created_at", "test_case_id", "created_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    test_case_id = Column(Integer, ForeignKey("api_test_cases.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), nullable=False)
    actual_status = Column(Integer)
    actual_body = Column(Text)
    error_message = Column(Text)
    duration_ms = Column(Integer)
    created_at = Column(Integer, nullable=False, default=unix_timestamp)

    test_case = relationship("ApiTestCase", back_populates="test_runs")
    batch_run_items = relationship("ApiBatchRunItem", back_populates="test_run")
