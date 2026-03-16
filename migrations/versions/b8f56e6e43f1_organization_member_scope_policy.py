"""organization_member_scope_policy

Revision ID: b8f56e6e43f1
Revises: a7c3d9e1f2b4
Create Date: 2026-03-16 11:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b8f56e6e43f1"
down_revision: Union[str, Sequence[str], None] = "a7c3d9e1f2b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("organization_members", schema=None) as batch_op:
        batch_op.add_column(sa.Column("department", sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column("workspace", sa.String(length=100), nullable=True))
        batch_op.create_index("ix_organization_members_org_department", ["organization_id", "department"], unique=False)
        batch_op.create_index("ix_organization_members_org_workspace", ["organization_id", "workspace"], unique=False)
        batch_op.create_check_constraint(
            "ck_organization_members_department_not_blank",
            "department IS NULL OR length(trim(department)) > 0",
        )
        batch_op.create_check_constraint(
            "ck_organization_members_workspace_not_blank",
            "workspace IS NULL OR length(trim(workspace)) > 0",
        )


def downgrade() -> None:
    with op.batch_alter_table("organization_members", schema=None) as batch_op:
        batch_op.drop_constraint("ck_organization_members_workspace_not_blank", type_="check")
        batch_op.drop_constraint("ck_organization_members_department_not_blank", type_="check")
        batch_op.drop_index("ix_organization_members_org_workspace")
        batch_op.drop_index("ix_organization_members_org_department")
        batch_op.drop_column("workspace")
        batch_op.drop_column("department")
