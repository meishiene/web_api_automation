"""phase4 worker heartbeat minimal loop

Revision ID: 2c1b7f9a4d10
Revises: f2a1c4d8b9e3
Create Date: 2026-03-16 22:40:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2c1b7f9a4d10"
down_revision = "f2a1c4d8b9e3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "worker_heartbeats",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("worker_id", sa.String(length=100), nullable=False),
        sa.Column("run_type", sa.String(length=20), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("current_queue_item_id", sa.Integer(), nullable=True),
        sa.Column("last_heartbeat_at", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "run_type IS NULL OR run_type IN ('api', 'web')",
            name="ck_worker_heartbeats_run_type_allowed",
        ),
        sa.CheckConstraint(
            "status IN ('online', 'busy', 'offline')",
            name="ck_worker_heartbeats_status_allowed",
        ),
        sa.CheckConstraint(
            "last_heartbeat_at >= 0",
            name="ck_worker_heartbeats_last_heartbeat_at_non_negative",
        ),
        sa.CheckConstraint(
            "created_at >= 0",
            name="ck_worker_heartbeats_created_at_non_negative",
        ),
        sa.CheckConstraint(
            "updated_at >= 0",
            name="ck_worker_heartbeats_updated_at_non_negative",
        ),
        sa.ForeignKeyConstraint(["current_queue_item_id"], ["run_queue.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "worker_id", name="uq_worker_heartbeats_project_worker"),
    )
    op.create_index("ix_worker_heartbeats_id", "worker_heartbeats", ["id"], unique=False)
    op.create_index("ix_worker_heartbeats_project_id", "worker_heartbeats", ["project_id"], unique=False)
    op.create_index("ix_worker_heartbeats_worker_id", "worker_heartbeats", ["worker_id"], unique=False)
    op.create_index("ix_worker_heartbeats_run_type", "worker_heartbeats", ["run_type"], unique=False)
    op.create_index(
        "ix_worker_heartbeats_project_status_last_heartbeat",
        "worker_heartbeats",
        ["project_id", "status", "last_heartbeat_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_worker_heartbeats_project_status_last_heartbeat", table_name="worker_heartbeats")
    op.drop_index("ix_worker_heartbeats_run_type", table_name="worker_heartbeats")
    op.drop_index("ix_worker_heartbeats_worker_id", table_name="worker_heartbeats")
    op.drop_index("ix_worker_heartbeats_project_id", table_name="worker_heartbeats")
    op.drop_index("ix_worker_heartbeats_id", table_name="worker_heartbeats")
    op.drop_table("worker_heartbeats")
