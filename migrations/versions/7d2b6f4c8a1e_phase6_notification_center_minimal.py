"""phase6 notification center minimal

Revision ID: 7d2b6f4c8a1e
Revises: 9c4e7a1d2f6b
Create Date: 2026-03-17 23:40:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7d2b6f4c8a1e"
down_revision = "9c4e7a1d2f6b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "notification_subscriptions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("channel_type", sa.String(length=20), nullable=False),
        sa.Column("destination", sa.String(length=500), nullable=False),
        sa.Column("is_enabled", sa.Integer(), nullable=False),
        sa.Column("max_attempts", sa.Integer(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.Integer(), nullable=False),
        sa.CheckConstraint("length(trim(name)) > 0", name="ck_notification_subscriptions_name_not_blank"),
        sa.CheckConstraint("length(trim(event_type)) > 0", name="ck_notification_subscriptions_event_type_not_blank"),
        sa.CheckConstraint(
            "channel_type IN ('webhook', 'email')",
            name="ck_notification_subscriptions_channel_type_allowed",
        ),
        sa.CheckConstraint("length(trim(destination)) > 0", name="ck_notification_subscriptions_destination_not_blank"),
        sa.CheckConstraint("is_enabled IN (0, 1)", name="ck_notification_subscriptions_is_enabled_bool"),
        sa.CheckConstraint("max_attempts >= 1", name="ck_notification_subscriptions_max_attempts_positive"),
        sa.CheckConstraint("created_at >= 0", name="ck_notification_subscriptions_created_at_non_negative"),
        sa.CheckConstraint("updated_at >= 0", name="ck_notification_subscriptions_updated_at_non_negative"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "name", name="uq_notification_subscriptions_project_name"),
    )
    op.create_index("ix_notification_subscriptions_id", "notification_subscriptions", ["id"], unique=False)
    op.create_index("ix_notification_subscriptions_project_id", "notification_subscriptions", ["project_id"], unique=False)
    op.create_index(
        "ix_notification_subscriptions_project_event",
        "notification_subscriptions",
        ["project_id", "event_type"],
        unique=False,
    )

    op.create_table(
        "notification_deliveries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("subscription_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("channel_type", sa.String(length=20), nullable=False),
        sa.Column("destination", sa.String(length=500), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column("max_attempts", sa.Integer(), nullable=False),
        sa.Column("next_retry_at", sa.Integer(), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("last_attempt_at", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.Integer(), nullable=False),
        sa.CheckConstraint("length(trim(event_type)) > 0", name="ck_notification_deliveries_event_type_not_blank"),
        sa.CheckConstraint(
            "channel_type IN ('webhook', 'email')",
            name="ck_notification_deliveries_channel_type_allowed",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'sent', 'retry_pending', 'dead_letter')",
            name="ck_notification_deliveries_status_allowed",
        ),
        sa.CheckConstraint("attempt_count >= 0", name="ck_notification_deliveries_attempt_count_non_negative"),
        sa.CheckConstraint("max_attempts >= 1", name="ck_notification_deliveries_max_attempts_positive"),
        sa.CheckConstraint("created_at >= 0", name="ck_notification_deliveries_created_at_non_negative"),
        sa.CheckConstraint("updated_at >= 0", name="ck_notification_deliveries_updated_at_non_negative"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["subscription_id"], ["notification_subscriptions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_notification_deliveries_id", "notification_deliveries", ["id"], unique=False)
    op.create_index("ix_notification_deliveries_project_id", "notification_deliveries", ["project_id"], unique=False)
    op.create_index("ix_notification_deliveries_subscription_id", "notification_deliveries", ["subscription_id"], unique=False)
    op.create_index(
        "ix_notification_deliveries_project_status",
        "notification_deliveries",
        ["project_id", "status"],
        unique=False,
    )
    op.create_index("ix_notification_deliveries_next_retry", "notification_deliveries", ["next_retry_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_notification_deliveries_next_retry", table_name="notification_deliveries")
    op.drop_index("ix_notification_deliveries_project_status", table_name="notification_deliveries")
    op.drop_index("ix_notification_deliveries_subscription_id", table_name="notification_deliveries")
    op.drop_index("ix_notification_deliveries_project_id", table_name="notification_deliveries")
    op.drop_index("ix_notification_deliveries_id", table_name="notification_deliveries")
    op.drop_table("notification_deliveries")

    op.drop_index("ix_notification_subscriptions_project_event", table_name="notification_subscriptions")
    op.drop_index("ix_notification_subscriptions_project_id", table_name="notification_subscriptions")
    op.drop_index("ix_notification_subscriptions_id", table_name="notification_subscriptions")
    op.drop_table("notification_subscriptions")
