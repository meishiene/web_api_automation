import json
import time
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.errors import AppException, ErrorCode
from app.models.project import Project
from app.models.user import User
from app.models.web_batch_run import WebBatchRun
from app.models.web_batch_run_item import WebBatchRunItem
from app.models.web_test_case import WebTestCase
from app.models.web_test_run import WebTestRun
from app.schemas.common import TestCaseIdCollectionRequest
from app.schemas.web_test_run import (
    WebBatchRunDetailResponse,
    WebBatchRunResponse,
    WebBatchRunItemResponse,
    WebTestRunDetailResponse,
    WebTestRunResponse,
)
from app.services.access_control import can_execute_web_test_run, can_view_web_test_run
from app.services.audit_service import create_audit_log
from app.services.execution_contract import ExecutionAdapter
from app.services.execution_orchestrator import run_execution_task
from app.services.web_executor import execute_web_test_case

router = APIRouter()


def _to_json_text(payload: Any) -> str | None:
    if payload is None:
        return None
    return json.dumps(payload, ensure_ascii=False)


def _from_json_array(payload: str | None) -> List[Any]:
    if not payload:
        return []
    try:
        value = json.loads(payload)
    except json.JSONDecodeError:
        return []
    return value if isinstance(value, list) else []


def _to_response(run: WebTestRun) -> WebTestRunResponse:
    return WebTestRunResponse(
        id=run.id,
        project_id=run.project_id,
        web_test_case_id=run.web_test_case_id,
        status=run.status,
        error_message=run.error_message,
        duration_ms=run.duration_ms,
        artifact_dir=run.artifact_dir,
        artifacts=[str(item) for item in _from_json_array(run.artifacts_json)],
        created_at=run.created_at,
    )


def _to_batch_response(batch: WebBatchRun) -> WebBatchRunResponse:
    return WebBatchRunResponse(
        id=batch.id,
        project_id=batch.project_id,
        triggered_by=batch.triggered_by,
        status=batch.status,
        total_cases=batch.total_cases,
        passed_cases=batch.passed_cases,
        failed_cases=batch.failed_cases,
        error_cases=batch.error_cases,
        started_at=batch.started_at,
        finished_at=batch.finished_at,
        created_at=batch.created_at,
    )


def _load_project_or_404(db: Session, project_id: int) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise AppException(404, ErrorCode.PROJECT_NOT_FOUND, "Project not found")
    return project


def _load_web_test_cases_by_ids(db: Session, project_id: int, case_ids: List[int]) -> List[WebTestCase]:
    records = (
        db.query(WebTestCase)
        .filter(WebTestCase.project_id == project_id, WebTestCase.id.in_(case_ids))
        .all()
    )
    record_map = {item.id: item for item in records}
    missing_ids = [case_id for case_id in case_ids if case_id not in record_map]
    if missing_ids:
        raise AppException(
            404,
            ErrorCode.WEB_TEST_CASE_NOT_FOUND,
            "Web test case not found",
            details={"missing_ids": missing_ids},
        )
    return [record_map[case_id] for case_id in case_ids]


def _resolve_batch_status(failed_cases: int, error_cases: int) -> str:
    if error_cases > 0:
        return "error"
    if failed_cases > 0:
        return "failed"
    return "success"


