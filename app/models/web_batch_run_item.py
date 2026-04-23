from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.lifecycle import unix_timestamp
from app.models.user import Base


class WebBatchRunItem(Base):
    __tablename__ = "web_batch_run_items"
    __table_args__ = (
        UniqueConstraint("batch_run_id", "order_index", name="uq_web_batch_run_items_batch_order"),
        CheckConstraint("order_index >= 0", name="ck_web_batch_run_items_order_non_negative"),
        CheckConstraint("status IN ('success', 'failed', 'error')", name="ck_web_batch_run_items_status_allowed"),
        CheckConstraint("created_at >= 0", name="ck_web_batch_run_items_created_at_non_negative"),
        Index("ix_web_batch_run_items_batch_run_id", "batch_run_id"),
        Index("ix_web_batch_run_items_web_test_case_id", "web_test_case_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    batch_run_id = Column(Integer, ForeignKey("web_batch_runs.id", ondelete="CASCADE"), nullable=False)
    web_test_case_id = Column(Integer, ForeignKey("web_test_cases.id", ondelete="CASCADE"), nullable=False)
    web_test_run_id = Column(Integer, ForeignKey("web_test_runs.id", ondelete="SET NULL"), nullable=True)
    order_index = Column(Integer, nullable=False, default=0)
    status = Column(String(20), nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(Integer, nullable=False, default=unix_timestamp)

    batch_run = relationship("WebBatchRun", back_populates="items")
    web_test_case = relationship("WebTestCase", back_populates="web_batch_run_items")
    web_test_run = relationship("WebTestRun", back_populates="web_batch_run_items")
