from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.lifecycle import unix_timestamp
from app.models.user import Base


class WebStep(Base):
    __tablename__ = "web_steps"
    __table_args__ = (
        UniqueConstraint("web_test_case_id", "order_index", name="uq_web_steps_case_order"),
        CheckConstraint("order_index >= 0", name="ck_web_steps_order_index_non_negative"),
        CheckConstraint(
            "action IN ('open', 'click', 'input', 'wait', 'assert', 'screenshot')",
            name="ck_web_steps_action_allowed",
        ),
        CheckConstraint("created_at >= 0", name="ck_web_steps_created_at_non_negative"),
        CheckConstraint("updated_at >= 0", name="ck_web_steps_updated_at_non_negative"),
        Index("ix_web_steps_web_test_case_id", "web_test_case_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    web_test_case_id = Column(Integer, ForeignKey("web_test_cases.id", ondelete="CASCADE"), nullable=False)
    order_index = Column(Integer, nullable=False)
    action = Column(String(50), nullable=False)
    params_json = Column(Text, nullable=True)
    created_at = Column(Integer, nullable=False, default=unix_timestamp)
    updated_at = Column(Integer, nullable=False, default=unix_timestamp, onupdate=unix_timestamp)

    test_case = relationship("WebTestCase", back_populates="steps")

