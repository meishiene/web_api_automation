from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.lifecycle import unix_timestamp
from app.models.user import Base


class IdentityOAuthSession(Base):
    __tablename__ = "identity_oauth_sessions"
    __table_args__ = (
        UniqueConstraint("state", name="uq_identity_oauth_sessions_state"),
        CheckConstraint("length(trim(provider)) > 0", name="ck_identity_oauth_sessions_provider_not_blank"),
        CheckConstraint("length(trim(state)) > 0", name="ck_identity_oauth_sessions_state_not_blank"),
        CheckConstraint("expires_at >= 0", name="ck_identity_oauth_sessions_expires_at_non_negative"),
        CheckConstraint("created_at >= 0", name="ck_identity_oauth_sessions_created_at_non_negative"),
        CheckConstraint("updated_at >= 0", name="ck_identity_oauth_sessions_updated_at_non_negative"),
        CheckConstraint("status IN ('pending', 'completed', 'expired')", name="ck_identity_oauth_sessions_status_allowed"),
        Index("ix_identity_oauth_sessions_project_id", "project_id"),
        Index("ix_identity_oauth_sessions_config_id", "integration_config_id"),
        Index("ix_identity_oauth_sessions_expires_at", "expires_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    integration_config_id = Column(Integer, ForeignKey("integration_configs.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(100), nullable=False)
    state = Column(String(128), nullable=False)
    redirect_uri = Column(String(500), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    expires_at = Column(Integer, nullable=False)
    requested_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    consumed_at = Column(Integer, nullable=True)
    created_at = Column(Integer, nullable=False, default=unix_timestamp)
    updated_at = Column(Integer, nullable=False, default=unix_timestamp, onupdate=unix_timestamp)

    project = relationship("Project", back_populates="identity_oauth_sessions")
    integration_config = relationship("IntegrationConfig", back_populates="identity_oauth_sessions")
