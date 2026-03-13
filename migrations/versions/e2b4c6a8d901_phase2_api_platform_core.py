"""phase2_api_platform_core

Revision ID: e2b4c6a8d901
Revises: d1f8902c4b61
Create Date: 2026-03-13 12:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e2b4c6a8d901"
down_revision: Union[str, Sequence[str], None] = "d1f8902c4b61"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("api_test_cases", schema=None) as batch_op:
        batch_op.add_column(sa.Column("assertion_rules", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("extraction_rules", sa.Text(), nullable=True))

    op.create_table(
        "api_test_suites",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "name", name="uq_api_test_suites_project_id_name"),
        sa.CheckConstraint("length(trim(name)) > 0", name="ck_api_test_suites_name_not_blank"),
        sa.CheckConstraint("created_at >= 0", name="ck_api_test_suites_created_at_non_negative"),
        sa.CheckConstraint("updated_at >= 0", name="ck_api_test_suites_updated_at_non_negative"),
    )
    op.create_index("ix_api_test_suites_project_id", "api_test_suites", ["project_id"], unique=False)
    op.create_index("ix_api_test_suites_project_id_updated_at", "api_test_suites", ["project_id", "updated_at"], unique=False)

    op.create_table(
        "api_test_suite_cases",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("suite_id", sa.Integer(), nullable=False),
        sa.Column("test_case_id", sa.Integer(), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["suite_id"], ["api_test_suites.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["test_case_id"], ["api_test_cases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("suite_id", "test_case_id", name="uq_api_test_suite_cases_suite_case"),
        sa.UniqueConstraint("suite_id", "order_index", name="uq_api_test_suite_cases_suite_order"),
        sa.CheckConstraint("order_index >= 0", name="ck_api_test_suite_cases_order_non_negative"),
        sa.CheckConstraint("created_at >= 0", name="ck_api_test_suite_cases_created_at_non_negative"),
    )
    op.create_index("ix_api_test_suite_cases_suite_id", "api_test_suite_cases", ["suite_id"], unique=False)
    op.create_index("ix_api_test_suite_cases_test_case_id", "api_test_suite_cases", ["test_case_id"], unique=False)

    op.create_table(
        "project_environments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "name", name="uq_project_environments_project_name"),
        sa.CheckConstraint("length(trim(name)) > 0", name="ck_project_environments_name_not_blank"),
        sa.CheckConstraint("created_at >= 0", name="ck_project_environments_created_at_non_negative"),
        sa.CheckConstraint("updated_at >= 0", name="ck_project_environments_updated_at_non_negative"),
    )
    op.create_index("ix_project_environments_project_id", "project_environments", ["project_id"], unique=False)

    op.create_table(
        "project_variables",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("is_secret", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "key", name="uq_project_variables_project_key"),
        sa.CheckConstraint("length(trim(key)) > 0", name="ck_project_variables_key_not_blank"),
        sa.CheckConstraint("is_secret IN (0, 1)", name="ck_project_variables_is_secret_bool"),
        sa.CheckConstraint("created_at >= 0", name="ck_project_variables_created_at_non_negative"),
        sa.CheckConstraint("updated_at >= 0", name="ck_project_variables_updated_at_non_negative"),
    )
    op.create_index("ix_project_variables_project_id", "project_variables", ["project_id"], unique=False)

    op.create_table(
        "environment_variables",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("environment_id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("is_secret", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["environment_id"], ["project_environments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("environment_id", "key", name="uq_environment_variables_env_key"),
        sa.CheckConstraint("length(trim(key)) > 0", name="ck_environment_variables_key_not_blank"),
        sa.CheckConstraint("is_secret IN (0, 1)", name="ck_environment_variables_is_secret_bool"),
        sa.CheckConstraint("created_at >= 0", name="ck_environment_variables_created_at_non_negative"),
        sa.CheckConstraint("updated_at >= 0", name="ck_environment_variables_updated_at_non_negative"),
    )
    op.create_index("ix_environment_variables_environment_id", "environment_variables", ["environment_id"], unique=False)

    op.create_table(
        "api_batch_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("suite_id", sa.Integer(), nullable=True),
        sa.Column("environment_id", sa.Integer(), nullable=True),
        sa.Column("triggered_by", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="queued"),
        sa.Column("total_cases", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("passed_cases", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failed_cases", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_cases", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("started_at", sa.Integer(), nullable=True),
        sa.Column("finished_at", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["environment_id"], ["project_environments.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["suite_id"], ["api_test_suites.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["triggered_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("status IN ('queued', 'running', 'success', 'failed', 'error')", name="ck_api_batch_runs_status_allowed"),
        sa.CheckConstraint("total_cases >= 0", name="ck_api_batch_runs_total_non_negative"),
        sa.CheckConstraint("passed_cases >= 0", name="ck_api_batch_runs_passed_non_negative"),
        sa.CheckConstraint("failed_cases >= 0", name="ck_api_batch_runs_failed_non_negative"),
        sa.CheckConstraint("error_cases >= 0", name="ck_api_batch_runs_error_non_negative"),
        sa.CheckConstraint("started_at IS NULL OR started_at >= 0", name="ck_api_batch_runs_started_at_non_negative"),
        sa.CheckConstraint("finished_at IS NULL OR finished_at >= 0", name="ck_api_batch_runs_finished_at_non_negative"),
        sa.CheckConstraint("created_at >= 0", name="ck_api_batch_runs_created_at_non_negative"),
    )
    op.create_index("ix_api_batch_runs_project_id_created_at", "api_batch_runs", ["project_id", "created_at"], unique=False)
    op.create_index("ix_api_batch_runs_suite_id", "api_batch_runs", ["suite_id"], unique=False)

    op.create_table(
        "api_batch_run_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("batch_run_id", sa.Integer(), nullable=False),
        sa.Column("test_case_id", sa.Integer(), nullable=False),
        sa.Column("test_run_id", sa.Integer(), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["batch_run_id"], ["api_batch_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["test_case_id"], ["api_test_cases.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["test_run_id"], ["test_runs.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("batch_run_id", "order_index", name="uq_api_batch_run_items_batch_order"),
        sa.CheckConstraint("order_index >= 0", name="ck_api_batch_run_items_order_non_negative"),
        sa.CheckConstraint("status IN ('success', 'failed', 'error')", name="ck_api_batch_run_items_status_allowed"),
        sa.CheckConstraint("created_at >= 0", name="ck_api_batch_run_items_created_at_non_negative"),
    )
    op.create_index("ix_api_batch_run_items_batch_run_id", "api_batch_run_items", ["batch_run_id"], unique=False)
    op.create_index("ix_api_batch_run_items_test_case_id", "api_batch_run_items", ["test_case_id"], unique=False)

    with op.batch_alter_table("api_test_suite_cases", schema=None) as batch_op:
        batch_op.alter_column("order_index", server_default=None)
    with op.batch_alter_table("project_variables", schema=None) as batch_op:
        batch_op.alter_column("is_secret", server_default=None)
    with op.batch_alter_table("environment_variables", schema=None) as batch_op:
        batch_op.alter_column("is_secret", server_default=None)
    with op.batch_alter_table("api_batch_runs", schema=None) as batch_op:
        batch_op.alter_column("status", server_default=None)
        batch_op.alter_column("total_cases", server_default=None)
        batch_op.alter_column("passed_cases", server_default=None)
        batch_op.alter_column("failed_cases", server_default=None)
        batch_op.alter_column("error_cases", server_default=None)
    with op.batch_alter_table("api_batch_run_items", schema=None) as batch_op:
        batch_op.alter_column("order_index", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_api_batch_run_items_test_case_id", table_name="api_batch_run_items")
    op.drop_index("ix_api_batch_run_items_batch_run_id", table_name="api_batch_run_items")
    op.drop_table("api_batch_run_items")

    op.drop_index("ix_api_batch_runs_suite_id", table_name="api_batch_runs")
    op.drop_index("ix_api_batch_runs_project_id_created_at", table_name="api_batch_runs")
    op.drop_table("api_batch_runs")

    op.drop_index("ix_environment_variables_environment_id", table_name="environment_variables")
    op.drop_table("environment_variables")

    op.drop_index("ix_project_variables_project_id", table_name="project_variables")
    op.drop_table("project_variables")

    op.drop_index("ix_project_environments_project_id", table_name="project_environments")
    op.drop_table("project_environments")

    op.drop_index("ix_api_test_suite_cases_test_case_id", table_name="api_test_suite_cases")
    op.drop_index("ix_api_test_suite_cases_suite_id", table_name="api_test_suite_cases")
    op.drop_table("api_test_suite_cases")

    op.drop_index("ix_api_test_suites_project_id_updated_at", table_name="api_test_suites")
    op.drop_index("ix_api_test_suites_project_id", table_name="api_test_suites")
    op.drop_table("api_test_suites")

    with op.batch_alter_table("api_test_cases", schema=None) as batch_op:
        batch_op.drop_column("extraction_rules")
        batch_op.drop_column("assertion_rules")
