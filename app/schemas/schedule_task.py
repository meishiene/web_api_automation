from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class ScheduleTaskBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    cron_expr: str = Field(..., min_length=1, max_length=100)
    timezone: str = Field(default="UTC", min_length=1, max_length=50)
    enabled: bool = True
    target_type: str = Field(..., pattern="^(test_case|test_suite|tag|custom)$")
    target_id: Optional[int] = None
    payload: Dict[str, Any] = Field(default_factory=dict)


class ScheduleTaskCreateRequest(ScheduleTaskBase):
    project_id: int


class ScheduleTaskUpdateRequest(ScheduleTaskBase):
    pass


class ScheduleTaskResponse(ORMModel):
    id: int
    project_id: int
    name: str
    cron_expr: str
    timezone: str
    enabled: bool
    target_type: str
    target_id: Optional[int]
    payload: Dict[str, Any]
    created_by: int
    created_at: int
    updated_at: int


class ScheduleTaskListResponse(BaseModel):
    items: List[ScheduleTaskResponse]
    total: int


class ScheduleTaskTriggerResponse(BaseModel):
    schedule_task_id: int
    queue_item_id: int
    status: str
