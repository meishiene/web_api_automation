"""phase6 integration config center

Revision ID: 6a9d4c2e1b7f
Revises: 2c1b7f9a4d10
Create Date: 2026-03-17 21:20:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6a9d4c2e1b7f"
down_revision = "2c1b7f9a4d10"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "integration_configs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("integration_type", sa.String(length=20), nullable=False),
        sa.Column("provider", sa.String(length=100), nullable=False),
        sa.Column("base_url", sa.String(length=500), nullable=True),
        sa.Column("credential_ref", sa.String(length=200), nullable=True),
        sa.Column("credential_value", sa.Text(), nullable=True),
        sa.Column("config_json", sa.Text(), nullable=True),
        sa.Column("is_enabled", sa.Integer(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.Integer(), nullable=False),
        sa.CheckConstraint("length(trim(name)) > 0", name="ck_integration_configs_name_not_blank"),
        sa.CheckConstraint(
            "integration_type IN ('cicd', 'notification', 'defect', 'identity', 'webhook')",
            name="ck_integration_configs_type_allowed",
        ),
        sa.CheckConstraint("length(trim(provider)) > 0", name="ck_integration_configs_provider_not_blank"),
        sa.CheckConstraint("is_enabled IN (0, 1)", name="ck_integration_configs_is_enabled_bool"),
        sa.CheckConstraint("created_at >= 0", name="ck_integration_configs_created_at_non_negative"),
        sa.CheckConstraint("updated_at >= 0", name="ck_integration_configs_updated_at_non_negative"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "name", name="uq_integration_configs_project_name"),
    )
    op.create_index("ix_integration_configs_id", "integration_configs", ["id"], unique=False)
    op.create_index("ix_integration_configs_project_id", "integration_configs", ["project_id"], unique=False)
    op.create_index(
        "ix_integration_configs_project_type",
        "integration_configs",
        ["project_id", "integration_type"],
        unique=False,
    )
    op.create_index(
        "ix_integration_configs_project_enabled",
        "integration_configs",
        ["project_id", "is_enabled"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_integration_configs_project_enabled", table_name="integration_configs")
    op.drop_index("ix_integration_configs_project_type", table_name="integration_configs")
    op.drop_index("ix_integration_configs_project_id", table_name="integration_configs")
    op.drop_index("ix_integration_configs_id", table_name="integration_configs")
    op.drop_table("integration_configs")
