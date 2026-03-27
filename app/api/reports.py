from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.errors import AppException, ErrorCode
from app.models.api_test_case import ApiTestCase
from app.models.integration_event import IntegrationEvent
from app.models.notification_delivery import NotificationDelivery
from app.models.project import Project
from app.models.run_queue import RunQueue
from app.models.test_run import TestRun
from app.models.user import User
from app.models.web_test_case import WebTestCase
from app.models.web_test_run import WebTestRun
from app.schemas.reporting import (
    FailureGovernanceListResponse,
    OperationsAlertItem,
    OperationsGuardrailStatus,
    OperationsOverviewResponse,
    OperationsProjectSignal,
    OperationsRetryTrendItem,
    ProjectReportSummaryResponse,
    ProjectReportTrendResponse,
)
from app.services.access_control import can_view_project, can_view_test_run
from app.services.audit_service import create_audit_log
from app.services.reporting_summary import (
    build_failure_governance_items,
    build_project_report_summary,
    build_project_trends,
    build_report_inputs_from_rows,
)

router = APIRouter()
_MAX_REPORT_WINDOW_SECONDS = 180 * 24 * 3600
_MAX_OPERATIONS_PROJECT_SIGNALS = 20
_OPERATIONS_ALERT_THRESHOLDS = {
    "retry_backlog": {"warning": 20, "critical": 50},
    "dead_letter_backlog": {"warning": 10, "critical": 20},
    "failed_backlog": {"warning": 30, "critical": 80},
}


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


def _day_bucket_start(ts: int) -> int:
    return int(datetime.fromtimestamp(ts, tz=timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).timestamp())


def _day_bucket_label(ts: int) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")


def _resolve_visible_projects(db: Session, user: User, project_ids: list[int] | None) -> list[Project]:
    if project_ids:
        projects = db.query(Project).filter(Project.id.in_(project_ids)).all()
        found_ids = {item.id for item in projects}
        missing_ids = [pid for pid in project_ids if pid not in found_ids]
        if missing_ids:
            raise AppException(404, ErrorCode.PROJECT_NOT_FOUND, "Project not found")
        for project in projects:
            if not can_view_project(db, user, project):
                raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")
        return projects

    return [project for project in db.query(Project).all() if can_view_project(db, user, project)]


def _build_operations_alerts(
    failed_backlog: int,
    dead_letter_backlog: int,
    retry_backlog: int,
) -> list[OperationsAlertItem]:
    metric_values = {
        "failed_backlog": failed_backlog,
        "dead_letter_backlog": dead_letter_backlog,
        "retry_backlog": retry_backlog,
    }
    messages = {
        "failed_backlog": "Failed backlog exceeded threshold",
        "dead_letter_backlog": "Dead-letter backlog exceeded threshold",
        "retry_backlog": "Retry backlog exceeded threshold",
    }

    alerts: list[OperationsAlertItem] = []
    for metric, actual in metric_values.items():
        critical_threshold = _OPERATIONS_ALERT_THRESHOLDS[metric]["critical"]
        warning_threshold = _OPERATIONS_ALERT_THRESHOLDS[metric]["warning"]
        if actual >= critical_threshold:
            alerts.append(
                OperationsAlertItem(
                    level="critical",
                    code=f"{metric}.critical",
                    message=messages[metric],
                    metric=metric,
                    threshold=critical_threshold,
                    actual=actual,
                )
            )
        elif actual >= warning_threshold:
            alerts.append(
                OperationsAlertItem(
                    level="warning",
                    code=f"{metric}.warning",
                    message=messages[metric],
                    metric=metric,
                    threshold=warning_threshold,
                    actual=actual,
                )
            )
    return alerts


