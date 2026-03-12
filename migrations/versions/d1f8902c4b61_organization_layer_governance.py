"""organization_layer_governance

Revision ID: d1f8902c4b61
Revises: 9b1f0b38d7d2
Create Date: 2026-03-12 15:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d1f8902c4b61"
down_revision: Union[str, Sequence[str], None] = "9b1f0b38d7d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_organizations_name"),
        sa.CheckConstraint("length(trim(name)) > 0", name="ck_organizations_name_not_blank"),
        sa.CheckConstraint("created_at >= 0", name="ck_organizations_created_at_non_negative"),
    )
    op.create_index("ix_organizations_owner_id", "organizations", ["owner_id"], unique=False)

    op.create_table(
        "organization_members",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False, server_default="member"),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "user_id", name="uq_organization_members_org_user"),
        sa.CheckConstraint("role IN ('admin', 'member')", name="ck_organization_members_role_allowed"),
        sa.CheckConstraint("created_at >= 0", name="ck_organization_members_created_at_non_negative"),
    )
    op.create_index("ix_organization_members_org_id", "organization_members", ["organization_id"], unique=False)
    op.create_index("ix_organization_members_user_id", "organization_members", ["user_id"], unique=False)

    with op.batch_alter_table("projects", schema=None) as batch_op:
        batch_op.add_column(sa.Column("organization_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_projects_organization_id_organizations",
            "organizations",
            ["organization_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch_op.create_index("ix_projects_organization_id", ["organization_id"], unique=False)

    with op.batch_alter_table("organization_members", schema=None) as batch_op:
        batch_op.alter_column("role", server_default=None)


def downgrade() -> None:
    with op.batch_alter_table("projects", schema=None) as batch_op:
        batch_op.drop_index("ix_projects_organization_id")
        batch_op.drop_constraint("fk_projects_organization_id_organizations", type_="foreignkey")
        batch_op.drop_column("organization_id")

    op.drop_index("ix_organization_members_user_id", table_name="organization_members")
    op.drop_index("ix_organization_members_org_id", table_name="organization_members")
    op.drop_table("organization_members")

    op.drop_index("ix_organizations_owner_id", table_name="organizations")
    op.drop_table("organizations")
