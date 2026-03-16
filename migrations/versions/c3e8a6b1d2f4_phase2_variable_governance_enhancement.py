"""phase2_variable_governance_enhancement

Revision ID: c3e8a6b1d2f4
Revises: b8f56e6e43f1
Create Date: 2026-03-16 12:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c3e8a6b1d2f4"
down_revision: Union[str, Sequence[str], None] = "b8f56e6e43f1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("project_variables", schema=None) as batch_op:
        batch_op.add_column(sa.Column("group_name", sa.String(length=100), nullable=True))
        batch_op.create_index(
            "ix_project_variables_project_id_group_name",
            ["project_id", "group_name"],
            unique=False,
        )
        batch_op.create_check_constraint(
            "ck_project_variables_group_name_not_blank",
            "group_name IS NULL OR length(trim(group_name)) > 0",
        )

    op.create_table(
        "environment_variable_group_bindings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("environment_id", sa.Integer(), nullable=False),
        sa.Column("group_name", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "length(trim(group_name)) > 0",
            name="ck_env_variable_group_bindings_group_not_blank",
        ),
        sa.CheckConstraint(
            "created_at >= 0",
            name="ck_env_variable_group_bindings_created_non_negative",
        ),
        sa.CheckConstraint(
            "updated_at >= 0",
            name="ck_env_variable_group_bindings_updated_non_negative",
        ),
        sa.ForeignKeyConstraint(
            ["environment_id"],
            ["project_environments.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "environment_id",
            "group_name",
            name="uq_env_variable_group_bindings_env_group",
        ),
    )
    with op.batch_alter_table("environment_variable_group_bindings", schema=None) as batch_op:
        batch_op.create_index(
            "ix_env_variable_group_bindings_environment_id",
            ["environment_id"],
            unique=False,
        )
        batch_op.create_index(
            "ix_env_variable_group_bindings_group_name",
            ["group_name"],
            unique=False,
        )

    with op.batch_alter_table("test_runs", schema=None) as batch_op:
        batch_op.add_column(sa.Column("runtime_variables", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("variable_sources", sa.Text(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("test_runs", schema=None) as batch_op:
        batch_op.drop_column("variable_sources")
        batch_op.drop_column("runtime_variables")

    with op.batch_alter_table("environment_variable_group_bindings", schema=None) as batch_op:
        batch_op.drop_index("ix_env_variable_group_bindings_group_name")
        batch_op.drop_index("ix_env_variable_group_bindings_environment_id")
    op.drop_table("environment_variable_group_bindings")

    with op.batch_alter_table("project_variables", schema=None) as batch_op:
        batch_op.drop_constraint("ck_project_variables_group_name_not_blank", type_="check")
        batch_op.drop_index("ix_project_variables_project_id_group_name")
        batch_op.drop_column("group_name")
