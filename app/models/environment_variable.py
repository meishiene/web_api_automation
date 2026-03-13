from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.lifecycle import unix_timestamp
from app.models.user import Base


class EnvironmentVariable(Base):
    __tablename__ = "environment_variables"
    __table_args__ = (
        UniqueConstraint("environment_id", "key", name="uq_environment_variables_env_key"),
        CheckConstraint("length(trim(key)) > 0", name="ck_environment_variables_key_not_blank"),
        CheckConstraint("is_secret IN (0, 1)", name="ck_environment_variables_is_secret_bool"),
        CheckConstraint("created_at >= 0", name="ck_environment_variables_created_at_non_negative"),
        CheckConstraint("updated_at >= 0", name="ck_environment_variables_updated_at_non_negative"),
        Index("ix_environment_variables_environment_id", "environment_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    environment_id = Column(Integer, ForeignKey("project_environments.id", ondelete="CASCADE"), nullable=False)
    key = Column(String(100), nullable=False)
    value = Column(Text, nullable=False)
    is_secret = Column(Integer, nullable=False, default=0)
    created_at = Column(Integer, nullable=False, default=unix_timestamp)
    updated_at = Column(Integer, nullable=False, default=unix_timestamp, onupdate=unix_timestamp)

    environment = relationship("ProjectEnvironment", back_populates="variables")
