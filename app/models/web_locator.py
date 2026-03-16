from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.lifecycle import unix_timestamp
from app.models.user import Base


class WebLocator(Base):
    __tablename__ = "web_locators"
    __table_args__ = (
        UniqueConstraint("project_id", "name", name="uq_web_locators_project_id_name"),
        CheckConstraint("length(trim(name)) > 0", name="ck_web_locators_name_not_blank"),
        CheckConstraint("length(trim(selector)) > 0", name="ck_web_locators_selector_not_blank"),
        CheckConstraint(
            "strategy IN ('css', 'xpath', 'text', 'role', 'testid')",
            name="ck_web_locators_strategy_allowed",
        ),
        CheckConstraint("created_at >= 0", name="ck_web_locators_created_at_non_negative"),
        CheckConstraint("updated_at >= 0", name="ck_web_locators_updated_at_non_negative"),
        Index("ix_web_locators_project_id", "project_id"),
        Index("ix_web_locators_project_id_updated_at", "project_id", "updated_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    strategy = Column(String(20), nullable=False, default="css")
    selector = Column(String(500), nullable=False)
    description = Column(String(500), nullable=True)
    created_at = Column(Integer, nullable=False, default=unix_timestamp)
    updated_at = Column(Integer, nullable=False, default=unix_timestamp, onupdate=unix_timestamp)

    project = relationship("Project", back_populates="web_locators")

