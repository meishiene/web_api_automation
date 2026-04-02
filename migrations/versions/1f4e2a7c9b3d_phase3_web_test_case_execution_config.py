"""phase3 web test case execution config

Revision ID: 1f4e2a7c9b3d
Revises: 6c8b1f2a9d4e
Create Date: 2026-04-01 00:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "1f4e2a7c9b3d"
down_revision: Union[str, Sequence[str], None] = "6c8b1f2a9d4e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("web_test_cases", schema=None) as batch_op:
        batch_op.add_column(sa.Column("browser_name", sa.String(length=20), nullable=False, server_default="chromium"))
        batch_op.add_column(sa.Column("viewport_width", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("viewport_height", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("timeout_ms", sa.Integer(), nullable=True, server_default="30000"))
        batch_op.add_column(sa.Column("headless", sa.Integer(), nullable=False, server_default="1"))
        batch_op.add_column(sa.Column("capture_on_failure", sa.Integer(), nullable=False, server_default="1"))
        batch_op.add_column(sa.Column("record_video", sa.Integer(), nullable=False, server_default="0"))
        batch_op.create_check_constraint(
            "ck_web_test_cases_browser_name_allowed",
            "browser_name IN ('chromium', 'firefox', 'webkit')",
        )
        batch_op.create_check_constraint(
            "ck_web_test_cases_viewport_width_min",
            "viewport_width IS NULL OR viewport_width >= 320",
        )
        batch_op.create_check_constraint(
            "ck_web_test_cases_viewport_height_min",
            "viewport_height IS NULL OR viewport_height >= 320",
        )
        batch_op.create_check_constraint(
            "ck_web_test_cases_timeout_ms_min",
            "timeout_ms IS NULL OR timeout_ms >= 100",
        )
        batch_op.create_check_constraint("ck_web_test_cases_headless_bool", "headless IN (0, 1)")
        batch_op.create_check_constraint(
            "ck_web_test_cases_capture_on_failure_bool",
            "capture_on_failure IN (0, 1)",
        )
        batch_op.create_check_constraint("ck_web_test_cases_record_video_bool", "record_video IN (0, 1)")


def downgrade() -> None:
    with op.batch_alter_table("web_test_cases", schema=None) as batch_op:
        batch_op.drop_constraint("ck_web_test_cases_record_video_bool", type_="check")
        batch_op.drop_constraint("ck_web_test_cases_capture_on_failure_bool", type_="check")
        batch_op.drop_constraint("ck_web_test_cases_headless_bool", type_="check")
        batch_op.drop_constraint("ck_web_test_cases_timeout_ms_min", type_="check")
        batch_op.drop_constraint("ck_web_test_cases_viewport_height_min", type_="check")
        batch_op.drop_constraint("ck_web_test_cases_viewport_width_min", type_="check")
        batch_op.drop_constraint("ck_web_test_cases_browser_name_allowed", type_="check")
        batch_op.drop_column("record_video")
        batch_op.drop_column("capture_on_failure")
        batch_op.drop_column("headless")
        batch_op.drop_column("timeout_ms")
        batch_op.drop_column("viewport_height")
        batch_op.drop_column("viewport_width")
        batch_op.drop_column("browser_name")
