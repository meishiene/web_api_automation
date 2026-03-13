from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.lifecycle import unix_timestamp
from app.models.user import Base


class ApiBatchRunItem(Base):
    __tablename__ = "api_batch_run_items"
    __table_args__ = (
        UniqueConstraint("batch_run_id", "order_index", name="uq_api_batch_run_items_batch_order"),
        CheckConstraint("order_index >= 0", name="ck_api_batch_run_items_order_non_negative"),
        CheckConstraint("status IN ('success', 'failed', 'error')", name="ck_api_batch_run_items_status_allowed"),
        CheckConstraint("created_at >= 0", name="ck_api_batch_run_items_created_at_non_negative"),
        Index("ix_api_batch_run_items_batch_run_id", "batch_run_id"),
        Index("ix_api_batch_run_items_test_case_id", "test_case_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    batch_run_id = Column(Integer, ForeignKey("api_batch_runs.id", ondelete="CASCADE"), nullable=False)
    test_case_id = Column(Integer, ForeignKey("api_test_cases.id", ondelete="CASCADE"), nullable=False)
    test_run_id = Column(Integer, ForeignKey("test_runs.id", ondelete="SET NULL"), nullable=True)
    order_index = Column(Integer, nullable=False, default=0)
    status = Column(String(20), nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(Integer, nullable=False, default=unix_timestamp)

    batch_run = relationship("ApiBatchRun", back_populates="items")
    test_case = relationship("ApiTestCase", back_populates="batch_run_items")
    test_run = relationship("TestRun", back_populates="batch_run_items")
