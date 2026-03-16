import time
from typing import Any, Dict, List, Set

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

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
from app.schemas.batch_run import BatchRunDetailResponse, BatchRunItemResponse, BatchRunResponse, SuiteRunRequest
from app.schemas.test_run import TestRunDetailResponse, TestRunResponse
from app.services.access_control import can_execute_test_run, can_view_test_run
from app.services.audit_service import create_audit_log
from app.services.test_executor import execute_test
from app.services.variable_resolver import resolve_runtime_variables

router = APIRouter()

_IDEMPOTENCY_TTL_SECONDS = 1800
_idempotency_cache: Dict[str, tuple[int, int]] = {}


def _persist_test_run(db: Session, case_id: int, result: dict) -> TestRun:
    test_run = TestRun(
        test_case_id=case_id,
        status=result["status"],
        actual_status=result["actual_status"],
        actual_body=result["actual_body"],
        error_message=result.get("error_message"),
        duration_ms=result.get("duration_ms"),
        created_at=int(time.time()),
    )
    db.add(test_run)
    db.flush()
    return test_run


def _validate_retry_options(retry_count: int, retry_on: Set[str]) -> None:
    allowed = {"failed", "error"}
    if not retry_on:
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "retry_on cannot be empty")
    unsupported = retry_on - allowed
    if unsupported:
        raise AppException(400, ErrorCode.VALIDATION_ERROR, f"retry_on contains unsupported status: {sorted(unsupported)}")
    if retry_count == 0 and retry_on != {"error"}:
        # Avoid confusion for callers: custom retry_on only has effect with retry_count > 0.
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "retry_on requires retry_count > 0")


def _purge_expired_idempotency(now_ts: int) -> None:
    expired_keys = [
        key for key, (_batch_id, created_at) in _idempotency_cache.items() if now_ts - created_at > _IDEMPOTENCY_TTL_SECONDS
    ]
    for key in expired_keys:
        _idempotency_cache.pop(key, None)


def _build_idempotency_cache_key(
    user_id: int,
    suite_id: int,
    environment_id: int | None,
    retry_count: int,
    retry_on: Set[str],
    idempotency_key: str,
) -> str:
    retry_signature = ",".join(sorted(retry_on))
    return f"{user_id}:{suite_id}:{environment_id}:{retry_count}:{retry_signature}:{idempotency_key}"


async def _execute_with_retry(
    test_case: ApiTestCase,
    runtime_variables: Dict[str, Any],
    retry_count: int,
    retry_on: Set[str],
) -> tuple[dict, int]:
    attempts = 0
    last_result: dict | None = None
    while attempts <= retry_count:
        last_result = await execute_test(test_case, runtime_variables=runtime_variables)
        if last_result.get("status") not in retry_on:
            break
        if attempts >= retry_count:
            break
        attempts += 1
    return last_result or {}, attempts


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

    retry_on = set(payload.retry_on or ["error"])
    _validate_retry_options(payload.retry_count, retry_on)

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

    now = int(time.time())
    _purge_expired_idempotency(now)

    cache_key = None
    if payload.idempotency_key:
        normalized = payload.idempotency_key.strip()
        cache_key = _build_idempotency_cache_key(
            user_id=user.id,
            suite_id=suite.id,
            environment_id=payload.environment_id,
            retry_count=payload.retry_count,
            retry_on=retry_on,
            idempotency_key=normalized,
        )
        cached = _idempotency_cache.get(cache_key)
        if cached:
            cached_batch_id, _cached_at = cached
            existing = db.query(ApiBatchRun).filter(ApiBatchRun.id == cached_batch_id).first()
            if existing:
                create_audit_log(
                    db=db,
                    request=request,
                    action="test_suite.run",
                    resource_type="api_test_suite",
                    resource_id=str(suite.id),
                    user_id=user.id,
                    details={"reused_batch_id": existing.id, "idempotency_key": normalized},
                )
                return existing
            _idempotency_cache.pop(cache_key, None)

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
        result, retry_used = await _execute_with_retry(
            test_case=link.test_case,
            runtime_variables=runtime_variables,
            retry_count=payload.retry_count,
            retry_on=retry_on,
        )
        test_run = _persist_test_run(db, link.test_case_id, result)

        item_error = result.get("error_message")
        if retry_used > 0 and item_error:
            item_error = f"{item_error} (retried {retry_used} time(s))"

        item = ApiBatchRunItem(
            batch_run_id=batch.id,
            test_case_id=link.test_case_id,
            test_run_id=test_run.id,
            order_index=link.order_index,
            status=result["status"],
            error_message=item_error,
            created_at=int(time.time()),
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

    batch.finished_at = int(time.time())
    db.commit()
    db.refresh(batch)

    if cache_key:
        _idempotency_cache[cache_key] = (batch.id, int(time.time()))

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
            "retry_count": payload.retry_count,
            "retry_on": sorted(list(retry_on)),
            "idempotency_key": payload.idempotency_key,
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

    item_rows = (
        db.query(ApiBatchRunItem, ApiTestCase, TestRun)
        .join(ApiTestCase, ApiTestCase.id == ApiBatchRunItem.test_case_id)
        .outerjoin(TestRun, TestRun.id == ApiBatchRunItem.test_run_id)
        .filter(ApiBatchRunItem.batch_run_id == batch_id)
        .order_by(ApiBatchRunItem.order_index.asc(), ApiBatchRunItem.id.asc())
        .all()
    )

    items = [
        BatchRunItemResponse(
            id=item.id,
            batch_run_id=item.batch_run_id,
            test_case_id=item.test_case_id,
            test_case_name=test_case.name,
            test_case_method=test_case.method,
            test_case_url=test_case.url,
            test_run_id=item.test_run_id,
            order_index=item.order_index,
            status=item.status,
            actual_status=(test_run.actual_status if test_run else None),
            duration_ms=(test_run.duration_ms if test_run else None),
            error_message=item.error_message,
            created_at=item.created_at,
        )
        for item, test_case, test_run in item_rows
    ]

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


@router.get("/{run_id}", response_model=TestRunDetailResponse)
def get_test_run_detail(
    run_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TestRunDetailResponse:
    run = (
        db.query(TestRun)
        .join(ApiTestCase)
        .join(Project)
        .filter(TestRun.id == run_id)
        .first()
    )
    if not run:
        raise AppException(404, ErrorCode.TEST_RUN_NOT_FOUND, "Test run not found")
    if not can_view_test_run(db, user, run.test_case.project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    return TestRunDetailResponse(
        id=run.id,
        test_case_id=run.test_case_id,
        status=run.status,
        actual_status=run.actual_status,
        actual_body=run.actual_body,
        error_message=run.error_message,
        duration_ms=run.duration_ms,
        created_at=run.created_at,
        test_case_name=run.test_case.name,
        test_case_method=run.test_case.method,
        test_case_url=run.test_case.url,
        test_case_expected_status=run.test_case.expected_status,
    )
