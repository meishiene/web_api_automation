from typing import List, Optional

from pydantic import BaseModel

from app.schemas.common import ORMModel


class SuiteRunRequest(BaseModel):
    environment_id: Optional[int] = None


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
    test_run_id: Optional[int]
    order_index: int
    status: str
    error_message: Optional[str]
    created_at: int


class BatchRunDetailResponse(BatchRunResponse):
    items: List[BatchRunItemResponse]
