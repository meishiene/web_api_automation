"""domain_model_governance

Revision ID: 01fcc228897e
Revises: 8daac485a5f7
Create Date: 2026-03-11 23:31:14.542221

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '01fcc228897e'
down_revision: Union[str, Sequence[str], None] = '8daac485a5f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _upgrade_postgres_foreign_keys() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    statements = [
        """
        ALTER TABLE projects
        DROP CONSTRAINT IF EXISTS projects_owner_id_fkey,
        ADD CONSTRAINT projects_owner_id_fkey
        FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
        """,
        """
        ALTER TABLE api_test_cases
        DROP CONSTRAINT IF EXISTS api_test_cases_project_id_fkey,
        ADD CONSTRAINT api_test_cases_project_id_fkey
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        """,
        """
        ALTER TABLE test_runs
        DROP CONSTRAINT IF EXISTS test_runs_test_case_id_fkey,
        ADD CONSTRAINT test_runs_test_case_id_fkey
        FOREIGN KEY (test_case_id) REFERENCES api_test_cases(id) ON DELETE CASCADE
        """,
        """
        ALTER TABLE schedule_tasks
        DROP CONSTRAINT IF EXISTS schedule_tasks_project_id_fkey,
        ADD CONSTRAINT schedule_tasks_project_id_fkey
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        """,
        """
        ALTER TABLE schedule_tasks
        DROP CONSTRAINT IF EXISTS schedule_tasks_created_by_fkey,
        ADD CONSTRAINT schedule_tasks_created_by_fkey
        FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
        """,
        """
        ALTER TABLE run_queue
        DROP CONSTRAINT IF EXISTS run_queue_project_id_fkey,
        ADD CONSTRAINT run_queue_project_id_fkey
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        """,
    ]
    for statement in statements:
        op.execute(sa.text(statement))


def _downgrade_postgres_foreign_keys() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    statements = [
        """
        ALTER TABLE projects
        DROP CONSTRAINT IF EXISTS projects_owner_id_fkey,
        ADD CONSTRAINT projects_owner_id_fkey
        FOREIGN KEY (owner_id) REFERENCES users(id)
        """,
        """
        ALTER TABLE api_test_cases
        DROP CONSTRAINT IF EXISTS api_test_cases_project_id_fkey,
        ADD CONSTRAINT api_test_cases_project_id_fkey
        FOREIGN KEY (project_id) REFERENCES projects(id)
        """,
        """
        ALTER TABLE test_runs
        DROP CONSTRAINT IF EXISTS test_runs_test_case_id_fkey,
        ADD CONSTRAINT test_runs_test_case_id_fkey
        FOREIGN KEY (test_case_id) REFERENCES api_test_cases(id)
        """,
        """
        ALTER TABLE schedule_tasks
        DROP CONSTRAINT IF EXISTS schedule_tasks_project_id_fkey,
        ADD CONSTRAINT schedule_tasks_project_id_fkey
        FOREIGN KEY (project_id) REFERENCES projects(id)
        """,
        """
        ALTER TABLE schedule_tasks
        DROP CONSTRAINT IF EXISTS schedule_tasks_created_by_fkey,
        ADD CONSTRAINT schedule_tasks_created_by_fkey
        FOREIGN KEY (created_by) REFERENCES users(id)
        """,
        """
        ALTER TABLE run_queue
        DROP CONSTRAINT IF EXISTS run_queue_project_id_fkey,
        ADD CONSTRAINT run_queue_project_id_fkey
        FOREIGN KEY (project_id) REFERENCES projects(id)
        """,
    ]
    for statement in statements:
        op.execute(sa.text(statement))


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('api_test_cases', schema=None) as batch_op:
        batch_op.alter_column('expected_status',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.create_check_constraint('ck_api_test_cases_name_not_blank', 'length(trim(name)) > 0')
        batch_op.create_check_constraint('ck_api_test_cases_url_not_blank', 'length(trim(url)) > 0')
        batch_op.create_check_constraint(
            'ck_api_test_cases_method_allowed',
            "method IN ('GET', 'POST', 'PUT', 'PATCH', 'DELETE')",
        )
        batch_op.create_check_constraint(
            'ck_api_test_cases_expected_status_range',
            'expected_status >= 100 AND expected_status < 600',
        )
        batch_op.create_check_constraint('ck_api_test_cases_created_at_non_negative', 'created_at >= 0')
        batch_op.create_check_constraint('ck_api_test_cases_updated_at_non_negative', 'updated_at >= 0')
        batch_op.create_index('ix_api_test_cases_project_id', ['project_id'], unique=False)
        batch_op.create_index('ix_api_test_cases_project_id_updated_at', ['project_id', 'updated_at'], unique=False)
        batch_op.create_unique_constraint('uq_api_test_cases_project_id_name', ['project_id', 'name'])

    with op.batch_alter_table('audit_logs', schema=None) as batch_op:
        batch_op.create_check_constraint('ck_audit_logs_result_allowed', "result IN ('success', 'failed')")
        batch_op.create_check_constraint('ck_audit_logs_created_at_non_negative', 'created_at >= 0')
        batch_op.create_index('ix_audit_logs_action_created_at', ['action', 'created_at'], unique=False)
        batch_op.create_index('ix_audit_logs_user_created_at', ['user_id', 'created_at'], unique=False)

    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.create_check_constraint('ck_projects_name_not_blank', 'length(trim(name)) > 0')
        batch_op.create_check_constraint('ck_projects_created_at_non_negative', 'created_at >= 0')
        batch_op.create_index('ix_projects_owner_id', ['owner_id'], unique=False)
        batch_op.create_unique_constraint('uq_projects_owner_id_name', ['owner_id', 'name'])

    with op.batch_alter_table('run_queue', schema=None) as batch_op:
        batch_op.create_check_constraint('ck_run_queue_run_type_allowed', "run_type IN ('api', 'web')")
        batch_op.create_check_constraint(
            'ck_run_queue_target_type_allowed',
            "target_type IN ('test_case', 'test_suite')",
        )
        batch_op.create_check_constraint(
            'ck_run_queue_status_allowed',
            "status IN ('queued', 'running', 'success', 'failed', 'error')",
        )
        batch_op.create_check_constraint('ck_run_queue_priority_range', 'priority >= 1 AND priority <= 10')
        batch_op.create_check_constraint(
            'ck_run_queue_scheduled_by_allowed',
            "scheduled_by IN ('manual', 'scheduler', 'ci')",
        )
        batch_op.create_check_constraint(
            'ck_run_queue_started_at_non_negative',
            'started_at IS NULL OR started_at >= 0',
        )
        batch_op.create_check_constraint(
            'ck_run_queue_finished_at_non_negative',
            'finished_at IS NULL OR finished_at >= 0',
        )
        batch_op.create_check_constraint('ck_run_queue_created_at_non_negative', 'created_at >= 0')
        batch_op.create_check_constraint(
            'ck_run_queue_finished_after_started',
            'finished_at IS NULL OR started_at IS NULL OR finished_at >= started_at',
        )
        batch_op.create_index('ix_run_queue_project_run_type', ['project_id', 'run_type'], unique=False)
        batch_op.create_index('ix_run_queue_project_status_created_at', ['project_id', 'status', 'created_at'], unique=False)

    with op.batch_alter_table('schedule_tasks', schema=None) as batch_op:
        batch_op.create_check_constraint('ck_schedule_tasks_name_not_blank', 'length(trim(name)) > 0')
        batch_op.create_check_constraint(
            'ck_schedule_tasks_cron_expr_not_blank',
            'length(trim(cron_expr)) > 0',
        )
        batch_op.create_check_constraint('ck_schedule_tasks_enabled_flag', 'enabled IN (0, 1)')
        batch_op.create_check_constraint(
            'ck_schedule_tasks_target_type_allowed',
            "target_type IN ('test_case', 'test_suite', 'tag', 'custom')",
        )
        batch_op.create_check_constraint('ck_schedule_tasks_created_at_non_negative', 'created_at >= 0')
        batch_op.create_check_constraint('ck_schedule_tasks_updated_at_non_negative', 'updated_at >= 0')
        batch_op.create_index('ix_schedule_tasks_created_by_updated_at', ['created_by', 'updated_at'], unique=False)
        batch_op.create_index('ix_schedule_tasks_project_enabled', ['project_id', 'enabled'], unique=False)
        batch_op.create_unique_constraint('uq_schedule_tasks_project_id_name', ['project_id', 'name'])

    with op.batch_alter_table('test_runs', schema=None) as batch_op:
        batch_op.create_check_constraint(
            'ck_test_runs_status_allowed',
            "status IN ('success', 'failed', 'error')",
        )
        batch_op.create_check_constraint(
            'ck_test_runs_actual_status_range',
            'actual_status IS NULL OR (actual_status >= 100 AND actual_status < 600)',
        )
        batch_op.create_check_constraint(
            'ck_test_runs_duration_non_negative',
            'duration_ms IS NULL OR duration_ms >= 0',
        )
        batch_op.create_check_constraint('ck_test_runs_created_at_non_negative', 'created_at >= 0')
        batch_op.create_index('ix_test_runs_test_case_id', ['test_case_id'], unique=False)
        batch_op.create_index('ix_test_runs_test_case_id_created_at', ['test_case_id', 'created_at'], unique=False)

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_check_constraint('ck_users_username_not_blank', 'length(trim(username)) > 0')
        batch_op.create_check_constraint('ck_users_created_at_non_negative', 'created_at >= 0')

    _upgrade_postgres_foreign_keys()


def downgrade() -> None:
    """Downgrade schema."""
    _downgrade_postgres_foreign_keys()

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('ck_users_created_at_non_negative', type_='check')
        batch_op.drop_constraint('ck_users_username_not_blank', type_='check')

    with op.batch_alter_table('test_runs', schema=None) as batch_op:
        batch_op.drop_index('ix_test_runs_test_case_id_created_at')
        batch_op.drop_index('ix_test_runs_test_case_id')
        batch_op.drop_constraint('ck_test_runs_created_at_non_negative', type_='check')
        batch_op.drop_constraint('ck_test_runs_duration_non_negative', type_='check')
        batch_op.drop_constraint('ck_test_runs_actual_status_range', type_='check')
        batch_op.drop_constraint('ck_test_runs_status_allowed', type_='check')

    with op.batch_alter_table('schedule_tasks', schema=None) as batch_op:
        batch_op.drop_constraint('uq_schedule_tasks_project_id_name', type_='unique')
        batch_op.drop_index('ix_schedule_tasks_project_enabled')
        batch_op.drop_index('ix_schedule_tasks_created_by_updated_at')
        batch_op.drop_constraint('ck_schedule_tasks_updated_at_non_negative', type_='check')
        batch_op.drop_constraint('ck_schedule_tasks_created_at_non_negative', type_='check')
        batch_op.drop_constraint('ck_schedule_tasks_target_type_allowed', type_='check')
        batch_op.drop_constraint('ck_schedule_tasks_enabled_flag', type_='check')
        batch_op.drop_constraint('ck_schedule_tasks_cron_expr_not_blank', type_='check')
        batch_op.drop_constraint('ck_schedule_tasks_name_not_blank', type_='check')

    with op.batch_alter_table('run_queue', schema=None) as batch_op:
        batch_op.drop_index('ix_run_queue_project_status_created_at')
        batch_op.drop_index('ix_run_queue_project_run_type')
        batch_op.drop_constraint('ck_run_queue_finished_after_started', type_='check')
        batch_op.drop_constraint('ck_run_queue_created_at_non_negative', type_='check')
        batch_op.drop_constraint('ck_run_queue_finished_at_non_negative', type_='check')
        batch_op.drop_constraint('ck_run_queue_started_at_non_negative', type_='check')
        batch_op.drop_constraint('ck_run_queue_scheduled_by_allowed', type_='check')
        batch_op.drop_constraint('ck_run_queue_priority_range', type_='check')
        batch_op.drop_constraint('ck_run_queue_status_allowed', type_='check')
        batch_op.drop_constraint('ck_run_queue_target_type_allowed', type_='check')
        batch_op.drop_constraint('ck_run_queue_run_type_allowed', type_='check')

    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.drop_constraint('uq_projects_owner_id_name', type_='unique')
        batch_op.drop_index('ix_projects_owner_id')
        batch_op.drop_constraint('ck_projects_created_at_non_negative', type_='check')
        batch_op.drop_constraint('ck_projects_name_not_blank', type_='check')

    with op.batch_alter_table('audit_logs', schema=None) as batch_op:
        batch_op.drop_index('ix_audit_logs_user_created_at')
        batch_op.drop_index('ix_audit_logs_action_created_at')
        batch_op.drop_constraint('ck_audit_logs_created_at_non_negative', type_='check')
        batch_op.drop_constraint('ck_audit_logs_result_allowed', type_='check')

    with op.batch_alter_table('api_test_cases', schema=None) as batch_op:
        batch_op.drop_constraint('uq_api_test_cases_project_id_name', type_='unique')
        batch_op.drop_index('ix_api_test_cases_project_id_updated_at')
        batch_op.drop_index('ix_api_test_cases_project_id')
        batch_op.drop_constraint('ck_api_test_cases_updated_at_non_negative', type_='check')
        batch_op.drop_constraint('ck_api_test_cases_created_at_non_negative', type_='check')
        batch_op.drop_constraint('ck_api_test_cases_expected_status_range', type_='check')
        batch_op.drop_constraint('ck_api_test_cases_method_allowed', type_='check')
        batch_op.drop_constraint('ck_api_test_cases_url_not_blank', type_='check')
        batch_op.drop_constraint('ck_api_test_cases_name_not_blank', type_='check')
        batch_op.alter_column('expected_status',
               existing_type=sa.INTEGER(),
               nullable=True)
