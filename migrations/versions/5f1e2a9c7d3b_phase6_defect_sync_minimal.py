"""phase6 defect sync minimal

Revision ID: 5f1e2a9c7d3b
Revises: 7d2b6f4c8a1e
Create Date: 2026-03-17 23:59:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5f1e2a9c7d3b"
down_revision = "7d2b6f4c8a1e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "defect_sync_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("integration_config_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("run_type", sa.String(length=20), nullable=False),
        sa.Column("last_run_id", sa.Integer(), nullable=False),
        sa.Column("case_id", sa.Integer(), nullable=True),
        sa.Column("case_name", sa.String(length=255), nullable=False),
        sa.Column("failure_fingerprint", sa.String(length=128), nullable=False),
        sa.Column("failure_category", sa.String(length=100), nullable=True),
        sa.Column("failure_message", sa.Text(), nullable=True),
        sa.Column("issue_key", sa.String(length=100), nullable=False),
        sa.Column("issue_url", sa.String(length=500), nullable=True),
        sa.Column("issue_status", sa.String(length=50), nullable=False),
        sa.Column("summary", sa.String(length=255), nullable=False),
        sa.Column("detail_api_path", sa.String(length=500), nullable=True),
        sa.Column("tags_json", sa.Text(), nullable=True),
        sa.Column("last_payload_json", sa.Text(), nullable=True),
        sa.Column("occurrence_count", sa.Integer(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.Integer(), nullable=False),
        sa.CheckConstraint("length(trim(run_type)) > 0", name="ck_defect_sync_run_type_not_blank"),
        sa.CheckConstraint("run_type IN ('api', 'web')", name="ck_defect_sync_run_type_allowed"),
        sa.CheckConstraint("length(trim(issue_key)) > 0", name="ck_defect_sync_issue_key_not_blank"),
        sa.CheckConstraint("occurrence_count >= 1", name="ck_defect_sync_occurrence_positive"),
        sa.CheckConstraint("created_at >= 0", name="ck_defect_sync_created_at_non_negative"),
        sa.CheckConstraint("updated_at >= 0", name="ck_defect_sync_updated_at_non_negative"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["integration_config_id"], ["integration_configs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "failure_fingerprint", name="uq_defect_sync_project_fingerprint"),
    )
    op.create_index("ix_defect_sync_project_id", "defect_sync_records", ["project_id"], unique=False)
    op.create_index("ix_defect_sync_config_id", "defect_sync_records", ["integration_config_id"], unique=False)
    op.create_index("ix_defect_sync_issue_key", "defect_sync_records", ["issue_key"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_defect_sync_issue_key", table_name="defect_sync_records")
    op.drop_index("ix_defect_sync_config_id", table_name="defect_sync_records")
    op.drop_index("ix_defect_sync_project_id", table_name="defect_sync_records")
    op.drop_table("defect_sync_records")
