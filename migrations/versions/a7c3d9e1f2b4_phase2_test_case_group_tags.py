"""phase2_test_case_group_tags

Revision ID: a7c3d9e1f2b4
Revises: e2b4c6a8d901
Create Date: 2026-03-16 10:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a7c3d9e1f2b4"
down_revision: Union[str, Sequence[str], None] = "e2b4c6a8d901"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("api_test_cases", schema=None) as batch_op:
        batch_op.add_column(sa.Column("case_group", sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column("tags", sa.Text(), nullable=True))
        batch_op.create_check_constraint(
            "ck_api_test_cases_case_group_not_blank",
            "case_group IS NULL OR length(trim(case_group)) > 0",
        )
        batch_op.create_index(
            "ix_api_test_cases_project_id_case_group",
            ["project_id", "case_group"],
            unique=False,
        )


def downgrade() -> None:
    with op.batch_alter_table("api_test_cases", schema=None) as batch_op:
        batch_op.drop_index("ix_api_test_cases_project_id_case_group")
        batch_op.drop_constraint("ck_api_test_cases_case_group_not_blank", type_="check")
        batch_op.drop_column("tags")
        batch_op.drop_column("case_group")
