from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.lifecycle import unix_timestamp
from app.models.user import Base


class WebTestCase(Base):
    __tablename__ = "web_test_cases"
    __table_args__ = (
        UniqueConstraint("project_id", "name", name="uq_web_test_cases_project_id_name"),
        CheckConstraint("length(trim(name)) > 0", name="ck_web_test_cases_name_not_blank"),
        CheckConstraint(
            "base_url IS NULL OR length(trim(base_url)) > 0",
            name="ck_web_test_cases_base_url_not_blank",
        ),
        CheckConstraint("created_at >= 0", name="ck_web_test_cases_created_at_non_negative"),
        CheckConstraint("updated_at >= 0", name="ck_web_test_cases_updated_at_non_negative"),
        Index("ix_web_test_cases_project_id", "project_id"),
        Index("ix_web_test_cases_project_id_updated_at", "project_id", "updated_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    base_url = Column(String(500), nullable=True)
    created_at = Column(Integer, nullable=False, default=unix_timestamp)
    updated_at = Column(Integer, nullable=False, default=unix_timestamp, onupdate=unix_timestamp)

    project = relationship("Project", back_populates="web_test_cases")
    steps = relationship(
        "WebStep",
        back_populates="test_case",
        cascade="all, delete-orphan",
        order_by="WebStep.order_index",
    )
    web_test_runs = relationship("WebTestRun", back_populates="web_test_case", cascade="all, delete-orphan")
