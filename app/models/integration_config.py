from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.lifecycle import unix_timestamp
from app.models.user import Base


class IntegrationConfig(Base):
    __tablename__ = "integration_configs"
    __table_args__ = (
        UniqueConstraint("project_id", "name", name="uq_integration_configs_project_name"),
        CheckConstraint("length(trim(name)) > 0", name="ck_integration_configs_name_not_blank"),
        CheckConstraint(
            "integration_type IN ('cicd', 'notification', 'defect', 'identity', 'webhook')",
            name="ck_integration_configs_type_allowed",
        ),
        CheckConstraint("length(trim(provider)) > 0", name="ck_integration_configs_provider_not_blank"),
        CheckConstraint("is_enabled IN (0, 1)", name="ck_integration_configs_is_enabled_bool"),
        CheckConstraint("created_at >= 0", name="ck_integration_configs_created_at_non_negative"),
        CheckConstraint("updated_at >= 0", name="ck_integration_configs_updated_at_non_negative"),
        Index("ix_integration_configs_project_id", "project_id"),
        Index("ix_integration_configs_project_type", "project_id", "integration_type"),
        Index("ix_integration_configs_project_enabled", "project_id", "is_enabled"),
    )

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    integration_type = Column(String(20), nullable=False)
    provider = Column(String(100), nullable=False)
    base_url = Column(String(500), nullable=True)
    credential_ref = Column(String(200), nullable=True)
    credential_value = Column(Text, nullable=True)
    config_json = Column(Text, nullable=True)
    is_enabled = Column(Integer, nullable=False, default=1)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(Integer, nullable=False, default=unix_timestamp)
    updated_at = Column(Integer, nullable=False, default=unix_timestamp, onupdate=unix_timestamp)

    project = relationship("Project", back_populates="integration_configs")
