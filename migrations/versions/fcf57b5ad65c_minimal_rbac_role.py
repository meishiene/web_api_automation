"""minimal_rbac_role

Revision ID: fcf57b5ad65c
Revises: 802c16c9f78e
Create Date: 2026-03-12 00:03:50.613324

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fcf57b5ad65c'
down_revision: Union[str, Sequence[str], None] = '802c16c9f78e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("role", sa.String(length=20), nullable=False, server_default="user"))
        batch_op.create_check_constraint("ck_users_role_allowed", "role IN ('admin', 'user')")

    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.alter_column("role", server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_constraint("ck_users_role_allowed", type_="check")
        batch_op.drop_column("role")
