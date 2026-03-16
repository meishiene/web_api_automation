"""phase3_web_test_runs

Revision ID: 11eb5f289eaf
Revises: adeb808fa0e9
Create Date: 2026-03-16 00:00:01.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "11eb5f289eaf"
down_revision: Union[str, Sequence[str], None] = "adeb808fa0e9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "web_test_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("web_test_case_id", sa.Integer(), nullable=False),
        sa.Column("triggered_by", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("artifact_dir", sa.String(length=500), nullable=True),
        sa.Column("artifacts_json", sa.Text(), nullable=True),
        sa.Column("step_logs_json", sa.Text(), nullable=True),
        sa.Column("started_at", sa.Integer(), nullable=True),
        sa.Column("finished_at", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "status IN ('running', 'success', 'failed', 'error')",
            name="ck_web_test_runs_status_allowed",
        ),
        sa.CheckConstraint(
            "duration_ms IS NULL OR duration_ms >= 0",
            name="ck_web_test_runs_duration_non_negative",
        ),
        sa.CheckConstraint(
            "started_at IS NULL OR started_at >= 0",
            name="ck_web_test_runs_started_at_non_negative",
        ),
        sa.CheckConstraint(
            "finished_at IS NULL OR finished_at >= 0",
            name="ck_web_test_runs_finished_at_non_negative",
        ),
        sa.CheckConstraint("created_at >= 0", name="ck_web_test_runs_created_at_non_negative"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["triggered_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["web_test_case_id"], ["web_test_cases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("web_test_runs", schema=None) as batch_op:
        batch_op.create_index("ix_web_test_runs_project_id", ["project_id"], unique=False)
        batch_op.create_index("ix_web_test_runs_web_test_case_id", ["web_test_case_id"], unique=False)
        batch_op.create_index("ix_web_test_runs_project_id_created_at", ["project_id", "created_at"], unique=False)


def downgrade() -> None:
    op.drop_table("web_test_runs")