async def _execute_web_test_case_run(db: Session, case: WebTestCase, user_id: int) -> WebTestRun:
    now = int(time.time())
    run = WebTestRun(
        project_id=case.project_id,
        web_test_case_id=case.id,
        triggered_by=user_id,
        status="running",
        started_at=now,
        created_at=now,
    )
    db.add(run)
    db.flush()

    artifact_dir_path = Path("artifacts") / "web-test-runs" / str(run.id)
    run.artifact_dir = str(artifact_dir_path)
    artifact_dir_path.mkdir(parents=True, exist_ok=True)
    db.flush()

    class _WebCaseExecutionAdapter(ExecutionAdapter):
        async def execute(self) -> dict[str, Any]:
            return await execute_web_test_case(case, artifact_dir=run.artifact_dir)

    _task, _job, result = await run_execution_task(
        db=db,
        project_id=case.project_id,
        run_type="web",
        target_type="test_case",
        target_id=case.id,
        adapter=_WebCaseExecutionAdapter(),
        created_by=user_id,
        trigger_mode="manual",
        context={"artifact_dir": run.artifact_dir},
    )

    run.status = result.get("status", "error")
    run.error_message = result.get("error_message")
    run.duration_ms = result.get("duration_ms")
    run.step_logs_json = _to_json_text(result.get("step_logs", []))
    run.artifacts_json = _to_json_text(result.get("artifacts", []))
    run.finished_at = int(time.time())

    db.commit()
    db.refresh(run)
    return run


