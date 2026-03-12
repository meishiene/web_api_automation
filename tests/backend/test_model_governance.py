import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

from app.models.api_test_case import ApiTestCase
from app.models.project import Project
from app.models.run_queue import RunQueue
from app.models.schedule_task import ScheduleTask
from app.models.test_run import TestRun as RunRecordModel
from app.models.user import User


def _seed_user(db_session, username: str) -> User:
    user = User(username=username, password="pwd")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _seed_project(db_session, owner_id: int, name: str = "project") -> Project:
    project = Project(name=name, description="desc", owner_id=owner_id)
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project


def test_unique_project_name_per_owner(db_session):
    owner = _seed_user(db_session, "owner")
    _seed_project(db_session, owner.id, "same-name")

    duplicate = Project(name="same-name", description="desc", owner_id=owner.id)
    db_session.add(duplicate)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    another_owner = _seed_user(db_session, "another-owner")
    project = Project(name="same-name", description="desc", owner_id=another_owner.id)
    db_session.add(project)
    db_session.commit()
    assert project.id is not None


def test_project_delete_cascades_to_related_entities(db_session):
    owner = _seed_user(db_session, "owner")
    project = _seed_project(db_session, owner.id, "cascade-project")

    case = ApiTestCase(name="case-1", project_id=project.id, method="GET", url="https://example.com")
    db_session.add(case)
    db_session.commit()
    db_session.refresh(case)

    run = RunRecordModel(test_case_id=case.id, status="success", duration_ms=1)
    task = ScheduleTask(
        project_id=project.id,
        name="task-1",
        cron_expr="*/5 * * * *",
        target_type="test_case",
        created_by=owner.id,
    )
    queue_item = RunQueue(project_id=project.id, run_type="api", target_type="test_case", target_id=case.id)
    db_session.add_all([run, task, queue_item])
    db_session.commit()

    db_session.delete(project)
    db_session.commit()

    assert db_session.query(ApiTestCase).filter(ApiTestCase.id == case.id).first() is None
    assert db_session.query(RunRecordModel).filter(RunRecordModel.id == run.id).first() is None
    assert db_session.query(ScheduleTask).filter(ScheduleTask.id == task.id).first() is None
    assert db_session.query(RunQueue).filter(RunQueue.id == queue_item.id).first() is None


def test_timestamp_lifecycle_defaults_are_applied(db_session):
    owner = _seed_user(db_session, "owner")
    project = _seed_project(db_session, owner.id, "lifecycle-project")

    case = ApiTestCase(name="case-1", project_id=project.id, method="GET", url="https://example.com")
    db_session.add(case)
    db_session.commit()
    db_session.refresh(case)

    assert isinstance(case.created_at, int)
    assert isinstance(case.updated_at, int)
    assert case.updated_at >= case.created_at


def test_check_constraints_reject_invalid_domain_values(db_session):
    owner = _seed_user(db_session, "owner")
    project = _seed_project(db_session, owner.id, "constraints-project")

    invalid_case = ApiTestCase(
        name="case-1",
        project_id=project.id,
        method="TRACE",
        url="https://example.com",
        expected_status=200,
    )
    db_session.add(invalid_case)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    invalid_queue = RunQueue(
        project_id=project.id,
        run_type="api",
        target_type="test_case",
        target_id=1,
        priority=0,
    )
    db_session.add(invalid_queue)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_governance_indexes_exist(db_session):
    inspector = inspect(db_session.bind)

    project_indexes = {item["name"] for item in inspector.get_indexes("projects")}
    run_indexes = {item["name"] for item in inspector.get_indexes("test_runs")}

    assert "ix_projects_owner_id" in project_indexes
    assert "ix_test_runs_test_case_id_created_at" in run_indexes
