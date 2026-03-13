from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.lifecycle import unix_timestamp
from app.models.user import Base


class ApiTestSuiteCase(Base):
    __tablename__ = "api_test_suite_cases"
    __table_args__ = (
        UniqueConstraint("suite_id", "test_case_id", name="uq_api_test_suite_cases_suite_case"),
        UniqueConstraint("suite_id", "order_index", name="uq_api_test_suite_cases_suite_order"),
        CheckConstraint("order_index >= 0", name="ck_api_test_suite_cases_order_non_negative"),
        CheckConstraint("created_at >= 0", name="ck_api_test_suite_cases_created_at_non_negative"),
        Index("ix_api_test_suite_cases_suite_id", "suite_id"),
        Index("ix_api_test_suite_cases_test_case_id", "test_case_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    suite_id = Column(Integer, ForeignKey("api_test_suites.id", ondelete="CASCADE"), nullable=False)
    test_case_id = Column(Integer, ForeignKey("api_test_cases.id", ondelete="CASCADE"), nullable=False)
    order_index = Column(Integer, nullable=False, default=0)
    created_at = Column(Integer, nullable=False, default=unix_timestamp)

    suite = relationship("ApiTestSuite", back_populates="cases")
    test_case = relationship("ApiTestCase", back_populates="suite_links")
