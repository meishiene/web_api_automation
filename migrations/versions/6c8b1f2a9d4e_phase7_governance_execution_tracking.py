"""phase7 governance execution tracking

Revision ID: 6c8b1f2a9d4e
Revises: 4c7b2d1e9a6f
Create Date: 2026-03-26 11:20:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6c8b1f2a9d4e"
down_revision = "4c7b2d1e9a6f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "integration_governance_executions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("execution_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("request_json", sa.Text(), nullable=False),
        sa.Column("result_json", sa.Text(), nullable=False),
        sa.Column("requested_by", sa.Integer(), nullable=True),
        sa.Column("completed_at", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "execution_type IN ('retry_failed')",
            name="ck_integration_governance_executions_type_allowed",
        ),
        sa.CheckConstraint(
            "status IN ('completed', 'failed')",
            name="ck_integration_governance_executions_status_allowed",
        ),
        sa.CheckConstraint(
            "length(trim(idempotency_key)) > 0",
            name="ck_integration_governance_executions_key_not_blank",
        ),
        sa.CheckConstraint(
            "created_at >= 0",
            name="ck_integration_governance_executions_created_at_non_negative",
        ),
        sa.CheckConstraint(
            "updated_at >= 0",
            name="ck_integration_governance_executions_updated_at_non_negative",
        ),
        sa.CheckConstraint(
            "completed_at >= 0",
            name="ck_integration_governance_executions_completed_at_non_negative",
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["requested_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "project_id",
            "execution_type",
            "idempotency_key",
            name="uq_integration_governance_executions_project_type_key",
        ),
    )
    op.create_index(
        "ix_integration_governance_executions_project_type_created",
        "integration_governance_executions",
        ["project_id", "execution_type", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_integration_governance_executions_id",
        "integration_governance_executions",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_integration_governance_executions_id",
        table_name="integration_governance_executions",
    )
    op.drop_index(
        "ix_integration_governance_executions_project_type_created",
        table_name="integration_governance_executions",
    )
    op.drop_table("integration_governance_executions")
