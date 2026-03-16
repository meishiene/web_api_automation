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
from app.models.web_test_case import WebTestCase
from app.models.web_test_run import WebTestRun
from app.schemas.web_test_run import WebTestRunDetailResponse, WebTestRunResponse
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

    now = int(time.time())
    run = WebTestRun(
        project_id=case.project_id,
        web_test_case_id=case.id,
        triggered_by=user.id,
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
        created_by=user.id,
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
