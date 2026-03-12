from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.lifecycle import unix_timestamp
from app.models.user import Base


class ApiTestCase(Base):
    __tablename__ = "api_test_cases"
    __table_args__ = (
        UniqueConstraint("project_id", "name", name="uq_api_test_cases_project_id_name"),
        CheckConstraint("length(trim(name)) > 0", name="ck_api_test_cases_name_not_blank"),
        CheckConstraint("length(trim(url)) > 0", name="ck_api_test_cases_url_not_blank"),
        CheckConstraint(
            "method IN ('GET', 'POST', 'PUT', 'PATCH', 'DELETE')",
            name="ck_api_test_cases_method_allowed",
        ),
        CheckConstraint(
            "expected_status >= 100 AND expected_status < 600",
            name="ck_api_test_cases_expected_status_range",
        ),
        CheckConstraint("created_at >= 0", name="ck_api_test_cases_created_at_non_negative"),
        CheckConstraint("updated_at >= 0", name="ck_api_test_cases_updated_at_non_negative"),
        Index("ix_api_test_cases_project_id", "project_id"),
        Index("ix_api_test_cases_project_id_updated_at", "project_id", "updated_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    method = Column(String(10), nullable=False)  # GET, POST, PUT, DELETE
    url = Column(String(500), nullable=False)
    headers = Column(Text)  # JSON string
    body = Column(Text)      # JSON string
    expected_status = Column(Integer, nullable=False, default=200)
    expected_body = Column(Text)  # JSON string, optional
    created_at = Column(Integer, nullable=False, default=unix_timestamp)
    updated_at = Column(Integer, nullable=False, default=unix_timestamp, onupdate=unix_timestamp)

    project = relationship("Project", back_populates="test_cases")
    test_runs = relationship("TestRun", back_populates="test_case", cascade="all, delete-orphan")
