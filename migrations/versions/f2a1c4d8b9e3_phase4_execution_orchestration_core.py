"""phase4 execution orchestration core

Revision ID: f2a1c4d8b9e3
Revises: 11eb5f289eaf
Create Date: 2026-03-16 20:50:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f2a1c4d8b9e3"
down_revision = "11eb5f289eaf"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "execution_tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("run_type", sa.String(length=20), nullable=False),
        sa.Column("target_type", sa.String(length=50), nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("trigger_mode", sa.String(length=20), nullable=False),
        sa.Column("queue_item_id", sa.Integer(), nullable=True),
        sa.Column("context_json", sa.Text(), nullable=True),
        sa.Column("error_code", sa.String(length=100), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.Integer(), nullable=True),
        sa.Column("finished_at", sa.Integer(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "run_type IN ('api', 'web')",
            name="ck_execution_tasks_run_type_allowed",
        ),
        sa.CheckConstraint(
            "target_type IN ('test_case', 'test_suite')",
            name="ck_execution_tasks_target_type_allowed",
        ),
        sa.CheckConstraint(
            "status IN ('queued', 'running', 'success', 'failed', 'error', 'canceled')",
            name="ck_execution_tasks_status_allowed",
        ),
        sa.CheckConstraint(
            "trigger_mode IN ('manual', 'scheduler', 'ci')",
            name="ck_execution_tasks_trigger_mode_allowed",
        ),
        sa.CheckConstraint(
            "started_at IS NULL OR started_at >= 0",
            name="ck_execution_tasks_started_at_non_negative",
        ),
        sa.CheckConstraint(
            "finished_at IS NULL OR finished_at >= 0",
            name="ck_execution_tasks_finished_at_non_negative",
        ),
        sa.CheckConstraint(
            "created_at >= 0",
            name="ck_execution_tasks_created_at_non_negative",
        ),
        sa.CheckConstraint(
            "updated_at >= 0",
            name="ck_execution_tasks_updated_at_non_negative",
        ),
        sa.CheckConstraint(
            "finished_at IS NULL OR started_at IS NULL OR finished_at >= started_at",
            name="ck_execution_tasks_finished_after_started",
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["queue_item_id"], ["run_queue.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_execution_tasks_id", "execution_tasks", ["id"], unique=False)
    op.create_index(
        "ix_execution_tasks_project_status_created_at",
        "execution_tasks",
        ["project_id", "status", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_execution_tasks_project_run_type",
        "execution_tasks",
        ["project_id", "run_type"],
        unique=False,
    )
    op.create_index(
        "ix_execution_tasks_target",
        "execution_tasks",
        ["target_type", "target_id"],
        unique=False,
    )
    op.create_index("ix_execution_tasks_project_id", "execution_tasks", ["project_id"], unique=False)
    op.create_index("ix_execution_tasks_run_type", "execution_tasks", ["run_type"], unique=False)
    op.create_index("ix_execution_tasks_status", "execution_tasks", ["status"], unique=False)
    op.create_index("ix_execution_tasks_target_id", "execution_tasks", ["target_id"], unique=False)
    op.create_index("ix_execution_tasks_queue_item_id", "execution_tasks", ["queue_item_id"], unique=False)
    op.create_index("ix_execution_tasks_created_by", "execution_tasks", ["created_by"], unique=False)

    op.create_table(
        "execution_jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("attempt_no", sa.Integer(), nullable=False),
        sa.Column("executor_type", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("output_json", sa.Text(), nullable=True),
        sa.Column("error_code", sa.String(length=100), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.Integer(), nullable=True),
        sa.Column("finished_at", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.CheckConstraint("attempt_no >= 1", name="ck_execution_jobs_attempt_no_positive"),
        sa.CheckConstraint(
            "executor_type IN ('api', 'web')",
            name="ck_execution_jobs_executor_type_allowed",
        ),
        sa.CheckConstraint(
            "status IN ('running', 'success', 'failed', 'error', 'canceled')",
            name="ck_execution_jobs_status_allowed",
        ),
        sa.CheckConstraint(
            "started_at IS NULL OR started_at >= 0",
            name="ck_execution_jobs_started_at_non_negative",
        ),
        sa.CheckConstraint(
            "finished_at IS NULL OR finished_at >= 0",
            name="ck_execution_jobs_finished_at_non_negative",
        ),
        sa.CheckConstraint(
            "created_at >= 0",
            name="ck_execution_jobs_created_at_non_negative",
        ),
        sa.CheckConstraint(
            "finished_at IS NULL OR started_at IS NULL OR finished_at >= started_at",
            name="ck_execution_jobs_finished_after_started",
        ),
        sa.ForeignKeyConstraint(["task_id"], ["execution_tasks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_execution_jobs_id", "execution_jobs", ["id"], unique=False)
    op.create_index("ix_execution_jobs_task_status", "execution_jobs", ["task_id", "status"], unique=False)
    op.create_index("ix_execution_jobs_task_id", "execution_jobs", ["task_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_execution_jobs_task_id", table_name="execution_jobs")
    op.drop_index("ix_execution_jobs_task_status", table_name="execution_jobs")
    op.drop_index("ix_execution_jobs_id", table_name="execution_jobs")
    op.drop_table("execution_jobs")

    op.drop_index("ix_execution_tasks_created_by", table_name="execution_tasks")
    op.drop_index("ix_execution_tasks_queue_item_id", table_name="execution_tasks")
    op.drop_index("ix_execution_tasks_target_id", table_name="execution_tasks")
    op.drop_index("ix_execution_tasks_status", table_name="execution_tasks")
    op.drop_index("ix_execution_tasks_run_type", table_name="execution_tasks")
    op.drop_index("ix_execution_tasks_project_id", table_name="execution_tasks")
    op.drop_index("ix_execution_tasks_target", table_name="execution_tasks")
    op.drop_index("ix_execution_tasks_project_run_type", table_name="execution_tasks")
    op.drop_index("ix_execution_tasks_project_status_created_at", table_name="execution_tasks")
    op.drop_index("ix_execution_tasks_id", table_name="execution_tasks")
    op.drop_table("execution_tasks")
