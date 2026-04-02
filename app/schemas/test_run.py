from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

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


class TestRunExecuteRequest(BaseModel):
    method: Optional[Literal["GET", "POST", "PUT", "PATCH", "DELETE"]] = None
    url: Optional[str] = Field(default=None, max_length=500)
    headers: Optional[str] = None
    body: Optional[str] = None
    expected_status: Optional[int] = Field(default=None, ge=100, lt=600)
    expected_body: Optional[str] = None
    assertion_rules: Optional[str] = None
    extraction_rules: Optional[str] = None

    @field_validator("url", "headers", "body", "expected_body", "assertion_rules", "extraction_rules", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        if not isinstance(value, str):
            return value
        normalized = value.strip()
        return normalized or None

    @field_validator("method", mode="before")
    @classmethod
    def normalize_method(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        return value.upper().strip()


class TestRunDetailResponse(TestRunResponse):
    test_case_name: str
    test_case_method: str
    test_case_url: str
    test_case_expected_status: int
    test_case_expected_body: Optional[str] = None
    test_case_assertion_rules: Optional[str] = None
    test_case_extraction_rules: Optional[str] = None
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
