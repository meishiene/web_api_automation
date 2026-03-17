import json
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel


AllowedRunStatus = Literal["running", "success", "failed", "error"]
AllowedRunType = Literal["api", "web"]
FailureCategory = Literal["assertion_failure", "timeout", "network_error", "execution_error", "test_failure"]


class ReportInputRun(BaseModel):
    run_type: AllowedRunType
    run_id: int
    project_id: int
    case_id: int
    case_name: str
    status: AllowedRunStatus
    duration_ms: Optional[int]
    error_message: Optional[str]
    created_at: int
    started_at: Optional[int] = None
    finished_at: Optional[int] = None
    artifact_dir: Optional[str] = None
    artifacts: Optional[list[str]] = None
    detail_api_path: str
    failure_category: Optional[FailureCategory] = None


def _parse_artifacts_json(payload: str | None) -> list[str] | None:
    if not payload:
        return None
    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, list):
        return None
    return [str(item) for item in parsed]


def classify_failure_category(status: str, error_message: str | None) -> FailureCategory | None:
    if status in {"success", "running"}:
        return None
    if status == "error":
        return "execution_error"

    message = (error_message or "").lower()
    if "assert" in message or "expect" in message or "mismatch" in message:
        return "assertion_failure"
    if "timeout" in message or "timed out" in message:
        return "timeout"
    if "connection" in message or "dns" in message or "network" in message:
        return "network_error"
    return "test_failure"


def map_api_row_to_report_input(run: Any, case: Any, project_id: int) -> ReportInputRun:
    return ReportInputRun(
        run_type="api",
        run_id=int(run.id),
        project_id=int(project_id),
        case_id=int(case.id),
        case_name=str(case.name),
        status=run.status,
        duration_ms=run.duration_ms,
        error_message=run.error_message,
        created_at=int(run.created_at),
        started_at=None,
        finished_at=None,
        artifact_dir=None,
        artifacts=None,
        detail_api_path=f"/api/test-runs/{run.id}",
        failure_category=classify_failure_category(run.status, run.error_message),
    )


def map_web_row_to_report_input(run: Any, case: Any, project_id: int) -> ReportInputRun:
    return ReportInputRun(
        run_type="web",
        run_id=int(run.id),
        project_id=int(project_id),
        case_id=int(case.id),
        case_name=str(case.name),
        status=run.status,
        duration_ms=run.duration_ms,
        error_message=run.error_message,
        created_at=int(run.created_at),
        started_at=run.started_at,
        finished_at=run.finished_at,
        artifact_dir=run.artifact_dir,
        artifacts=_parse_artifacts_json(run.artifacts_json),
        detail_api_path=f"/api/web-test-runs/{run.id}",
        failure_category=classify_failure_category(run.status, run.error_message),
    )


def build_report_summary(statuses: list[str]) -> Dict[str, float | int]:
    allowed = {"running", "success", "failed", "error"}
    filtered = [status for status in statuses if status in allowed]

    success_count = sum(1 for status in filtered if status == "success")
    failed_count = sum(1 for status in filtered if status == "failed")
    error_count = sum(1 for status in filtered if status == "error")
    running_count = sum(1 for status in filtered if status == "running")
    completed_count = success_count + failed_count + error_count
    total_count = len(filtered)

    pass_rate = 0 if completed_count == 0 else success_count / completed_count
    fail_rate = 0 if completed_count == 0 else (failed_count + error_count) / completed_count

    return {
        "total_count": total_count,
        "completed_count": completed_count,
        "success_count": success_count,
        "failed_count": failed_count,
        "error_count": error_count,
        "running_count": running_count,
        "pass_rate": pass_rate,
        "fail_rate": fail_rate,
    }
