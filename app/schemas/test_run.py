from typing import Dict, Optional

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
