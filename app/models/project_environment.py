from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.lifecycle import unix_timestamp
from app.models.user import Base


class ProjectEnvironment(Base):
    __tablename__ = "project_environments"
    __table_args__ = (
        UniqueConstraint("project_id", "name", name="uq_project_environments_project_name"),
        CheckConstraint("length(trim(name)) > 0", name="ck_project_environments_name_not_blank"),
        CheckConstraint("created_at >= 0", name="ck_project_environments_created_at_non_negative"),
        CheckConstraint("updated_at >= 0", name="ck_project_environments_updated_at_non_negative"),
        Index("ix_project_environments_project_id", "project_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(Integer, nullable=False, default=unix_timestamp)
    updated_at = Column(Integer, nullable=False, default=unix_timestamp, onupdate=unix_timestamp)

    project = relationship("Project", back_populates="environments")
    creator = relationship("User", back_populates="created_environments")
    variables = relationship("EnvironmentVariable", back_populates="environment", cascade="all, delete-orphan")
    batch_runs = relationship("ApiBatchRun", back_populates="environment")
