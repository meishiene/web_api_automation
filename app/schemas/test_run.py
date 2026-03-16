from typing import Dict, List, Literal, Optional

from pydantic import BaseModel

from app.schemas.common import ORMModel


class TestRunResponse(ORMModel):
    id: int
    test_case_id: int
    status: str
    actual_status: Optional[int]
    actual_body: Optional[str]
    error_message: Optional[str]
    duration_ms: int
    created_at: int


class TestRunDetailResponse(TestRunResponse):
    test_case_name: str
    test_case_method: str
    test_case_url: str
    test_case_expected_status: int
    runtime_variables: Optional[Dict[str, str]] = None
    variable_sources: Optional[Dict[str, str]] = None


class UnifiedRunResponse(ORMModel):
    run_type: Literal["api", "web"]
    run_id: int
    project_id: int
    case_id: int
    case_name: str
    status: str
    duration_ms: Optional[int]
    error_message: Optional[str]
    created_at: int
    started_at: Optional[int] = None
    finished_at: Optional[int] = None
    detail_api_path: str
    artifact_dir: Optional[str] = None
    artifacts: Optional[List[str]] = None


class UnifiedRunListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[UnifiedRunResponse]
