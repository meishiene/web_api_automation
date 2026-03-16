from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class QueueClaimRequest(BaseModel):
    project_id: int
    worker_id: str = Field(..., min_length=1, max_length=100)
    run_type: Optional[str] = Field(default=None, pattern="^(api|web)$")


class QueueCompleteRequest(BaseModel):
    worker_id: str = Field(..., min_length=1, max_length=100)
    status: str = Field(..., pattern="^(success|failed|error)$")
    result: Dict[str, Any] = Field(default_factory=dict)


class WorkerExecuteOnceRequest(BaseModel):
    project_id: int
    worker_id: str = Field(..., min_length=1, max_length=100)
    run_type: Optional[str] = Field(default=None, pattern="^(api|web)$")


class WorkerHeartbeatRequest(BaseModel):
    project_id: int
    worker_id: str = Field(..., min_length=1, max_length=100)
    run_type: Optional[str] = Field(default=None, pattern="^(api|web)$")
    status: str = Field(default="online", pattern="^(online|busy|offline)$")
    current_queue_item_id: Optional[int] = None


class RunQueueItemResponse(ORMModel):
    id: int
    project_id: int
    run_type: str
    target_type: str
    target_id: int
    status: str
    priority: int
    payload: Optional[str]
    scheduled_by: str
    worker_id: Optional[str]
    started_at: Optional[int]
    finished_at: Optional[int]
    created_at: int


class QueueClaimResponse(BaseModel):
    claimed: bool
    queue_item: Optional[RunQueueItemResponse] = None


class QueueListResponse(BaseModel):
    items: list[RunQueueItemResponse]
    total: int


class QueueCompleteResponse(BaseModel):
    queue_item_id: int
    status: str
    finished_at: int


class WorkerExecuteOnceResponse(BaseModel):
    executed: bool
    queue_item_id: Optional[int] = None
    status: Optional[str] = None


class WorkerHeartbeatResponse(ORMModel):
    id: int
    project_id: int
    worker_id: str
    run_type: Optional[str]
    status: str
    current_queue_item_id: Optional[int]
    last_heartbeat_at: int
    created_at: int
    updated_at: int


class WorkerHeartbeatListResponse(BaseModel):
    items: list[WorkerHeartbeatResponse]
    total: int
