from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_permissions
from app.models.user import User
from app.permissions import Permission, has_permission
from app.errors import AppException, ErrorCode
from app.schemas.audit_log import (
    AuditLogGovernanceRunRequest,
    AuditLogGovernanceRunResponse,
    AuditLogListResponse,
)
from app.services.audit_service import query_audit_logs, run_audit_retention

router = APIRouter()


@router.get("/", response_model=AuditLogListResponse)
def get_audit_logs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    include_archived: bool = Query(default=False),
    action: Optional[str] = Query(default=None),
    result: Optional[str] = Query(default=None),
    request_id: Optional[str] = Query(default=None),
    path_contains: Optional[str] = Query(default=None),
    created_from: Optional[int] = Query(default=None, ge=0),
    created_to: Optional[int] = Query(default=None, ge=0),
    user_id: Optional[int] = Query(default=None, ge=1),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AuditLogListResponse:
    can_view_all = has_permission(user.role, Permission.AUDIT_LOG_VIEW_ALL)
    if user_id is not None and user_id != user.id and not can_view_all:
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    query_user_id = user_id if can_view_all else user.id
    scope_all = can_view_all and user_id is None

    total, items = query_audit_logs(
        db=db,
        user_id=query_user_id,
        page=page,
        page_size=page_size,
        include_archived=include_archived,
        action=action,
        result=result,
        request_id=request_id,
        path_contains=path_contains,
        created_from=created_from,
        created_to=created_to,
        scope_all=scope_all,
    )
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items,
    }


@router.post("/governance/run", response_model=AuditLogGovernanceRunResponse)
def run_audit_log_governance(
    payload: AuditLogGovernanceRunRequest,
    _: User = Depends(require_permissions(Permission.AUDIT_GOVERNANCE_RUN)),
    db: Session = Depends(get_db),
) -> AuditLogGovernanceRunResponse:
    summary = run_audit_retention(
        db=db,
        active_retention_days=payload.active_retention_days,
        archive_retention_days=payload.archive_retention_days,
        batch_size=payload.batch_size,
        dry_run=payload.dry_run,
    )
    return {
        "active_retention_days": payload.active_retention_days,
        "archive_retention_days": payload.archive_retention_days,
        "dry_run": payload.dry_run,
        **summary,
    }
