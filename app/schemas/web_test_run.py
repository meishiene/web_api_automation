from typing import Any, Dict, List, Optional

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