@router.post("/web-test-cases/{case_id}/run", response_model=WebTestRunResponse)
async def run_web_test_case(
    case_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WebTestRunResponse:
    case = db.query(WebTestCase).join(Project).filter(WebTestCase.id == case_id).first()
    if not case:
        raise AppException(404, ErrorCode.WEB_TEST_CASE_NOT_FOUND, "Web test case not found")
    if not can_execute_web_test_run(db, user, case.project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    run = await _execute_web_test_case_run(db=db, case=case, user_id=user.id)

    create_audit_log(
        db=db,
        request=request,
        action="web_test_run.execute",
        resource_type="web_test_case",
        resource_id=str(case.id),
        user_id=user.id,
        details={"run_id": run.id, "status": run.status},
    )
    return _to_response(run)


@router.post("/project/{project_id}/batch-run", response_model=WebBatchRunResponse)
async def run_selected_web_test_cases(
    project_id: int,
    payload: TestCaseIdCollectionRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WebBatchRunResponse:
    project = _load_project_or_404(db, project_id)
    if not can_execute_web_test_run(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    ordered_cases = _load_web_test_cases_by_ids(db, project_id, payload.test_case_ids)
    now = int(time.time())
    batch = WebBatchRun(
        project_id=project_id,
        triggered_by=user.id,
        status="running",
        total_cases=len(ordered_cases),
        passed_cases=0,
        failed_cases=0,
        error_cases=0,
        started_at=now,
        created_at=now,
    )
    db.add(batch)
    db.flush()

    audit_entries: list[tuple[int, WebTestRun]] = []
    passed_cases = 0
    failed_cases = 0
    error_cases = 0

    for index, case in enumerate(ordered_cases):
        run = await _execute_web_test_case_run(db=db, case=case, user_id=user.id)
        db.add(
            WebBatchRunItem(
                batch_run_id=batch.id,
                web_test_case_id=case.id,
                web_test_run_id=run.id,
                order_index=index,
                status=run.status,
                error_message=run.error_message,
                created_at=int(time.time()),
            )
        )
        audit_entries.append((case.id, run))

        if run.status == "success":
            passed_cases += 1
        elif run.status == "failed":
            failed_cases += 1
        else:
            error_cases += 1

    batch.passed_cases = passed_cases
    batch.failed_cases = failed_cases
    batch.error_cases = error_cases
    batch.status = _resolve_batch_status(failed_cases, error_cases)
    batch.finished_at = int(time.time())
    db.commit()
    db.refresh(batch)

    for case_id, run in audit_entries:
        create_audit_log(
            db=db,
            request=request,
            action="web_test_run.execute",
            resource_type="web_test_case",
            resource_id=str(case_id),
            user_id=user.id,
            details={"run_id": run.id, "status": run.status, "batch_mode": True, "batch_run_id": batch.id},
        )

    create_audit_log(
        db=db,
        request=request,
        action="web_test_run.batch_execute",
        resource_type="project",
        resource_id=str(project_id),
        user_id=user.id,
        details={
            "batch_run_id": batch.id,
            "test_case_ids": payload.test_case_ids,
            "total_cases": batch.total_cases,
            "passed_cases": passed_cases,
            "failed_cases": failed_cases,
            "error_cases": error_cases,
            "status": batch.status,
        },
    )
    return _to_batch_response(batch)


@router.get("/batches/project/{project_id}", response_model=List[WebBatchRunResponse])
def list_web_batch_runs(
    project_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[WebBatchRunResponse]:
    project = _load_project_or_404(db, project_id)
    if not can_view_web_test_run(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    records = (
        db.query(WebBatchRun)
        .filter(WebBatchRun.project_id == project_id)
        .order_by(WebBatchRun.id.desc())
        .all()
    )
    return [_to_batch_response(item) for item in records]


@router.get("/batches/{batch_id}", response_model=WebBatchRunDetailResponse)
def get_web_batch_run_detail(
    batch_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WebBatchRunDetailResponse:
    batch = db.query(WebBatchRun).join(Project).filter(WebBatchRun.id == batch_id).first()
    if not batch:
        raise AppException(404, ErrorCode.BATCH_RUN_NOT_FOUND, "Batch run not found")
    if not can_view_web_test_run(db, user, batch.project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    rows = (
        db.query(WebBatchRunItem, WebTestCase, WebTestRun)
        .join(WebTestCase, WebTestCase.id == WebBatchRunItem.web_test_case_id)
        .outerjoin(WebTestRun, WebTestRun.id == WebBatchRunItem.web_test_run_id)
        .filter(WebBatchRunItem.batch_run_id == batch_id)
        .order_by(WebBatchRunItem.order_index.asc(), WebBatchRunItem.id.asc())
        .all()
    )
    items = [
        WebBatchRunItemResponse(
            id=item.id,
            batch_run_id=item.batch_run_id,
            web_test_case_id=case.id,
            web_test_case_name=case.name,
            status=item.status,
            web_test_run_id=run.id if run else None,
            duration_ms=run.duration_ms if run else None,
            error_message=item.error_message or (run.error_message if run else None),
            created_at=item.created_at,
        )
        for item, case, run in rows
    ]
    return WebBatchRunDetailResponse(**_to_batch_response(batch).model_dump(), items=items)


@router.get("/project/{project_id}", response_model=List[WebTestRunResponse])
def list_web_test_runs(
    project_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[WebTestRunResponse]:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise AppException(404, ErrorCode.PROJECT_NOT_FOUND, "Project not found")
    if not can_view_web_test_run(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    records = (
        db.query(WebTestRun)
        .filter(WebTestRun.project_id == project_id)
        .order_by(WebTestRun.created_at.desc(), WebTestRun.id.desc())
        .all()
    )
    return [_to_response(item) for item in records]


@router.get("/{run_id}", response_model=WebTestRunDetailResponse)
def get_web_test_run_detail(
    run_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WebTestRunDetailResponse:
    run = db.query(WebTestRun).filter(WebTestRun.id == run_id).first()
    if not run:
        raise AppException(404, ErrorCode.WEB_TEST_RUN_NOT_FOUND, "Web test run not found")

    project = db.query(Project).filter(Project.id == run.project_id).first()
    if not project:
        raise AppException(404, ErrorCode.PROJECT_NOT_FOUND, "Project not found")
    if not can_view_web_test_run(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    case = db.query(WebTestCase).filter(WebTestCase.id == run.web_test_case_id).first()
    if not case:
        raise AppException(404, ErrorCode.WEB_TEST_CASE_NOT_FOUND, "Web test case not found")

    return WebTestRunDetailResponse(
        **_to_response(run).model_dump(),
        web_test_case_name=case.name,
        web_test_case_base_url=case.base_url,
        step_logs=[item for item in _from_json_array(run.step_logs_json) if isinstance(item, dict)],
    )
