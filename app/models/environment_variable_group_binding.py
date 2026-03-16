from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.lifecycle import unix_timestamp
from app.models.user import Base


class EnvironmentVariableGroupBinding(Base):
    __tablename__ = "environment_variable_group_bindings"
    __table_args__ = (
        UniqueConstraint("environment_id", "group_name", name="uq_env_variable_group_bindings_env_group"),
        CheckConstraint("length(trim(group_name)) > 0", name="ck_env_variable_group_bindings_group_not_blank"),
        CheckConstraint("created_at >= 0", name="ck_env_variable_group_bindings_created_non_negative"),
        CheckConstraint("updated_at >= 0", name="ck_env_variable_group_bindings_updated_non_negative"),
        Index("ix_env_variable_group_bindings_environment_id", "environment_id"),
        Index("ix_env_variable_group_bindings_group_name", "group_name"),
    )

    id = Column(Integer, primary_key=True, index=True)
    environment_id = Column(Integer, ForeignKey("project_environments.id", ondelete="CASCADE"), nullable=False)
    group_name = Column(String(100), nullable=False)
    created_at = Column(Integer, nullable=False, default=unix_timestamp)
    updated_at = Column(Integer, nullable=False, default=unix_timestamp, onupdate=unix_timestamp)

    environment = relationship("ProjectEnvironment", back_populates="variable_group_bindings")
