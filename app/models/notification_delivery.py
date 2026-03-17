from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.lifecycle import unix_timestamp
from app.models.user import Base


class NotificationDelivery(Base):
    __tablename__ = "notification_deliveries"
    __table_args__ = (
        CheckConstraint("length(trim(event_type)) > 0", name="ck_notification_deliveries_event_type_not_blank"),
        CheckConstraint(
            "channel_type IN ('webhook', 'email')",
            name="ck_notification_deliveries_channel_type_allowed",
        ),
        CheckConstraint(
            "status IN ('pending', 'sent', 'retry_pending', 'dead_letter')",
            name="ck_notification_deliveries_status_allowed",
        ),
        CheckConstraint("attempt_count >= 0", name="ck_notification_deliveries_attempt_count_non_negative"),
        CheckConstraint("max_attempts >= 1", name="ck_notification_deliveries_max_attempts_positive"),
        CheckConstraint("created_at >= 0", name="ck_notification_deliveries_created_at_non_negative"),
        CheckConstraint("updated_at >= 0", name="ck_notification_deliveries_updated_at_non_negative"),
        Index("ix_notification_deliveries_project_id", "project_id"),
        Index("ix_notification_deliveries_subscription_id", "subscription_id"),
        Index("ix_notification_deliveries_project_status", "project_id", "status"),
        Index("ix_notification_deliveries_next_retry", "next_retry_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("notification_subscriptions.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(100), nullable=False)
    channel_type = Column(String(20), nullable=False)
    destination = Column(String(500), nullable=False)
    payload_json = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    attempt_count = Column(Integer, nullable=False, default=0)
    max_attempts = Column(Integer, nullable=False, default=3)
    next_retry_at = Column(Integer, nullable=True)
    last_error = Column(Text, nullable=True)
    last_attempt_at = Column(Integer, nullable=True)
    created_at = Column(Integer, nullable=False, default=unix_timestamp)
    updated_at = Column(Integer, nullable=False, default=unix_timestamp, onupdate=unix_timestamp)

    subscription = relationship("NotificationSubscription", back_populates="deliveries")
    project = relationship("Project", back_populates="notification_deliveries")
