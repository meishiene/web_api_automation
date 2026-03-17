from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.errors import AppException, ErrorCode
from app.models.api_test_case import ApiTestCase
from app.models.project import Project
from app.models.test_run import TestRun
from app.models.user import User
from app.models.web_test_case import WebTestCase
from app.models.web_test_run import WebTestRun
from app.schemas.reporting import (
    FailureGovernanceListResponse,
    ProjectReportSummaryResponse,
    ProjectReportTrendResponse,
)
from app.services.access_control import can_view_test_run
from app.services.audit_service import create_audit_log
from app.services.reporting_summary import (
    build_failure_governance_items,
    build_project_report_summary,
    build_project_trends,
    build_report_inputs_from_rows,
)

router = APIRouter()
_MAX_REPORT_WINDOW_SECONDS = 180 * 24 * 3600


def _validate_report_time_window(created_from: int | None, created_to: int | None) -> None:
    if created_from is None or created_to is None:
        return
    if created_from > created_to:
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "created_from cannot be greater than created_to")
    if created_to - created_from > _MAX_REPORT_WINDOW_SECONDS:
        raise AppException(
            400,
            ErrorCode.VALIDATION_ERROR,
            "created_to - created_from cannot exceed 180 days",
        )


@router.get("/project/{project_id}/summary", response_model=ProjectReportSummaryResponse)
def get_project_report_summary(
    project_id: int,
    request: Request,
    run_type: str | None = Query(default=None, pattern="^(api|web)$"),
    created_from: int | None = Query(default=None, ge=0),
    created_to: int | None = Query(default=None, ge=0),
    top_n: int = Query(default=5, ge=1, le=20),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectReportSummaryResponse:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise AppException(404, ErrorCode.PROJECT_NOT_FOUND, "Project not found")
    if not can_view_test_run(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    _validate_report_time_window(created_from=created_from, created_to=created_to)

    api_rows = []
    web_rows = []
    if run_type in (None, "api"):
        api_query = (
            db.query(TestRun, ApiTestCase)
            .join(ApiTestCase, ApiTestCase.id == TestRun.test_case_id)
            .filter(ApiTestCase.project_id == project_id)
        )
        if created_from is not None:
            api_query = api_query.filter(TestRun.created_at >= created_from)
        if created_to is not None:
            api_query = api_query.filter(TestRun.created_at <= created_to)
        api_rows = api_query.all()

    if run_type in (None, "web"):
        web_query = (
            db.query(WebTestRun, WebTestCase)
            .join(WebTestCase, WebTestCase.id == WebTestRun.web_test_case_id)
            .filter(WebTestRun.project_id == project_id)
        )
        if created_from is not None:
            web_query = web_query.filter(WebTestRun.created_at >= created_from)
        if created_to is not None:
            web_query = web_query.filter(WebTestRun.created_at <= created_to)
        web_rows = web_query.all()

    report_inputs = build_report_inputs_from_rows(
        api_rows=api_rows,
        web_rows=web_rows,
        project_id=project_id,
    )

    payload = build_project_report_summary(project_id=project_id, items=report_inputs, top_n=top_n)
    create_audit_log(
        db=db,
        request=request,
        action="report.summary.read",
        resource_type="project_report",
        resource_id=str(project_id),
        user_id=user.id,
        details={
            "run_type": run_type,
            "created_from": created_from,
            "created_to": created_to,
            "top_n": top_n,
            "total_count": payload.get("total_count", 0),
        },
    )
    return ProjectReportSummaryResponse(**payload)


@router.get("/project/{project_id}/trends", response_model=ProjectReportTrendResponse)
def get_project_report_trends(
    project_id: int,
    request: Request,
    granularity: str = Query(default="day", pattern="^(day|week)$"),
    run_type: str | None = Query(default=None, pattern="^(api|web)$"),
    created_from: int | None = Query(default=None, ge=0),
    created_to: int | None = Query(default=None, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectReportTrendResponse:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise AppException(404, ErrorCode.PROJECT_NOT_FOUND, "Project not found")
    if not can_view_test_run(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    _validate_report_time_window(created_from=created_from, created_to=created_to)

    api_rows = []
    web_rows = []
    if run_type in (None, "api"):
        api_query = (
            db.query(TestRun, ApiTestCase)
            .join(ApiTestCase, ApiTestCase.id == TestRun.test_case_id)
            .filter(ApiTestCase.project_id == project_id)
        )
        if created_from is not None:
            api_query = api_query.filter(TestRun.created_at >= created_from)
        if created_to is not None:
            api_query = api_query.filter(TestRun.created_at <= created_to)
        api_rows = api_query.all()

    if run_type in (None, "web"):
        web_query = (
            db.query(WebTestRun, WebTestCase)
            .join(WebTestCase, WebTestCase.id == WebTestRun.web_test_case_id)
            .filter(WebTestRun.project_id == project_id)
        )
        if created_from is not None:
            web_query = web_query.filter(WebTestRun.created_at >= created_from)
        if created_to is not None:
            web_query = web_query.filter(WebTestRun.created_at <= created_to)
        web_rows = web_query.all()

    report_inputs = build_report_inputs_from_rows(
        api_rows=api_rows,
        web_rows=web_rows,
        project_id=project_id,
    )

    payload = build_project_trends(
        project_id=project_id,
        items=report_inputs,
        granularity=granularity,  # type: ignore[arg-type]
    )
    create_audit_log(
        db=db,
        request=request,
        action="report.trends.read",
        resource_type="project_report",
        resource_id=str(project_id),
        user_id=user.id,
        details={
            "granularity": granularity,
            "run_type": run_type,
            "created_from": created_from,
            "created_to": created_to,
            "bucket_count": len(payload.get("items", [])),
        },
    )
    return ProjectReportTrendResponse(**payload)


@router.get("/project/{project_id}/failures", response_model=FailureGovernanceListResponse)
def get_project_report_failures(
    project_id: int,
    request: Request,
    run_type: str | None = Query(default=None, pattern="^(api|web)$"),
    failure_category: str | None = Query(
        default=None,
        pattern="^(assertion_failure|timeout|network_error|execution_error|test_failure)$",
    ),
    created_from: int | None = Query(default=None, ge=0),
    created_to: int | None = Query(default=None, ge=0),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FailureGovernanceListResponse:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise AppException(404, ErrorCode.PROJECT_NOT_FOUND, "Project not found")
    if not can_view_test_run(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    _validate_report_time_window(created_from=created_from, created_to=created_to)

    api_rows = []
    web_rows = []
    if run_type in (None, "api"):
        api_query = (
            db.query(TestRun, ApiTestCase)
            .join(ApiTestCase, ApiTestCase.id == TestRun.test_case_id)
            .filter(ApiTestCase.project_id == project_id)
        )
        if created_from is not None:
            api_query = api_query.filter(TestRun.created_at >= created_from)
        if created_to is not None:
            api_query = api_query.filter(TestRun.created_at <= created_to)
        api_rows = api_query.all()

    if run_type in (None, "web"):
        web_query = (
            db.query(WebTestRun, WebTestCase)
            .join(WebTestCase, WebTestCase.id == WebTestRun.web_test_case_id)
            .filter(WebTestRun.project_id == project_id)
        )
        if created_from is not None:
            web_query = web_query.filter(WebTestRun.created_at >= created_from)
        if created_to is not None:
            web_query = web_query.filter(WebTestRun.created_at <= created_to)
        web_rows = web_query.all()

    report_inputs = build_report_inputs_from_rows(
        api_rows=api_rows,
        web_rows=web_rows,
        project_id=project_id,
    )
    payload = build_failure_governance_items(
        items=report_inputs,
        run_type=run_type,
        failure_category=failure_category,
        page=page,
        page_size=page_size,
    )
    create_audit_log(
        db=db,
        request=request,
        action="report.failures.read",
        resource_type="project_report",
        resource_id=str(project_id),
        user_id=user.id,
        details={
            "run_type": run_type,
            "failure_category": failure_category,
            "created_from": created_from,
            "created_to": created_to,
            "page": page,
            "page_size": page_size,
            "total": payload.get("total", 0),
        },
    )
    return FailureGovernanceListResponse(**payload)
