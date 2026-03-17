from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.lifecycle import unix_timestamp
from app.models.user import Base


class IntegrationEvent(Base):
    __tablename__ = "integration_events"
    __table_args__ = (
        UniqueConstraint(
            "integration_config_id",
            "idempotency_key",
            name="uq_integration_events_config_idempotency",
        ),
        CheckConstraint("length(trim(event_type)) > 0", name="ck_integration_events_event_type_not_blank"),
        CheckConstraint("direction IN ('inbound', 'outbound')", name="ck_integration_events_direction_allowed"),
        CheckConstraint(
            "status IN ('received', 'processed', 'retry_pending', 'failed')",
            name="ck_integration_events_status_allowed",
        ),
        CheckConstraint("attempt_count >= 0", name="ck_integration_events_attempt_count_non_negative"),
        CheckConstraint("max_attempts >= 1", name="ck_integration_events_max_attempts_positive"),
        CheckConstraint("created_at >= 0", name="ck_integration_events_created_at_non_negative"),
        CheckConstraint("updated_at >= 0", name="ck_integration_events_updated_at_non_negative"),
        Index("ix_integration_events_project_id", "project_id"),
        Index("ix_integration_events_config_id", "integration_config_id"),
        Index("ix_integration_events_project_status", "project_id", "status"),
        Index("ix_integration_events_next_retry", "next_retry_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    integration_config_id = Column(Integer, ForeignKey("integration_configs.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(100), nullable=False)
    direction = Column(String(20), nullable=False, default="inbound")
    status = Column(String(20), nullable=False, default="received")
    payload_json = Column(Text, nullable=False)
    headers_json = Column(Text, nullable=True)
    signature = Column(String(255), nullable=True)
    idempotency_key = Column(String(128), nullable=False)
    attempt_count = Column(Integer, nullable=False, default=0)
    max_attempts = Column(Integer, nullable=False, default=3)
    next_retry_at = Column(Integer, nullable=True)
    last_error = Column(Text, nullable=True)
    last_processed_at = Column(Integer, nullable=True)
    created_at = Column(Integer, nullable=False, default=unix_timestamp)
    updated_at = Column(Integer, nullable=False, default=unix_timestamp, onupdate=unix_timestamp)

    integration_config = relationship("IntegrationConfig", back_populates="events")
