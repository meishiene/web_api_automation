from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.dependencies import get_current_user
from app.errors import AppException, ErrorCode
from app.models.api_batch_run import ApiBatchRun
from app.models.api_batch_run_item import ApiBatchRunItem
from app.models.api_test_case import ApiTestCase
from app.models.api_test_suite import ApiTestSuite
from app.models.api_test_suite_case import ApiTestSuiteCase
from app.models.project import Project
from app.models.project_environment import ProjectEnvironment
from app.models.test_run import TestRun
from app.models.user import User
from app.schemas.batch_run import BatchRunDetailResponse, BatchRunResponse, SuiteRunRequest
from app.schemas.test_run import TestRunResponse
from app.services.access_control import can_execute_test_run, can_view_test_run
from app.services.audit_service import create_audit_log
from app.services.test_executor import execute_test
from app.services.variable_resolver import resolve_runtime_variables

router = APIRouter()


def _persist_test_run(db: Session, case_id: int, result: dict) -> TestRun:
    test_run = TestRun(
        test_case_id=case_id,
        status=result["status"],
        actual_status=result["actual_status"],
        actual_body=result["actual_body"],
        error_message=result.get("error_message"),
        duration_ms=result.get("duration_ms"),
        created_at=int(__import__("time").time()),
    )
    db.add(test_run)
    db.flush()
    return test_run


@router.post("/test-cases/{case_id}/run", response_model=TestRunResponse)
async def run_test_case(
    case_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TestRunResponse:
    test_case = db.query(ApiTestCase).join(Project).filter(ApiTestCase.id == case_id).first()

    if not test_case:
        raise AppException(404, ErrorCode.TEST_CASE_NOT_FOUND, "Test case not found")
    if not can_execute_test_run(db, user, test_case.project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    result = await execute_test(test_case)
    test_run = _persist_test_run(db, case_id, result)
    db.commit()
    db.refresh(test_run)

    create_audit_log(
        db=db,
        request=request,
        action="test_run.execute",
        resource_type="api_test_case",
        resource_id=str(case_id),
        user_id=user.id,
        details={"run_id": test_run.id, "status": test_run.status},
    )

    return test_run


@router.post("/suites/{suite_id}/run", response_model=BatchRunResponse)
async def run_test_suite(
    suite_id: int,
    payload: SuiteRunRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BatchRunResponse:
    suite = db.query(ApiTestSuite).join(Project).filter(ApiTestSuite.id == suite_id).first()
    if not suite:
        raise AppException(404, ErrorCode.TEST_SUITE_NOT_FOUND, "Test suite not found")
    if not can_execute_test_run(db, user, suite.project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    environment = None
    if payload.environment_id is not None:
        environment = (
            db.query(ProjectEnvironment)
            .filter(ProjectEnvironment.id == payload.environment_id)
            .first()
        )
        if not environment or environment.project_id != suite.project_id:
            raise AppException(404, ErrorCode.ENVIRONMENT_NOT_FOUND, "Environment not found")

    links = (
        db.query(ApiTestSuiteCase)
        .filter(ApiTestSuiteCase.suite_id == suite_id)
        .order_by(ApiTestSuiteCase.order_index.asc(), ApiTestSuiteCase.id.asc())
        .all()
    )
    if not links:
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "Test suite has no test cases")

    now = int(__import__("time").time())
    batch = ApiBatchRun(
        project_id=suite.project_id,
        suite_id=suite.id,
        environment_id=payload.environment_id,
        triggered_by=user.id,
        status="running",
        total_cases=len(links),
        passed_cases=0,
        failed_cases=0,
        error_cases=0,
        started_at=now,
        created_at=now,
    )
    db.add(batch)
    db.flush()

    runtime_variables = resolve_runtime_variables(db, suite.project_id, payload.environment_id)

    for link in links:
        result = await execute_test(link.test_case, runtime_variables=runtime_variables)
        test_run = _persist_test_run(db, link.test_case_id, result)

        item = ApiBatchRunItem(
            batch_run_id=batch.id,
            test_case_id=link.test_case_id,
            test_run_id=test_run.id,
            order_index=link.order_index,
            status=result["status"],
            error_message=result.get("error_message"),
            created_at=int(__import__("time").time()),
        )
        db.add(item)

        if result["status"] == "success":
            batch.passed_cases += 1
            runtime_variables.update(result.get("extracted_variables") or {})
        elif result["status"] == "failed":
            batch.failed_cases += 1
        else:
            batch.error_cases += 1

    if batch.error_cases > 0:
        batch.status = "error"
    elif batch.failed_cases > 0:
        batch.status = "failed"
    else:
        batch.status = "success"

    batch.finished_at = int(__import__("time").time())
    db.commit()
    db.refresh(batch)

    create_audit_log(
        db=db,
        request=request,
        action="test_suite.run",
        resource_type="api_test_suite",
        resource_id=str(suite.id),
        user_id=user.id,
        details={
            "batch_run_id": batch.id,
            "status": batch.status,
            "total_cases": batch.total_cases,
            "passed_cases": batch.passed_cases,
            "failed_cases": batch.failed_cases,
            "error_cases": batch.error_cases,
        },
    )

    return batch


@router.get("/project/{project_id}", response_model=List[TestRunResponse])
def get_test_runs(
    project_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[TestRunResponse]:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise AppException(404, ErrorCode.PROJECT_NOT_FOUND, "Project not found")
    if not can_view_test_run(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    return db.query(TestRun).join(ApiTestCase).filter(ApiTestCase.project_id == project_id).all()


@router.get("/batches/project/{project_id}", response_model=List[BatchRunResponse])
def list_batch_runs(
    project_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[BatchRunResponse]:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise AppException(404, ErrorCode.PROJECT_NOT_FOUND, "Project not found")
    if not can_view_test_run(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    return (
        db.query(ApiBatchRun)
        .filter(ApiBatchRun.project_id == project_id)
        .order_by(ApiBatchRun.id.desc())
        .all()
    )


@router.get("/batches/{batch_id}", response_model=BatchRunDetailResponse)
def get_batch_run_detail(
    batch_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BatchRunDetailResponse:
    batch = db.query(ApiBatchRun).join(Project).filter(ApiBatchRun.id == batch_id).first()
    if not batch:
        raise AppException(404, ErrorCode.BATCH_RUN_NOT_FOUND, "Batch run not found")
    if not can_view_test_run(db, user, batch.project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    items = (
        db.query(ApiBatchRunItem)
        .filter(ApiBatchRunItem.batch_run_id == batch_id)
        .order_by(ApiBatchRunItem.order_index.asc(), ApiBatchRunItem.id.asc())
        .all()
    )

    return BatchRunDetailResponse(
        id=batch.id,
        project_id=batch.project_id,
        suite_id=batch.suite_id,
        environment_id=batch.environment_id,
        triggered_by=batch.triggered_by,
        status=batch.status,
        total_cases=batch.total_cases,
        passed_cases=batch.passed_cases,
        failed_cases=batch.failed_cases,
        error_cases=batch.error_cases,
        started_at=batch.started_at,
        finished_at=batch.finished_at,
        created_at=batch.created_at,
        items=items,
    )
