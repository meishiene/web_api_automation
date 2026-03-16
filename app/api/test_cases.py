import json
import time
from typing import List

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.errors import AppException, ErrorCode
from app.models.api_test_case import ApiTestCase
from app.models.project import Project
from app.models.user import User
from app.schemas.api_test_case import (
    TestCaseCopyRequest,
    TestCaseCreateRequest,
    TestCaseExportResponse,
    TestCaseImportRequest,
    TestCaseImportResponse,
    TestCaseResponse,
)
from app.schemas.common import MessageResponse
from app.services.access_control import can_manage_test_case, can_view_test_case
from app.services.audit_service import create_audit_log

router = APIRouter()


def _serialize_tags(raw_tags: str | None) -> List[str]:
    if not raw_tags:
        return []
    try:
        data = json.loads(raw_tags)
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, str)]


def _to_response(test_case: ApiTestCase) -> TestCaseResponse:
    return TestCaseResponse(
        id=test_case.id,
        name=test_case.name,
        project_id=test_case.project_id,
        method=test_case.method,
        url=test_case.url,
        case_group=test_case.case_group,
        tags=_serialize_tags(test_case.tags),
        headers=test_case.headers,
        body=test_case.body,
        expected_status=test_case.expected_status,
        expected_body=test_case.expected_body,
        assertion_rules=test_case.assertion_rules,
        extraction_rules=test_case.extraction_rules,
        created_at=test_case.created_at,
        updated_at=test_case.updated_at,
    )


def _build_unique_name(db: Session, project_id: int, base_name: str) -> str:
    normalized = base_name.strip()
    if not normalized:
        normalized = "copied-case"

    existing = db.query(ApiTestCase).filter(ApiTestCase.project_id == project_id, ApiTestCase.name == normalized).first()
    if not existing:
        return normalized

    suffix = 2
    while True:
        candidate = f"{normalized}-{suffix}"
        exists = (
            db.query(ApiTestCase)
            .filter(ApiTestCase.project_id == project_id, ApiTestCase.name == candidate)
            .first()
        )
        if not exists:
            return candidate
        suffix += 1


