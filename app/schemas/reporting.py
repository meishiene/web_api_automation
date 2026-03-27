from typing import List, Literal, Optional

from pydantic import BaseModel

from app.schemas.common import ORMModel


class TopFailureItem(ORMModel):
    case_id: int
    case_name: str
    run_type: Literal["api", "web"]
    failure_category: Literal["assertion_failure", "timeout", "network_error", "execution_error", "test_failure"]
    count: int
    last_error_message: Optional[str] = None
    last_seen_at: int


class ProjectReportSummaryResponse(BaseModel):
    project_id: int
    total_count: int
    completed_count: int
    success_count: int
    failed_count: int
    error_count: int
    running_count: int
    pass_rate: float
    fail_rate: float
    top_failures: List[TopFailureItem]


class TrendBucketItem(ORMModel):
    bucket_start: int
    bucket_label: str
    total_count: int
    completed_count: int
    success_count: int
    failed_count: int
    error_count: int
    running_count: int
    pass_rate: float
    fail_rate: float


class ProjectReportTrendResponse(BaseModel):
    project_id: int
    granularity: Literal["day", "week"]
    items: List[TrendBucketItem]


class FailureGovernanceItem(ORMModel):
    run_type: Literal["api", "web"]
    run_id: int
    project_id: int
    case_id: int
    case_name: str
    status: Literal["failed", "error"]
    failure_category: Literal["assertion_failure", "timeout", "network_error", "execution_error", "test_failure"]
    error_message: Optional[str] = None
    created_at: int
    detail_api_path: str


class FailureGovernanceListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[FailureGovernanceItem]


class OperationsRetryTrendItem(ORMModel):
    bucket_start: int
    bucket_label: str
    retry_events: int
    retry_deliveries: int
    total_retries: int


class OperationsProjectSignal(ORMModel):
    project_id: int
    project_name: str
    failed_backlog: int
    dead_letter_backlog: int
    retry_backlog: int


class OperationsAlertItem(BaseModel):
    level: Literal["warning", "critical"]
    code: str
    message: str
    metric: str
    threshold: int
    actual: int


class OperationsGuardrailStatus(BaseModel):
    degraded: bool
    degradation_reasons: List[str]
    project_signal_limit: int
    project_signal_returned: int
    alerts: List[OperationsAlertItem]


class OperationsOverviewResponse(BaseModel):
    generated_at: int
    project_count: int
    failed_backlog: int
    dead_letter_backlog: int
    retry_backlog: int
    retry_trend: List[OperationsRetryTrendItem]
    project_signals: List[OperationsProjectSignal]
    guardrails: OperationsGuardrailStatus
