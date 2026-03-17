"""phase6 identity oauth minimal

Revision ID: 4c7b2d1e9a6f
Revises: 5f1e2a9c7d3b
Create Date: 2026-03-18 00:40:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4c7b2d1e9a6f"
down_revision = "5f1e2a9c7d3b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "identity_provider_bindings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("integration_config_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=100), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("external_subject", sa.String(length=255), nullable=False),
        sa.Column("external_email", sa.String(length=255), nullable=True),
        sa.Column("last_login_at", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.Integer(), nullable=False),
        sa.CheckConstraint("length(trim(provider)) > 0", name="ck_identity_binding_provider_not_blank"),
        sa.CheckConstraint("length(trim(external_subject)) > 0", name="ck_identity_binding_subject_not_blank"),
        sa.CheckConstraint("created_at >= 0", name="ck_identity_binding_created_at_non_negative"),
        sa.CheckConstraint("updated_at >= 0", name="ck_identity_binding_updated_at_non_negative"),
        sa.ForeignKeyConstraint(["integration_config_id"], ["integration_configs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider", "external_subject", name="uq_identity_binding_provider_subject"),
        sa.UniqueConstraint("provider", "user_id", name="uq_identity_binding_provider_user"),
    )
    op.create_index("ix_identity_binding_project_id", "identity_provider_bindings", ["project_id"], unique=False)
    op.create_index("ix_identity_binding_config_id", "identity_provider_bindings", ["integration_config_id"], unique=False)
    op.create_index("ix_identity_binding_user_id", "identity_provider_bindings", ["user_id"], unique=False)

    op.create_table(
        "identity_oauth_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("integration_config_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=100), nullable=False),
        sa.Column("state", sa.String(length=128), nullable=False),
        sa.Column("redirect_uri", sa.String(length=500), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("expires_at", sa.Integer(), nullable=False),
        sa.Column("requested_by", sa.Integer(), nullable=True),
        sa.Column("consumed_at", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.Integer(), nullable=False),
        sa.CheckConstraint("length(trim(provider)) > 0", name="ck_identity_oauth_sessions_provider_not_blank"),
        sa.CheckConstraint("length(trim(state)) > 0", name="ck_identity_oauth_sessions_state_not_blank"),
        sa.CheckConstraint("expires_at >= 0", name="ck_identity_oauth_sessions_expires_at_non_negative"),
        sa.CheckConstraint("created_at >= 0", name="ck_identity_oauth_sessions_created_at_non_negative"),
        sa.CheckConstraint("updated_at >= 0", name="ck_identity_oauth_sessions_updated_at_non_negative"),
        sa.CheckConstraint("status IN ('pending', 'completed', 'expired')", name="ck_identity_oauth_sessions_status_allowed"),
        sa.ForeignKeyConstraint(["integration_config_id"], ["integration_configs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["requested_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("state", name="uq_identity_oauth_sessions_state"),
    )
    op.create_index("ix_identity_oauth_sessions_project_id", "identity_oauth_sessions", ["project_id"], unique=False)
    op.create_index("ix_identity_oauth_sessions_config_id", "identity_oauth_sessions", ["integration_config_id"], unique=False)
    op.create_index("ix_identity_oauth_sessions_expires_at", "identity_oauth_sessions", ["expires_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_identity_oauth_sessions_expires_at", table_name="identity_oauth_sessions")
    op.drop_index("ix_identity_oauth_sessions_config_id", table_name="identity_oauth_sessions")
    op.drop_index("ix_identity_oauth_sessions_project_id", table_name="identity_oauth_sessions")
    op.drop_table("identity_oauth_sessions")

    op.drop_index("ix_identity_binding_user_id", table_name="identity_provider_bindings")
    op.drop_index("ix_identity_binding_config_id", table_name="identity_provider_bindings")
    op.drop_index("ix_identity_binding_project_id", table_name="identity_provider_bindings")
    op.drop_table("identity_provider_bindings")