@router.get("/project/{project_id}", response_model=List[TestCaseResponse])
def get_test_cases(
    project_id: int,
    keyword: str | None = Query(default=None),
    case_group: str | None = Query(default=None),
    tag: str | None = Query(default=None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[TestCaseResponse]:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise AppException(404, ErrorCode.PROJECT_NOT_FOUND, "Project not found")
    if not can_view_test_case(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    query = db.query(ApiTestCase).filter(ApiTestCase.project_id == project_id)

    if keyword:
        normalized = keyword.strip()
        if normalized:
            pattern = f"%{normalized}%"
            query = query.filter(or_(ApiTestCase.name.ilike(pattern), ApiTestCase.url.ilike(pattern)))

    if case_group:
        normalized_group = case_group.strip()
        if normalized_group:
            query = query.filter(ApiTestCase.case_group == normalized_group)

    if tag:
        normalized_tag = tag.strip()
        if normalized_tag:
            query = query.filter(ApiTestCase.tags.like(f'%"{normalized_tag}"%'))

    records = query.order_by(ApiTestCase.updated_at.desc(), ApiTestCase.id.desc()).all()
    return [_to_response(item) for item in records]


@router.get("/project/{project_id}/export", response_model=TestCaseExportResponse)
def export_test_cases(
    project_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TestCaseExportResponse:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise AppException(404, ErrorCode.PROJECT_NOT_FOUND, "Project not found")
    if not can_view_test_case(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    records = (
        db.query(ApiTestCase)
        .filter(ApiTestCase.project_id == project_id)
        .order_by(ApiTestCase.updated_at.desc(), ApiTestCase.id.desc())
        .all()
    )
    cases = [
        TestCaseCreateRequest(
            name=item.name,
            method=item.method,
            url=item.url,
            case_group=item.case_group,
            tags=_serialize_tags(item.tags),
            headers=item.headers,
            body=item.body,
            expected_status=item.expected_status,
            expected_body=item.expected_body,
            assertion_rules=item.assertion_rules,
            extraction_rules=item.extraction_rules,
        )
        for item in records
    ]
    return TestCaseExportResponse(project_id=project_id, total_cases=len(cases), cases=cases)


@router.post("/project/{project_id}/import", response_model=TestCaseImportResponse)
def import_test_cases(
    project_id: int,
    payload: TestCaseImportRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TestCaseImportResponse:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise AppException(404, ErrorCode.PROJECT_NOT_FOUND, "Project not found")
    if not can_manage_test_case(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    imported = 0
    skipped = 0
    created_case_ids: List[int] = []
    now = int(time.time())

    for item in payload.cases:
        duplicated = (
            db.query(ApiTestCase)
            .filter(ApiTestCase.project_id == project_id, ApiTestCase.name == item.name)
            .first()
        )
        if duplicated:
            if payload.skip_duplicates:
                skipped += 1
                continue
            raise AppException(400, ErrorCode.TEST_CASE_ALREADY_EXISTS, f"Duplicate test case name: {item.name}")

        case = ApiTestCase(
            name=item.name,
            project_id=project_id,
            method=item.method,
            url=item.url,
            case_group=item.case_group,
            tags=(json.dumps(item.tags, ensure_ascii=False) if item.tags else None),
            headers=item.headers,
            body=item.body,
            expected_status=item.expected_status,
            expected_body=item.expected_body,
            assertion_rules=item.assertion_rules,
            extraction_rules=item.extraction_rules,
            created_at=now,
            updated_at=now,
        )
        db.add(case)
        db.flush()

        imported += 1
        created_case_ids.append(case.id)

    db.commit()
    create_audit_log(
        db=db,
        request=request,
        action="test_case.import",
        resource_type="project",
        resource_id=str(project_id),
        user_id=user.id,
        details={"imported": imported, "skipped": skipped},
    )

    return TestCaseImportResponse(imported=imported, skipped=skipped, created_case_ids=created_case_ids)


@router.post("/project/{project_id}", response_model=TestCaseResponse)
def create_test_case(
    project_id: int,
    test_case: TestCaseCreateRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TestCaseResponse:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise AppException(404, ErrorCode.PROJECT_NOT_FOUND, "Project not found")
    if not can_manage_test_case(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    duplicated_name = (
        db.query(ApiTestCase)
        .filter(ApiTestCase.project_id == project_id, ApiTestCase.name == test_case.name)
        .first()
    )
    if duplicated_name:
        raise AppException(400, ErrorCode.TEST_CASE_ALREADY_EXISTS, "Test case name already exists")

    now = int(time.time())
    new_test_case = ApiTestCase(
        name=test_case.name,
        project_id=project_id,
        method=test_case.method.upper(),
        url=test_case.url,
        case_group=test_case.case_group,
        tags=(json.dumps(test_case.tags, ensure_ascii=False) if test_case.tags else None),
        headers=test_case.headers,
        body=test_case.body,
        expected_status=test_case.expected_status,
        expected_body=test_case.expected_body,
        assertion_rules=test_case.assertion_rules,
        extraction_rules=test_case.extraction_rules,
        created_at=now,
        updated_at=now,
    )
    db.add(new_test_case)
    db.commit()
    db.refresh(new_test_case)
    create_audit_log(
        db=db,
        request=request,
        action="test_case.create",
        resource_type="api_test_case",
        resource_id=str(new_test_case.id),
        user_id=user.id,
        details={"name": new_test_case.name, "project_id": project_id},
    )
    return _to_response(new_test_case)


@router.post("/{case_id}/copy", response_model=TestCaseResponse)
def copy_test_case(
    case_id: int,
    payload: TestCaseCopyRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TestCaseResponse:
    source = db.query(ApiTestCase).join(Project).filter(ApiTestCase.id == case_id).first()
    if not source:
        raise AppException(404, ErrorCode.TEST_CASE_NOT_FOUND, "Test case not found")
    if not can_manage_test_case(db, user, source.project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    base_name = payload.name or f"{source.name}-copy"
    target_name = _build_unique_name(db, source.project_id, base_name)
    now = int(time.time())

    copied = ApiTestCase(
        name=target_name,
        project_id=source.project_id,
        method=source.method,
        url=source.url,
        case_group=source.case_group,
        tags=source.tags,
        headers=source.headers,
        body=source.body,
        expected_status=source.expected_status,
        expected_body=source.expected_body,
        assertion_rules=source.assertion_rules,
        extraction_rules=source.extraction_rules,
        created_at=now,
        updated_at=now,
    )
    db.add(copied)
    db.commit()
    db.refresh(copied)

    create_audit_log(
        db=db,
        request=request,
        action="test_case.copy",
        resource_type="api_test_case",
        resource_id=str(copied.id),
        user_id=user.id,
        details={"source_case_id": source.id, "name": copied.name},
    )
    return _to_response(copied)


@router.put("/{case_id}", response_model=TestCaseResponse)
def update_test_case(
    case_id: int,
    test_case: TestCaseCreateRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TestCaseResponse:
    existing_case = db.query(ApiTestCase).join(Project).filter(ApiTestCase.id == case_id).first()
    if not existing_case:
        raise AppException(404, ErrorCode.TEST_CASE_NOT_FOUND, "Test case not found")
    if not can_manage_test_case(db, user, existing_case.project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    duplicated_name = (
        db.query(ApiTestCase)
        .filter(
            ApiTestCase.project_id == existing_case.project_id,
            ApiTestCase.name == test_case.name,
            ApiTestCase.id != case_id,
        )
        .first()
    )
    if duplicated_name:
        raise AppException(400, ErrorCode.TEST_CASE_ALREADY_EXISTS, "Test case name already exists")

    existing_case.name = test_case.name
    existing_case.method = test_case.method.upper()
    existing_case.url = test_case.url
    existing_case.case_group = test_case.case_group
    existing_case.tags = json.dumps(test_case.tags, ensure_ascii=False) if test_case.tags else None
    existing_case.headers = test_case.headers
    existing_case.body = test_case.body
    existing_case.expected_status = test_case.expected_status
    existing_case.expected_body = test_case.expected_body
    existing_case.assertion_rules = test_case.assertion_rules
    existing_case.extraction_rules = test_case.extraction_rules
    existing_case.updated_at = int(time.time())

    db.commit()
    db.refresh(existing_case)
    create_audit_log(
        db=db,
        request=request,
        action="test_case.update",
        resource_type="api_test_case",
        resource_id=str(existing_case.id),
        user_id=user.id,
        details={"name": existing_case.name},
    )
    return _to_response(existing_case)


@router.delete("/{case_id}", response_model=MessageResponse)
def delete_test_case(
    case_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing_case = db.query(ApiTestCase).join(Project).filter(ApiTestCase.id == case_id).first()
    if not existing_case:
        raise AppException(404, ErrorCode.TEST_CASE_NOT_FOUND, "Test case not found")
    if not can_manage_test_case(db, user, existing_case.project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    db.delete(existing_case)
    db.commit()
    create_audit_log(
        db=db,
        request=request,
        action="test_case.delete",
        resource_type="api_test_case",
        resource_id=str(case_id),
        user_id=user.id,
    )
    return {"message": "Test case deleted"}
