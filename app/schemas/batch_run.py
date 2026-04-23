from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel, TestCaseIdCollectionRequest


class SuiteRunRequest(BaseModel):
    environment_id: Optional[int] = None
    retry_count: int = Field(default=0, ge=0, le=3)
    retry_on: List[str] = Field(default_factory=lambda: ["error"])
    idempotency_key: Optional[str] = Field(default=None, min_length=1, max_length=64)


class TestCaseBatchRunRequest(TestCaseIdCollectionRequest):
    environment_id: Optional[int] = None
    retry_count: int = Field(default=0, ge=0, le=3)
    retry_on: List[str] = Field(default_factory=lambda: ["error"])


class BatchRunResponse(ORMModel):
    id: int
    project_id: int
    suite_id: Optional[int]
    environment_id: Optional[int]
    triggered_by: Optional[int]
    status: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    error_cases: int
    started_at: Optional[int]
    finished_at: Optional[int]
    created_at: int


class BatchRunItemResponse(ORMModel):
    id: int
    batch_run_id: int
    test_case_id: int
    test_case_name: str
    test_case_method: str
    test_case_url: str
    test_run_id: Optional[int]
    order_index: int
    status: str
    actual_status: Optional[int]
    duration_ms: Optional[int]
    error_message: Optional[str]
    created_at: int


class BatchRunDetailResponse(BatchRunResponse):
    items: List[BatchRunItemResponse]
