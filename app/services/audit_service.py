import json
import logging
import time
from typing import Any, Dict, Optional

from fastapi import Request
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.audit_log_archive import AuditLogArchive

logger = logging.getLogger("app.audit")


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "-")


def create_audit_log(
    db: Session,
    request: Request,
    action: str,
    resource_type: str,
    resource_id: Optional[str],
    result: str = "success",
    user_id: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None,
) -> None:
    payload = json.dumps(details, ensure_ascii=False) if details is not None else None
    record = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        result=result,
        request_id=_request_id(request),
        client_ip=request.client.host if request.client else None,
        method=request.method,
        path=request.url.path,
        details=payload,
        created_at=int(time.time()),
    )
    db.add(record)
    db.commit()

    logger.info(
        "audit_log_created",
        extra={
            "event": "audit_log",
            "request_id": _request_id(request),
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "result": result,
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host if request.client else None,
        },
    )


def _apply_filters(query, model, user_id: int, action: Optional[str], result: Optional[str], request_id: Optional[str], path_contains: Optional[str], created_from: Optional[int], created_to: Optional[int]):
    query = query.filter(model.user_id == user_id)
    if action:
        query = query.filter(model.action == action)
    if result:
        query = query.filter(model.result == result)
    if request_id:
        query = query.filter(model.request_id == request_id)
    if path_contains:
        query = query.filter(model.path.contains(path_contains))
    if created_from is not None:
        query = query.filter(model.created_at >= created_from)
    if created_to is not None:
        query = query.filter(model.created_at <= created_to)
    return query


def query_audit_logs(
    db: Session,
    user_id: Optional[int],
    page: int,
    page_size: int,
    include_archived: bool = False,
    action: Optional[str] = None,
    result: Optional[str] = None,
    request_id: Optional[str] = None,
    path_contains: Optional[str] = None,
    created_from: Optional[int] = None,
    created_to: Optional[int] = None,
    scope_all: bool = False,
) -> tuple[int, list[dict[str, Any]]]:
    if scope_all:
        base_query = db.query(AuditLog)
        if action:
            base_query = base_query.filter(AuditLog.action == action)
        if result:
            base_query = base_query.filter(AuditLog.result == result)
        if request_id:
            base_query = base_query.filter(AuditLog.request_id == request_id)
        if path_contains:
            base_query = base_query.filter(AuditLog.path.contains(path_contains))
        if created_from is not None:
            base_query = base_query.filter(AuditLog.created_at >= created_from)
        if created_to is not None:
            base_query = base_query.filter(AuditLog.created_at <= created_to)
        if user_id is not None:
            base_query = base_query.filter(AuditLog.user_id == user_id)
    else:
        if user_id is None:
            raise ValueError("user_id is required when scope_all is false")
        base_query = _apply_filters(
            db.query(AuditLog),
            AuditLog,
            user_id=user_id,
            action=action,
            result=result,
            request_id=request_id,
            path_contains=path_contains,
            created_from=created_from,
            created_to=created_to,
        )
    total = base_query.count()
    records = (
        base_query.order_by(AuditLog.created_at.desc(), AuditLog.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = [
        {
            "id": item.id,
            "user_id": item.user_id,
            "action": item.action,
            "resource_type": item.resource_type,
            "resource_id": item.resource_id,
            "result": item.result,
            "request_id": item.request_id,
            "client_ip": item.client_ip,
            "method": item.method,
            "path": item.path,
            "details": item.details,
            "created_at": item.created_at,
            "archived": False,
        }
        for item in records
    ]

    if include_archived and len(items) < page_size:
        if scope_all:
            archived_query = db.query(AuditLogArchive)
            if action:
                archived_query = archived_query.filter(AuditLogArchive.action == action)
            if result:
                archived_query = archived_query.filter(AuditLogArchive.result == result)
            if request_id:
                archived_query = archived_query.filter(AuditLogArchive.request_id == request_id)
            if path_contains:
                archived_query = archived_query.filter(AuditLogArchive.path.contains(path_contains))
            if created_from is not None:
                archived_query = archived_query.filter(AuditLogArchive.created_at >= created_from)
            if created_to is not None:
                archived_query = archived_query.filter(AuditLogArchive.created_at <= created_to)
            if user_id is not None:
                archived_query = archived_query.filter(AuditLogArchive.user_id == user_id)
        else:
            archived_query = _apply_filters(
                db.query(AuditLogArchive),
                AuditLogArchive,
                user_id=user_id,
                action=action,
                result=result,
                request_id=request_id,
                path_contains=path_contains,
                created_from=created_from,
                created_to=created_to,
            )
        total += archived_query.count()
        archived_items = (
            archived_query.order_by(AuditLogArchive.created_at.desc(), AuditLogArchive.id.desc())
            .limit(page_size - len(items))
            .all()
        )
        items.extend(
            [
                {
                    "id": item.id,
                    "user_id": item.user_id,
                    "action": item.action,
                    "resource_type": item.resource_type,
                    "resource_id": item.resource_id,
                    "result": item.result,
                    "request_id": item.request_id,
                    "client_ip": item.client_ip,
                    "method": item.method,
                    "path": item.path,
                    "details": item.details,
                    "created_at": item.created_at,
                    "archived": True,
                }
                for item in archived_items
            ]
        )

    return total, items


def run_audit_retention(
    db: Session,
    active_retention_days: int,
    archive_retention_days: int,
    batch_size: int = 500,
    dry_run: bool = False,
) -> Dict[str, int]:
    now = int(time.time())
    archive_before = now - active_retention_days * 24 * 3600
    delete_archive_before = now - archive_retention_days * 24 * 3600

    candidate_archive_count = db.query(func.count(AuditLog.id)).filter(AuditLog.created_at < archive_before).scalar() or 0
    candidate_delete_archive_count = db.query(func.count(AuditLogArchive.id)).filter(AuditLogArchive.created_at < delete_archive_before).scalar() or 0

    archived_count = 0
    deleted_archive_count = 0

    if not dry_run:
        while True:
            rows = (
                db.query(AuditLog)
                .filter(AuditLog.created_at < archive_before)
                .order_by(AuditLog.id.asc())
                .limit(batch_size)
                .all()
            )
            if not rows:
                break

            for row in rows:
                archived = AuditLogArchive(
                    original_id=row.id,
                    user_id=row.user_id,
                    action=row.action,
                    resource_type=row.resource_type,
                    resource_id=row.resource_id,
                    result=row.result,
                    request_id=row.request_id,
                    client_ip=row.client_ip,
                    method=row.method,
                    path=row.path,
                    details=row.details,
                    created_at=row.created_at,
                    archived_at=now,
                )
                db.add(archived)
                db.delete(row)
                archived_count += 1
            db.commit()

        while True:
            archive_rows = (
                db.query(AuditLogArchive)
                .filter(AuditLogArchive.created_at < delete_archive_before)
                .order_by(AuditLogArchive.id.asc())
                .limit(batch_size)
                .all()
            )
            if not archive_rows:
                break
            for row in archive_rows:
                db.delete(row)
                deleted_archive_count += 1
            db.commit()

    return {
        "archived_count": archived_count,
        "deleted_archive_count": deleted_archive_count,
        "candidate_archive_count": int(candidate_archive_count),
        "candidate_delete_archive_count": int(candidate_delete_archive_count),
    }
