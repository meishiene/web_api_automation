import json
import time
from typing import Optional

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.errors import AppException, ErrorCode
from app.models.project import Project
from app.models.run_queue import RunQueue
from app.models.user import User
from app.models.worker_heartbeat import WorkerHeartbeat
from app.schemas.queue_worker import (
    QueueClaimRequest,
    QueueClaimResponse,
    QueueCompleteRequest,
    QueueCompleteResponse,
    QueueListResponse,
    RunQueueItemResponse,
    WorkerExecuteOnceRequest,
    WorkerExecuteOnceResponse,
    WorkerHeartbeatRequest,
    WorkerHeartbeatListResponse,
    WorkerHeartbeatResponse,
)
from app.services.access_control import can_manage_project, can_view_project
from app.services.audit_service import create_audit_log
from app.services.queue_worker_runtime import (
    claim_one_queue_item,
    consume_queue_item_once,
    upsert_worker_heartbeat,
)

router = APIRouter()


def _project_or_404(db: Session, project_id: int) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise AppException(404, ErrorCode.PROJECT_NOT_FOUND, "Project not found")
    return project


def _queue_item_response(queue_item: RunQueue) -> RunQueueItemResponse:
    return RunQueueItemResponse.model_validate(queue_item)


@router.get("/project/{project_id}", response_model=QueueListResponse)
def list_queue_items(
    project_id: int,
    status: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> QueueListResponse:
    project = _project_or_404(db, project_id)
    if not can_view_project(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    query = db.query(RunQueue).filter(RunQueue.project_id == project_id)
    if status:
        query = query.filter(RunQueue.status == status)
    records = query.order_by(RunQueue.created_at.desc(), RunQueue.id.desc()).all()
    return QueueListResponse(
        items=[_queue_item_response(item) for item in records],
        total=len(records),
    )


@router.get("/worker/heartbeats/project/{project_id}", response_model=WorkerHeartbeatListResponse)
def list_worker_heartbeats(
    project_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WorkerHeartbeatListResponse:
    project = _project_or_404(db, project_id)
    if not can_view_project(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    records = (
        db.query(WorkerHeartbeat)
        .filter(WorkerHeartbeat.project_id == project_id)
        .order_by(WorkerHeartbeat.last_heartbeat_at.desc(), WorkerHeartbeat.id.desc())
        .all()
    )
    return WorkerHeartbeatListResponse(
        items=[WorkerHeartbeatResponse.model_validate(item) for item in records],
        total=len(records),
    )


@router.get("/{queue_item_id}", response_model=RunQueueItemResponse)
def get_queue_item_detail(
    queue_item_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RunQueueItemResponse:
    queue_item = db.query(RunQueue).filter(RunQueue.id == queue_item_id).first()
    if not queue_item:
        raise AppException(404, ErrorCode.RUN_QUEUE_ITEM_NOT_FOUND, "Queue item not found")

    project = _project_or_404(db, queue_item.project_id)
    if not can_view_project(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")
    return _queue_item_response(queue_item)


@router.post("/claim", response_model=QueueClaimResponse)
def claim_queue_item(
    payload: QueueClaimRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> QueueClaimResponse:
    project = _project_or_404(db, payload.project_id)
    if not can_manage_project(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    queue_item = claim_one_queue_item(
        db=db,
        project_id=payload.project_id,
        worker_id=payload.worker_id.strip(),
        run_type=payload.run_type,
    )
    if not queue_item:
        return QueueClaimResponse(claimed=False, queue_item=None)

    create_audit_log(
        db=db,
        request=request,
        action="run_queue.claim",
        resource_type="run_queue",
        resource_id=str(queue_item.id),
        user_id=user.id,
        details={"worker_id": payload.worker_id, "run_type": payload.run_type},
    )

    return QueueClaimResponse(claimed=True, queue_item=_queue_item_response(queue_item))


@router.post("/{queue_item_id}/complete", response_model=QueueCompleteResponse)
def complete_queue_item(
    queue_item_id: int,
    payload: QueueCompleteRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> QueueCompleteResponse:
    queue_item = db.query(RunQueue).filter(RunQueue.id == queue_item_id).first()
    if not queue_item:
        raise AppException(404, ErrorCode.RUN_QUEUE_ITEM_NOT_FOUND, "Queue item not found")

    project = _project_or_404(db, queue_item.project_id)
    if not can_manage_project(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    if queue_item.status not in {"queued", "running"}:
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "Queue item is not in executable state")
    if queue_item.worker_id and queue_item.worker_id != payload.worker_id:
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "Queue item belongs to another worker")

    now = int(time.time())
    if queue_item.started_at is None:
        queue_item.started_at = now
    queue_item.worker_id = payload.worker_id
    queue_item.status = payload.status
    queue_item.finished_at = now
    if payload.result:
        queue_item.payload = json.dumps(
            {
                "input": _safe_json_loads(queue_item.payload),
                "result": payload.result,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    db.commit()
    db.refresh(queue_item)

    create_audit_log(
        db=db,
        request=request,
        action="run_queue.complete",
        resource_type="run_queue",
        resource_id=str(queue_item.id),
        user_id=user.id,
        details={"worker_id": payload.worker_id, "status": payload.status},
    )

    return QueueCompleteResponse(
        queue_item_id=queue_item.id,
        status=queue_item.status,
        finished_at=queue_item.finished_at or now,
    )


@router.post("/worker/execute-once", response_model=WorkerExecuteOnceResponse)
async def worker_execute_once(
    payload: WorkerExecuteOnceRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WorkerExecuteOnceResponse:
    project = _project_or_404(db, payload.project_id)
    if not can_manage_project(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    result = await consume_queue_item_once(
        db=db,
        project_id=payload.project_id,
        worker_id=payload.worker_id.strip(),
        run_type=payload.run_type,
    )
    if not result.get("executed"):
        return WorkerExecuteOnceResponse(executed=False)

    create_audit_log(
        db=db,
        request=request,
        action="run_queue.execute_once",
        resource_type="run_queue",
        resource_id=str(result["queue_item_id"]),
        user_id=user.id,
        details={
            "worker_id": payload.worker_id,
            "result_status": result.get("status"),
        },
    )

    return WorkerExecuteOnceResponse(
        executed=True,
        queue_item_id=result["queue_item_id"],
        status=result.get("status"),
    )


@router.post("/worker/heartbeat", response_model=WorkerHeartbeatResponse)
def worker_heartbeat(
    payload: WorkerHeartbeatRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WorkerHeartbeatResponse:
    project = _project_or_404(db, payload.project_id)
    if not can_manage_project(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    if payload.current_queue_item_id is not None:
        queue_item = db.query(RunQueue).filter(RunQueue.id == payload.current_queue_item_id).first()
        if not queue_item or queue_item.project_id != payload.project_id:
            raise AppException(400, ErrorCode.VALIDATION_ERROR, "current_queue_item_id not found in project")

    heartbeat = upsert_worker_heartbeat(
        db=db,
        project_id=payload.project_id,
        worker_id=payload.worker_id.strip(),
        run_type=payload.run_type,
        status=payload.status,
        current_queue_item_id=payload.current_queue_item_id,
    )

    create_audit_log(
        db=db,
        request=request,
        action="worker.heartbeat",
        resource_type="worker_heartbeat",
        resource_id=str(heartbeat.id),
        user_id=user.id,
        details={"worker_id": payload.worker_id, "status": payload.status},
    )

    return WorkerHeartbeatResponse.model_validate(heartbeat)


def _safe_json_loads(raw: Optional[str]) -> dict:
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}
