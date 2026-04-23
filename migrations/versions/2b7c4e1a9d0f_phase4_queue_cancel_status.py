"""phase4 queue cancel status

Revision ID: 2b7c4e1a9d0f
Revises: 1f4e2a7c9b3d
Create Date: 2026-04-03 00:40:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2b7c4e1a9d0f"
down_revision: Union[str, Sequence[str], None] = "1f4e2a7c9b3d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_named_check_constraint(bind, table_name: str, constraint_name: str) -> bool:
    inspector = sa.inspect(bind)
    constraints = inspector.get_check_constraints(table_name)
    return any(item.get("name") == constraint_name for item in constraints)


def upgrade() -> None:
    bind = op.get_bind()
    if not _has_named_check_constraint(bind, "run_queue", "ck_run_queue_status_allowed"):
        return
    with op.batch_alter_table("run_queue", schema=None) as batch_op:
        batch_op.drop_constraint("ck_run_queue_status_allowed", type_="check")
        batch_op.create_check_constraint(
            "ck_run_queue_status_allowed",
            "status IN ('queued', 'running', 'success', 'failed', 'error', 'canceled')",
        )


def downgrade() -> None:
    bind = op.get_bind()
    if not _has_named_check_constraint(bind, "run_queue", "ck_run_queue_status_allowed"):
        return
    with op.batch_alter_table("run_queue", schema=None) as batch_op:
        batch_op.drop_constraint("ck_run_queue_status_allowed", type_="check")
        batch_op.create_check_constraint(
            "ck_run_queue_status_allowed",
            "status IN ('queued', 'running', 'success', 'failed', 'error')",
        )
