"""audit_log_governance

Revision ID: 802c16c9f78e
Revises: 01fcc228897e
Create Date: 2026-03-11 23:52:36.605895

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '802c16c9f78e'
down_revision: Union[str, Sequence[str], None] = '01fcc228897e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "audit_logs_archive",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("original_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("resource_type", sa.String(length=100), nullable=False),
        sa.Column("resource_id", sa.String(length=100), nullable=True),
        sa.Column("result", sa.String(length=20), nullable=False),
        sa.Column("request_id", sa.String(length=100), nullable=True),
        sa.Column("client_ip", sa.String(length=64), nullable=True),
        sa.Column("method", sa.String(length=10), nullable=False),
        sa.Column("path", sa.String(length=500), nullable=False),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.Column("archived_at", sa.Integer(), nullable=False),
        sa.CheckConstraint("result IN ('success', 'failed')", name="ck_audit_logs_archive_result_allowed"),
        sa.CheckConstraint("created_at >= 0", name="ck_audit_logs_archive_created_at_non_negative"),
        sa.CheckConstraint("archived_at >= 0", name="ck_audit_logs_archive_archived_at_non_negative"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("original_id", name="uq_audit_logs_archive_original_id"),
    )
    with op.batch_alter_table("audit_logs_archive", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_audit_logs_archive_id"), ["id"], unique=False)
        batch_op.create_index(batch_op.f("ix_audit_logs_archive_original_id"), ["original_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_audit_logs_archive_user_id"), ["user_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_audit_logs_archive_action"), ["action"], unique=False)
        batch_op.create_index(batch_op.f("ix_audit_logs_archive_request_id"), ["request_id"], unique=False)
        batch_op.create_index("ix_audit_logs_archive_action_created_at", ["action", "created_at"], unique=False)
        batch_op.create_index("ix_audit_logs_archive_user_created_at", ["user_id", "created_at"], unique=False)
        batch_op.create_index("ix_audit_logs_archive_archived_at", ["archived_at"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("audit_logs_archive", schema=None) as batch_op:
        batch_op.drop_index("ix_audit_logs_archive_archived_at")
        batch_op.drop_index("ix_audit_logs_archive_user_created_at")
        batch_op.drop_index("ix_audit_logs_archive_action_created_at")
        batch_op.drop_index(batch_op.f("ix_audit_logs_archive_request_id"))
        batch_op.drop_index(batch_op.f("ix_audit_logs_archive_action"))
        batch_op.drop_index(batch_op.f("ix_audit_logs_archive_user_id"))
        batch_op.drop_index(batch_op.f("ix_audit_logs_archive_original_id"))
        batch_op.drop_index(batch_op.f("ix_audit_logs_archive_id"))

    op.drop_table("audit_logs_archive")
