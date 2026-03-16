import json
import time
from typing import Any, Dict

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.errors import AppException, ErrorCode
from app.models.project import Project
from app.models.run_queue import RunQueue
from app.models.schedule_task import ScheduleTask
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.schedule_task import (
    ScheduleTaskCreateRequest,
    ScheduleTaskListResponse,
    ScheduleTaskResponse,
    ScheduleTaskTriggerResponse,
    ScheduleTaskUpdateRequest,
)
from app.services.access_control import can_manage_project, can_view_project
from app.services.audit_service import create_audit_log

router = APIRouter()


def _parse_payload(raw: str | None) -> Dict[str, Any]:
    if not raw:
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _to_payload_text(payload: Dict[str, Any] | None) -> str | None:
    if payload is None:
        return None
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _to_response(task: ScheduleTask) -> ScheduleTaskResponse:
    return ScheduleTaskResponse(
        id=task.id,
        project_id=task.project_id,
        name=task.name,
        cron_expr=task.cron_expr,
        timezone=task.timezone,
        enabled=bool(task.enabled),
        target_type=task.target_type,
        target_id=task.target_id,
        payload=_parse_payload(task.payload),
        created_by=task.created_by,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


@router.get("/project/{project_id}", response_model=ScheduleTaskListResponse)
def list_schedule_tasks(
    project_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ScheduleTaskListResponse:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise AppException(404, ErrorCode.PROJECT_NOT_FOUND, "Project not found")
    if not can_view_project(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    records = (
        db.query(ScheduleTask)
        .filter(ScheduleTask.project_id == project_id)
        .order_by(ScheduleTask.updated_at.desc(), ScheduleTask.id.desc())
        .all()
    )
    return ScheduleTaskListResponse(
        items=[_to_response(item) for item in records],
        total=len(records),
    )


@router.post("", response_model=ScheduleTaskResponse)
def create_schedule_task(
    payload: ScheduleTaskCreateRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ScheduleTaskResponse:
    project = db.query(Project).filter(Project.id == payload.project_id).first()
    if not project:
        raise AppException(404, ErrorCode.PROJECT_NOT_FOUND, "Project not found")
    if not can_manage_project(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    duplicated = (
        db.query(ScheduleTask)
        .filter(ScheduleTask.project_id == payload.project_id, ScheduleTask.name == payload.name.strip())
        .first()
    )
    if duplicated:
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "Schedule task name already exists")

    now = int(time.time())
    task = ScheduleTask(
        project_id=payload.project_id,
        name=payload.name.strip(),
        cron_expr=payload.cron_expr.strip(),
        timezone=payload.timezone.strip(),
        enabled=1 if payload.enabled else 0,
        target_type=payload.target_type,
        target_id=payload.target_id,
        payload=_to_payload_text(payload.payload),
        created_by=user.id,
        created_at=now,
        updated_at=now,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    create_audit_log(
        db=db,
        request=request,
        action="schedule_task.create",
        resource_type="schedule_task",
        resource_id=str(task.id),
        user_id=user.id,
        details={"project_id": payload.project_id, "name": task.name},
    )
    return _to_response(task)


@router.put("/{task_id}", response_model=ScheduleTaskResponse)
def update_schedule_task(
    task_id: int,
    payload: ScheduleTaskUpdateRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ScheduleTaskResponse:
    task = db.query(ScheduleTask).filter(ScheduleTask.id == task_id).first()
    if not task:
        raise AppException(404, ErrorCode.SCHEDULE_TASK_NOT_FOUND, "Schedule task not found")

    project = db.query(Project).filter(Project.id == task.project_id).first()
    if not project:
        raise AppException(404, ErrorCode.PROJECT_NOT_FOUND, "Project not found")
    if not can_manage_project(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    duplicated = (
        db.query(ScheduleTask)
        .filter(
            ScheduleTask.project_id == task.project_id,
            ScheduleTask.name == payload.name.strip(),
            ScheduleTask.id != task.id,
        )
        .first()
    )
    if duplicated:
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "Schedule task name already exists")

    task.name = payload.name.strip()
    task.cron_expr = payload.cron_expr.strip()
    task.timezone = payload.timezone.strip()
    task.enabled = 1 if payload.enabled else 0
    task.target_type = payload.target_type
    task.target_id = payload.target_id
    task.payload = _to_payload_text(payload.payload)
    task.updated_at = int(time.time())
    db.commit()
    db.refresh(task)

    create_audit_log(
        db=db,
        request=request,
        action="schedule_task.update",
        resource_type="schedule_task",
        resource_id=str(task.id),
        user_id=user.id,
        details={"name": task.name},
    )
    return _to_response(task)


@router.delete("/{task_id}", response_model=MessageResponse)
def delete_schedule_task(
    task_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    task = db.query(ScheduleTask).filter(ScheduleTask.id == task_id).first()
    if not task:
        raise AppException(404, ErrorCode.SCHEDULE_TASK_NOT_FOUND, "Schedule task not found")

    project = db.query(Project).filter(Project.id == task.project_id).first()
    if not project:
        raise AppException(404, ErrorCode.PROJECT_NOT_FOUND, "Project not found")
    if not can_manage_project(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    db.delete(task)
    db.commit()

    create_audit_log(
        db=db,
        request=request,
        action="schedule_task.delete",
        resource_type="schedule_task",
        resource_id=str(task_id),
        user_id=user.id,
    )
    return MessageResponse(message="Schedule task deleted")


@router.post("/{task_id}/trigger", response_model=ScheduleTaskTriggerResponse)
def trigger_schedule_task(
    task_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ScheduleTaskTriggerResponse:
    task = db.query(ScheduleTask).filter(ScheduleTask.id == task_id).first()
    if not task:
        raise AppException(404, ErrorCode.SCHEDULE_TASK_NOT_FOUND, "Schedule task not found")

    project = db.query(Project).filter(Project.id == task.project_id).first()
    if not project:
        raise AppException(404, ErrorCode.PROJECT_NOT_FOUND, "Project not found")
    if not can_manage_project(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    if task.enabled != 1:
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "Schedule task is disabled")

    payload = _parse_payload(task.payload)
    run_type = str(payload.get("run_type", "api")).lower()
    if run_type not in {"api", "web"}:
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "Invalid run_type in schedule payload")
    try:
        priority = int(payload.get("priority", 5))
    except (TypeError, ValueError):
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "Invalid priority in schedule payload")
    if priority < 1 or priority > 10:
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "priority must be between 1 and 10")

    if task.target_type not in {"test_case", "test_suite"}:
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "Unsupported target_type for queue trigger")
    if task.target_id is None:
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "target_id is required for queue trigger")

    queue_item = RunQueue(
        project_id=task.project_id,
        run_type=run_type,
        target_type=task.target_type,
        target_id=task.target_id,
        status="queued",
        priority=priority,
        payload=_to_payload_text(payload),
        scheduled_by="scheduler",
        created_at=int(time.time()),
    )
    db.add(queue_item)
    db.commit()
    db.refresh(queue_item)

    create_audit_log(
        db=db,
        request=request,
        action="schedule_task.trigger",
        resource_type="schedule_task",
        resource_id=str(task.id),
        user_id=user.id,
        details={"queue_item_id": queue_item.id, "run_type": run_type},
    )

    return ScheduleTaskTriggerResponse(
        schedule_task_id=task.id,
        queue_item_id=queue_item.id,
        status=queue_item.status,
    )
