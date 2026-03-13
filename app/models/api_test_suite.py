from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.lifecycle import unix_timestamp
from app.models.user import Base


class ApiTestSuite(Base):
    __tablename__ = "api_test_suites"
    __table_args__ = (
        UniqueConstraint("project_id", "name", name="uq_api_test_suites_project_id_name"),
        CheckConstraint("length(trim(name)) > 0", name="ck_api_test_suites_name_not_blank"),
        CheckConstraint("created_at >= 0", name="ck_api_test_suites_created_at_non_negative"),
        CheckConstraint("updated_at >= 0", name="ck_api_test_suites_updated_at_non_negative"),
        Index("ix_api_test_suites_project_id", "project_id"),
        Index("ix_api_test_suites_project_id_updated_at", "project_id", "updated_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(Integer, nullable=False, default=unix_timestamp)
    updated_at = Column(Integer, nullable=False, default=unix_timestamp, onupdate=unix_timestamp)

    project = relationship("Project", back_populates="test_suites")
    creator = relationship("User", back_populates="created_test_suites")
    cases = relationship("ApiTestSuiteCase", back_populates="suite", cascade="all, delete-orphan")
    batch_runs = relationship("ApiBatchRun", back_populates="suite")
