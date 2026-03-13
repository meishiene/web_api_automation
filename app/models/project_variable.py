from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.lifecycle import unix_timestamp
from app.models.user import Base


class ProjectVariable(Base):
    __tablename__ = "project_variables"
    __table_args__ = (
        UniqueConstraint("project_id", "key", name="uq_project_variables_project_key"),
        CheckConstraint("length(trim(key)) > 0", name="ck_project_variables_key_not_blank"),
        CheckConstraint("is_secret IN (0, 1)", name="ck_project_variables_is_secret_bool"),
        CheckConstraint("created_at >= 0", name="ck_project_variables_created_at_non_negative"),
        CheckConstraint("updated_at >= 0", name="ck_project_variables_updated_at_non_negative"),
        Index("ix_project_variables_project_id", "project_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    key = Column(String(100), nullable=False)
    value = Column(Text, nullable=False)
    is_secret = Column(Integer, nullable=False, default=0)
    created_at = Column(Integer, nullable=False, default=unix_timestamp)
    updated_at = Column(Integer, nullable=False, default=unix_timestamp, onupdate=unix_timestamp)

    project = relationship("Project", back_populates="project_variables")
