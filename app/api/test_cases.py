from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.api_test_case import ApiTestCase
from app.models.project import Project
from app.models.user import User
from app.dependencies import get_current_user
from app.errors import AppException, ErrorCode
from app.services.access_control import can_manage_test_case, can_view_test_case
from app.services.audit_service import create_audit_log
from app.schemas.api_test_case import TestCaseCreateRequest, TestCaseResponse
from app.schemas.common import MessageResponse

router = APIRouter()


@router.get("/project/{project_id}", response_model=List[TestCaseResponse])
def get_test_cases(
    project_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[TestCaseResponse]:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise AppException(404, ErrorCode.PROJECT_NOT_FOUND, "Project not found")
    if not can_view_test_case(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    test_cases = db.query(ApiTestCase).filter(ApiTestCase.project_id == project_id).all()
    return test_cases


@router.post("/project/{project_id}", response_model=TestCaseResponse)
def create_test_case(
    project_id: int,
    test_case: TestCaseCreateRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
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

    now = int(__import__('time').time())
    new_test_case = ApiTestCase(
        name=test_case.name,
        project_id=project_id,
        method=test_case.method.upper(),
        url=test_case.url,
        headers=test_case.headers,
        body=test_case.body,
        expected_status=test_case.expected_status,
        expected_body=test_case.expected_body,
        created_at=now,
        updated_at=now
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
    return new_test_case


@router.put("/{case_id}", response_model=TestCaseResponse)
def update_test_case(
    case_id: int,
    test_case: TestCaseCreateRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TestCaseResponse:
    existing_case = db.query(ApiTestCase).join(Project).filter(
        ApiTestCase.id == case_id
    ).first()
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
    existing_case.headers = test_case.headers
    existing_case.body = test_case.body
    existing_case.expected_status = test_case.expected_status
    existing_case.expected_body = test_case.expected_body
    existing_case.updated_at = int(__import__('time').time())

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
    return existing_case


@router.delete("/{case_id}", response_model=MessageResponse)
def delete_test_case(
    case_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing_case = db.query(ApiTestCase).join(Project).filter(
        ApiTestCase.id == case_id
    ).first()
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
