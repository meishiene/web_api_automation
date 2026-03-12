from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class AuditLogQueryResponse(ORMModel):
    id: int
    user_id: Optional[int]
    action: str
    resource_type: str
    resource_id: Optional[str]
    result: str
    request_id: Optional[str]
    client_ip: Optional[str]
    method: str
    path: str
    details: Optional[str]
    created_at: int
    archived: bool = False


class AuditLogListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[AuditLogQueryResponse]


class AuditLogGovernanceRunRequest(BaseModel):
    active_retention_days: int = Field(default=30, ge=1, le=3650)
    archive_retention_days: int = Field(default=180, ge=1, le=3650)
    batch_size: int = Field(default=500, ge=1, le=5000)
    dry_run: bool = False


class AuditLogGovernanceRunResponse(BaseModel):
    active_retention_days: int
    archive_retention_days: int
    dry_run: bool
    archived_count: int
    deleted_archive_count: int
    candidate_archive_count: int
    candidate_delete_archive_count: int
