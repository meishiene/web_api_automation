from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.lifecycle import unix_timestamp
from app.models.user import Base


class IdentityProviderBinding(Base):
    __tablename__ = "identity_provider_bindings"
    __table_args__ = (
        UniqueConstraint("provider", "external_subject", name="uq_identity_binding_provider_subject"),
        UniqueConstraint("provider", "user_id", name="uq_identity_binding_provider_user"),
        CheckConstraint("length(trim(provider)) > 0", name="ck_identity_binding_provider_not_blank"),
        CheckConstraint("length(trim(external_subject)) > 0", name="ck_identity_binding_subject_not_blank"),
        CheckConstraint("created_at >= 0", name="ck_identity_binding_created_at_non_negative"),
        CheckConstraint("updated_at >= 0", name="ck_identity_binding_updated_at_non_negative"),
        Index("ix_identity_binding_project_id", "project_id"),
        Index("ix_identity_binding_config_id", "integration_config_id"),
        Index("ix_identity_binding_user_id", "user_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    integration_config_id = Column(Integer, ForeignKey("integration_configs.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    external_subject = Column(String(255), nullable=False)
    external_email = Column(String(255), nullable=True)
    last_login_at = Column(Integer, nullable=True)
    created_at = Column(Integer, nullable=False, default=unix_timestamp)
    updated_at = Column(Integer, nullable=False, default=unix_timestamp, onupdate=unix_timestamp)

    project = relationship("Project", back_populates="identity_provider_bindings")
    integration_config = relationship("IntegrationConfig", back_populates="identity_provider_bindings")
    user = relationship("User", back_populates="identity_provider_bindings")
