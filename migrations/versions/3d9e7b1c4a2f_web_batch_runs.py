"""web_batch_runs

Revision ID: 3d9e7b1c4a2f
Revises: 2b7c4e1a9d0f
Create Date: 2026-04-17 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "3d9e7b1c4a2f"
down_revision: Union[str, Sequence[str], None] = "2b7c4e1a9d0f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "web_batch_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("triggered_by", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("total_cases", sa.Integer(), nullable=False),
        sa.Column("passed_cases", sa.Integer(), nullable=False),
        sa.Column("failed_cases", sa.Integer(), nullable=False),
        sa.Column("error_cases", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.Integer(), nullable=True),
        sa.Column("finished_at", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.CheckConstraint("status IN ('queued', 'running', 'success', 'failed', 'error')", name="ck_web_batch_runs_status_allowed"),
        sa.CheckConstraint("total_cases >= 0", name="ck_web_batch_runs_total_non_negative"),
        sa.CheckConstraint("passed_cases >= 0", name="ck_web_batch_runs_passed_non_negative"),
        sa.CheckConstraint("failed_cases >= 0", name="ck_web_batch_runs_failed_non_negative"),
        sa.CheckConstraint("error_cases >= 0", name="ck_web_batch_runs_error_non_negative"),
        sa.CheckConstraint("started_at IS NULL OR started_at >= 0", name="ck_web_batch_runs_started_at_non_negative"),
        sa.CheckConstraint("finished_at IS NULL OR finished_at >= 0", name="ck_web_batch_runs_finished_at_non_negative"),
        sa.CheckConstraint("created_at >= 0", name="ck_web_batch_runs_created_at_non_negative"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["triggered_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("web_batch_runs", schema=None) as batch_op:
        batch_op.create_index("ix_web_batch_runs_project_id_created_at", ["project_id", "created_at"], unique=False)

    op.create_table(
        "web_batch_run_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("batch_run_id", sa.Integer(), nullable=False),
        sa.Column("web_test_case_id", sa.Integer(), nullable=False),
        sa.Column("web_test_run_id", sa.Integer(), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.CheckConstraint("order_index >= 0", name="ck_web_batch_run_items_order_non_negative"),
        sa.CheckConstraint("status IN ('success', 'failed', 'error')", name="ck_web_batch_run_items_status_allowed"),
        sa.CheckConstraint("created_at >= 0", name="ck_web_batch_run_items_created_at_non_negative"),
        sa.ForeignKeyConstraint(["batch_run_id"], ["web_batch_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["web_test_case_id"], ["web_test_cases.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["web_test_run_id"], ["web_test_runs.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("batch_run_id", "order_index", name="uq_web_batch_run_items_batch_order"),
    )
    with op.batch_alter_table("web_batch_run_items", schema=None) as batch_op:
        batch_op.create_index("ix_web_batch_run_items_batch_run_id", ["batch_run_id"], unique=False)
        batch_op.create_index("ix_web_batch_run_items_web_test_case_id", ["web_test_case_id"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("web_batch_run_items", schema=None) as batch_op:
        batch_op.drop_index("ix_web_batch_run_items_web_test_case_id")
        batch_op.drop_index("ix_web_batch_run_items_batch_run_id")
    op.drop_table("web_batch_run_items")

    with op.batch_alter_table("web_batch_runs", schema=None) as batch_op:
        batch_op.drop_index("ix_web_batch_runs_project_id_created_at")
    op.drop_table("web_batch_runs")
