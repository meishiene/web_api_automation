"""phase6 integration event inbox

Revision ID: 9c4e7a1d2f6b
Revises: 6a9d4c2e1b7f
Create Date: 2026-03-17 22:10:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9c4e7a1d2f6b"
down_revision = "6a9d4c2e1b7f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "integration_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("integration_config_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("direction", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("headers_json", sa.Text(), nullable=True),
        sa.Column("signature", sa.String(length=255), nullable=True),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column("max_attempts", sa.Integer(), nullable=False),
        sa.Column("next_retry_at", sa.Integer(), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("last_processed_at", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.Integer(), nullable=False),
        sa.CheckConstraint("length(trim(event_type)) > 0", name="ck_integration_events_event_type_not_blank"),
        sa.CheckConstraint("direction IN ('inbound', 'outbound')", name="ck_integration_events_direction_allowed"),
        sa.CheckConstraint(
            "status IN ('received', 'processed', 'retry_pending', 'failed')",
            name="ck_integration_events_status_allowed",
        ),
        sa.CheckConstraint("attempt_count >= 0", name="ck_integration_events_attempt_count_non_negative"),
        sa.CheckConstraint("max_attempts >= 1", name="ck_integration_events_max_attempts_positive"),
        sa.CheckConstraint("created_at >= 0", name="ck_integration_events_created_at_non_negative"),
        sa.CheckConstraint("updated_at >= 0", name="ck_integration_events_updated_at_non_negative"),
        sa.ForeignKeyConstraint(["integration_config_id"], ["integration_configs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "integration_config_id",
            "idempotency_key",
            name="uq_integration_events_config_idempotency",
        ),
    )
    op.create_index("ix_integration_events_id", "integration_events", ["id"], unique=False)
    op.create_index("ix_integration_events_project_id", "integration_events", ["project_id"], unique=False)
    op.create_index("ix_integration_events_config_id", "integration_events", ["integration_config_id"], unique=False)
    op.create_index(
        "ix_integration_events_project_status",
        "integration_events",
        ["project_id", "status"],
        unique=False,
    )
    op.create_index("ix_integration_events_next_retry", "integration_events", ["next_retry_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_integration_events_next_retry", table_name="integration_events")
    op.drop_index("ix_integration_events_project_status", table_name="integration_events")
    op.drop_index("ix_integration_events_config_id", table_name="integration_events")
    op.drop_index("ix_integration_events_project_id", table_name="integration_events")
    op.drop_index("ix_integration_events_id", table_name="integration_events")
    op.drop_table("integration_events")
