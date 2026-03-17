from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.lifecycle import unix_timestamp
from app.models.user import Base


class NotificationSubscription(Base):
    __tablename__ = "notification_subscriptions"
    __table_args__ = (
        UniqueConstraint("project_id", "name", name="uq_notification_subscriptions_project_name"),
        CheckConstraint("length(trim(name)) > 0", name="ck_notification_subscriptions_name_not_blank"),
        CheckConstraint("length(trim(event_type)) > 0", name="ck_notification_subscriptions_event_type_not_blank"),
        CheckConstraint(
            "channel_type IN ('webhook', 'email')",
            name="ck_notification_subscriptions_channel_type_allowed",
        ),
        CheckConstraint("length(trim(destination)) > 0", name="ck_notification_subscriptions_destination_not_blank"),
        CheckConstraint("is_enabled IN (0, 1)", name="ck_notification_subscriptions_is_enabled_bool"),
        CheckConstraint("max_attempts >= 1", name="ck_notification_subscriptions_max_attempts_positive"),
        CheckConstraint("created_at >= 0", name="ck_notification_subscriptions_created_at_non_negative"),
        CheckConstraint("updated_at >= 0", name="ck_notification_subscriptions_updated_at_non_negative"),
        Index("ix_notification_subscriptions_project_id", "project_id"),
        Index("ix_notification_subscriptions_project_event", "project_id", "event_type"),
    )

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    event_type = Column(String(100), nullable=False)
    channel_type = Column(String(20), nullable=False)
    destination = Column(String(500), nullable=False)
    is_enabled = Column(Integer, nullable=False, default=1)
    max_attempts = Column(Integer, nullable=False, default=3)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(Integer, nullable=False, default=unix_timestamp)
    updated_at = Column(Integer, nullable=False, default=unix_timestamp, onupdate=unix_timestamp)

    project = relationship("Project", back_populates="notification_subscriptions")
    deliveries = relationship("NotificationDelivery", back_populates="subscription", cascade="all, delete-orphan")