@router.get("/operations/overview", response_model=OperationsOverviewResponse)
def get_operations_overview(
    request: Request,
    project_ids: list[int] | None = Query(default=None),
    days: int = Query(default=7, ge=1, le=30),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OperationsOverviewResponse:
    projects = _resolve_visible_projects(db=db, user=user, project_ids=project_ids)
    now = int(datetime.now(tz=timezone.utc).timestamp())
    project_id_list = [item.id for item in projects]
    if not project_id_list:
        return OperationsOverviewResponse(
            generated_at=now,
            project_count=0,
            failed_backlog=0,
            dead_letter_backlog=0,
            retry_backlog=0,
            retry_trend=[],
            project_signals=[],
            guardrails=OperationsGuardrailStatus(
                degraded=False,
                degradation_reasons=[],
                project_signal_limit=_MAX_OPERATIONS_PROJECT_SIGNALS,
                project_signal_returned=0,
                alerts=[],
            ),
        )

    queue_items = db.query(RunQueue).filter(RunQueue.project_id.in_(project_id_list)).all()
    events = db.query(IntegrationEvent).filter(IntegrationEvent.project_id.in_(project_id_list)).all()
    deliveries = db.query(NotificationDelivery).filter(NotificationDelivery.project_id.in_(project_id_list)).all()

    failed_by_project: dict[int, int] = {pid: 0 for pid in project_id_list}
    dead_letter_by_project: dict[int, int] = {pid: 0 for pid in project_id_list}
    retry_by_project: dict[int, int] = {pid: 0 for pid in project_id_list}

    for item in queue_items:
        if item.status in {"failed", "error"}:
            failed_by_project[item.project_id] = failed_by_project.get(item.project_id, 0) + 1

    for item in events:
        if item.status in {"failed", "retry_pending"}:
            retry_by_project[item.project_id] = retry_by_project.get(item.project_id, 0) + 1

    for item in deliveries:
        if item.status == "dead_letter":
            dead_letter_by_project[item.project_id] = dead_letter_by_project.get(item.project_id, 0) + 1
        if item.status in {"retry_pending", "dead_letter"}:
            retry_by_project[item.project_id] = retry_by_project.get(item.project_id, 0) + 1

    today_start = _day_bucket_start(now)
    start_day = today_start - (days - 1) * 86400
    trend_map: dict[int, dict[str, int]] = {
        start_day + offset * 86400: {"retry_events": 0, "retry_deliveries": 0}
        for offset in range(days)
    }

    for item in events:
        if item.status not in {"failed", "retry_pending"}:
            continue
        bucket = _day_bucket_start(item.updated_at)
        if bucket < start_day or bucket > today_start:
            continue
        trend_map[bucket]["retry_events"] += 1

    for item in deliveries:
        if item.status not in {"retry_pending", "dead_letter"}:
            continue
        bucket = _day_bucket_start(item.updated_at)
        if bucket < start_day or bucket > today_start:
            continue
        trend_map[bucket]["retry_deliveries"] += 1

    retry_trend = [
        OperationsRetryTrendItem(
            bucket_start=bucket,
            bucket_label=_day_bucket_label(bucket),
            retry_events=payload["retry_events"],
            retry_deliveries=payload["retry_deliveries"],
            total_retries=payload["retry_events"] + payload["retry_deliveries"],
        )
        for bucket, payload in sorted(trend_map.items(), key=lambda pair: pair[0])
    ]

    project_signals = [
        OperationsProjectSignal(
            project_id=item.id,
            project_name=item.name,
            failed_backlog=failed_by_project.get(item.id, 0),
            dead_letter_backlog=dead_letter_by_project.get(item.id, 0),
            retry_backlog=retry_by_project.get(item.id, 0),
        )
        for item in projects
    ]
    project_signals.sort(key=lambda item: (item.retry_backlog, item.failed_backlog, item.dead_letter_backlog), reverse=True)

    failed_backlog = sum(failed_by_project.values())
    dead_letter_backlog = sum(dead_letter_by_project.values())
    retry_backlog = sum(retry_by_project.values())
    alerts = _build_operations_alerts(
        failed_backlog=failed_backlog,
        dead_letter_backlog=dead_letter_backlog,
        retry_backlog=retry_backlog,
    )
    degradation_reasons: list[str] = []
    if len(project_signals) > _MAX_OPERATIONS_PROJECT_SIGNALS:
        degradation_reasons.append("project_signals_truncated")
        project_signals = project_signals[:_MAX_OPERATIONS_PROJECT_SIGNALS]

    create_audit_log(
        db=db,
        request=request,
        action="report.operations.read",
        resource_type="operations_report",
        resource_id="cross_project",
        user_id=user.id,
        details={
            "project_count": len(project_id_list),
            "days": days,
            "failed_backlog": failed_backlog,
            "dead_letter_backlog": dead_letter_backlog,
            "retry_backlog": retry_backlog,
            "degraded": bool(degradation_reasons),
            "degradation_reasons": degradation_reasons,
            "alert_codes": [item.code for item in alerts],
        },
    )

    return OperationsOverviewResponse(
        generated_at=now,
        project_count=len(project_id_list),
        failed_backlog=failed_backlog,
        dead_letter_backlog=dead_letter_backlog,
        retry_backlog=retry_backlog,
        retry_trend=retry_trend,
        project_signals=project_signals,
        guardrails=OperationsGuardrailStatus(
            degraded=bool(degradation_reasons),
            degradation_reasons=degradation_reasons,
            project_signal_limit=_MAX_OPERATIONS_PROJECT_SIGNALS,
            project_signal_returned=len(project_signals),
            alerts=alerts,
        ),
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
