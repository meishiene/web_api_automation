"""phase3_web_testing_core

Revision ID: adeb808fa0e9
Revises: c3e8a6b1d2f4
Create Date: 2026-03-16 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "adeb808fa0e9"
down_revision: Union[str, Sequence[str], None] = "c3e8a6b1d2f4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "web_test_cases",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("base_url", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.Integer(), nullable=False),
        sa.CheckConstraint("length(trim(name)) > 0", name="ck_web_test_cases_name_not_blank"),
        sa.CheckConstraint(
            "base_url IS NULL OR length(trim(base_url)) > 0",
            name="ck_web_test_cases_base_url_not_blank",
        ),
        sa.CheckConstraint("created_at >= 0", name="ck_web_test_cases_created_at_non_negative"),
        sa.CheckConstraint("updated_at >= 0", name="ck_web_test_cases_updated_at_non_negative"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "name", name="uq_web_test_cases_project_id_name"),
    )
    with op.batch_alter_table("web_test_cases", schema=None) as batch_op:
        batch_op.create_index("ix_web_test_cases_project_id", ["project_id"], unique=False)
        batch_op.create_index("ix_web_test_cases_project_id_updated_at", ["project_id", "updated_at"], unique=False)

    op.create_table(
        "web_steps",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("web_test_case_id", sa.Integer(), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("params_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.Integer(), nullable=False),
        sa.CheckConstraint("order_index >= 0", name="ck_web_steps_order_index_non_negative"),
        sa.CheckConstraint(
            "action IN ('open', 'click', 'input', 'wait', 'assert', 'screenshot')",
            name="ck_web_steps_action_allowed",
        ),
        sa.CheckConstraint("created_at >= 0", name="ck_web_steps_created_at_non_negative"),
        sa.CheckConstraint("updated_at >= 0", name="ck_web_steps_updated_at_non_negative"),
        sa.ForeignKeyConstraint(["web_test_case_id"], ["web_test_cases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("web_test_case_id", "order_index", name="uq_web_steps_case_order"),
    )
    with op.batch_alter_table("web_steps", schema=None) as batch_op:
        batch_op.create_index("ix_web_steps_web_test_case_id", ["web_test_case_id"], unique=False)

    op.create_table(
        "web_locators",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("strategy", sa.String(length=20), nullable=False),
        sa.Column("selector", sa.String(length=500), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.Integer(), nullable=False),
        sa.CheckConstraint("length(trim(name)) > 0", name="ck_web_locators_name_not_blank"),
        sa.CheckConstraint("length(trim(selector)) > 0", name="ck_web_locators_selector_not_blank"),
        sa.CheckConstraint(
            "strategy IN ('css', 'xpath', 'text', 'role', 'testid')",
            name="ck_web_locators_strategy_allowed",
        ),
        sa.CheckConstraint("created_at >= 0", name="ck_web_locators_created_at_non_negative"),
        sa.CheckConstraint("updated_at >= 0", name="ck_web_locators_updated_at_non_negative"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "name", name="uq_web_locators_project_id_name"),
    )
    with op.batch_alter_table("web_locators", schema=None) as batch_op:
        batch_op.create_index("ix_web_locators_project_id", ["project_id"], unique=False)
        batch_op.create_index("ix_web_locators_project_id_updated_at", ["project_id", "updated_at"], unique=False)


def downgrade() -> None:
    op.drop_table("web_locators")
    op.drop_table("web_steps")
    op.drop_table("web_test_cases")

