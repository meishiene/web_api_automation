from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class WebTestRunResponse(ORMModel):
    id: int
    project_id: int
    web_test_case_id: int
    status: str
    error_message: Optional[str]
    duration_ms: Optional[int]
    artifact_dir: Optional[str]
    artifacts: List[str]
    created_at: int


class WebTestRunDetailResponse(WebTestRunResponse):
    web_test_case_name: str
    web_test_case_base_url: Optional[str]
    step_logs: List[Dict[str, Any]]


class WebBatchRunResponse(ORMModel):
    id: int
    project_id: int
    triggered_by: Optional[int]
    status: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    error_cases: int
    started_at: Optional[int]
    finished_at: Optional[int]
    created_at: int


class WebBatchRunItemResponse(ORMModel):
    id: int
    batch_run_id: int
    web_test_case_id: int
    web_test_case_name: str
    status: str
    web_test_run_id: Optional[int]
    duration_ms: Optional[int]
    error_message: Optional[str]
    created_at: int
 

class WebBatchRunDetailResponse(WebBatchRunResponse):
    items: List[WebBatchRunItemResponse] = Field(default_factory=list)
