from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.dependencies import get_current_user
from app.errors import AppException, ErrorCode
from app.models.api_test_case import ApiTestCase
from app.models.api_test_suite import ApiTestSuite
from app.models.api_test_suite_case import ApiTestSuiteCase
from app.models.project import Project
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.test_suite import (
    TestSuiteCaseResponse,
    TestSuiteCaseUpsertRequest,
    TestSuiteCreateRequest,
    TestSuiteResponse,
)
from app.services.access_control import can_manage_test_case, can_view_test_case
from app.services.audit_service import create_audit_log

router = APIRouter()


def _build_suite_response(suite: ApiTestSuite) -> TestSuiteResponse:
    return TestSuiteResponse(
        id=suite.id,
        project_id=suite.project_id,
        name=suite.name,
        description=suite.description,
        created_by=suite.created_by,
        created_at=suite.created_at,
        updated_at=suite.updated_at,
        case_count=len(suite.cases),
    )


@router.get("/project/{project_id}", response_model=List[TestSuiteResponse])
def list_suites(
    project_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[TestSuiteResponse]:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise AppException(404, ErrorCode.PROJECT_NOT_FOUND, "Project not found")
    if not can_view_test_case(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    suites = (
        db.query(ApiTestSuite)
        .filter(ApiTestSuite.project_id == project_id)
        .order_by(ApiTestSuite.id.asc())
        .all()
    )
    return [_build_suite_response(suite) for suite in suites]


@router.post("/project/{project_id}", response_model=TestSuiteResponse)
def create_suite(
    project_id: int,
    payload: TestSuiteCreateRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TestSuiteResponse:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise AppException(404, ErrorCode.PROJECT_NOT_FOUND, "Project not found")
    if not can_manage_test_case(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    duplicated = (
        db.query(ApiTestSuite)
        .filter(ApiTestSuite.project_id == project_id, ApiTestSuite.name == payload.name)
        .first()
    )
    if duplicated:
        raise AppException(400, ErrorCode.TEST_SUITE_ALREADY_EXISTS, "Test suite name already exists")

    now = int(__import__("time").time())
    suite = ApiTestSuite(
        project_id=project_id,
        name=payload.name,
        description=payload.description,
        created_by=user.id,
        created_at=now,
        updated_at=now,
    )
    db.add(suite)
    db.commit()
    db.refresh(suite)

    create_audit_log(
        db=db,
        request=request,
        action="test_suite.create",
        resource_type="api_test_suite",
        resource_id=str(suite.id),
        user_id=user.id,
        details={"project_id": project_id, "name": suite.name},
    )
    return _build_suite_response(suite)


@router.put("/{suite_id}", response_model=TestSuiteResponse)
def update_suite(
    suite_id: int,
    payload: TestSuiteCreateRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TestSuiteResponse:
    suite = db.query(ApiTestSuite).join(Project).filter(ApiTestSuite.id == suite_id).first()
    if not suite:
        raise AppException(404, ErrorCode.TEST_SUITE_NOT_FOUND, "Test suite not found")
    if not can_manage_test_case(db, user, suite.project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    duplicated = (
        db.query(ApiTestSuite)
        .filter(
            ApiTestSuite.project_id == suite.project_id,
            ApiTestSuite.name == payload.name,
            ApiTestSuite.id != suite_id,
        )
        .first()
    )
    if duplicated:
        raise AppException(400, ErrorCode.TEST_SUITE_ALREADY_EXISTS, "Test suite name already exists")

    suite.name = payload.name
    suite.description = payload.description
    suite.updated_at = int(__import__("time").time())
    db.commit()
    db.refresh(suite)

    create_audit_log(
        db=db,
        request=request,
        action="test_suite.update",
        resource_type="api_test_suite",
        resource_id=str(suite.id),
        user_id=user.id,
        details={"name": suite.name},
    )
    return _build_suite_response(suite)


@router.delete("/{suite_id}", response_model=MessageResponse)
def delete_suite(
    suite_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    suite = db.query(ApiTestSuite).join(Project).filter(ApiTestSuite.id == suite_id).first()
    if not suite:
        raise AppException(404, ErrorCode.TEST_SUITE_NOT_FOUND, "Test suite not found")
    if not can_manage_test_case(db, user, suite.project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    db.delete(suite)
    db.commit()

    create_audit_log(
        db=db,
        request=request,
        action="test_suite.delete",
        resource_type="api_test_suite",
        resource_id=str(suite_id),
        user_id=user.id,
    )
    return {"message": "Test suite deleted"}


@router.get("/{suite_id}/cases", response_model=List[TestSuiteCaseResponse])
def list_suite_cases(
    suite_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[TestSuiteCaseResponse]:
    suite = db.query(ApiTestSuite).join(Project).filter(ApiTestSuite.id == suite_id).first()
    if not suite:
        raise AppException(404, ErrorCode.TEST_SUITE_NOT_FOUND, "Test suite not found")
    if not can_view_test_case(db, user, suite.project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    links = (
        db.query(ApiTestSuiteCase)
        .filter(ApiTestSuiteCase.suite_id == suite_id)
        .order_by(ApiTestSuiteCase.order_index.asc(), ApiTestSuiteCase.id.asc())
        .all()
    )

    return [
        TestSuiteCaseResponse(
            id=link.id,
            suite_id=link.suite_id,
            test_case_id=link.test_case_id,
            order_index=link.order_index,
            created_at=link.created_at,
            test_case_name=link.test_case.name if link.test_case else None,
        )
        for link in links
    ]


@router.post("/{suite_id}/cases/{case_id}", response_model=TestSuiteCaseResponse)
def upsert_suite_case(
    suite_id: int,
    case_id: int,
    payload: TestSuiteCaseUpsertRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TestSuiteCaseResponse:
    suite = db.query(ApiTestSuite).join(Project).filter(ApiTestSuite.id == suite_id).first()
    if not suite:
        raise AppException(404, ErrorCode.TEST_SUITE_NOT_FOUND, "Test suite not found")
    if not can_manage_test_case(db, user, suite.project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    test_case = db.query(ApiTestCase).filter(ApiTestCase.id == case_id).first()
    if not test_case or test_case.project_id != suite.project_id:
        raise AppException(404, ErrorCode.TEST_CASE_NOT_FOUND, "Test case not found")

    conflict = (
        db.query(ApiTestSuiteCase)
        .filter(
            ApiTestSuiteCase.suite_id == suite_id,
            ApiTestSuiteCase.order_index == payload.order_index,
            ApiTestSuiteCase.test_case_id != case_id,
        )
        .first()
    )
    if conflict:
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "order_index already exists in suite")

    link = (
        db.query(ApiTestSuiteCase)
        .filter(ApiTestSuiteCase.suite_id == suite_id, ApiTestSuiteCase.test_case_id == case_id)
        .first()
    )
    now = int(__import__("time").time())
    if link:
        link.order_index = payload.order_index
    else:
        link = ApiTestSuiteCase(
            suite_id=suite_id,
            test_case_id=case_id,
            order_index=payload.order_index,
            created_at=now,
        )
        db.add(link)

    suite.updated_at = now
    db.commit()
    db.refresh(link)

    create_audit_log(
        db=db,
        request=request,
        action="test_suite.case.upsert",
        resource_type="api_test_suite_case",
        resource_id=str(link.id),
        user_id=user.id,
        details={"suite_id": suite_id, "test_case_id": case_id, "order_index": link.order_index},
    )

    return TestSuiteCaseResponse(
        id=link.id,
        suite_id=link.suite_id,
        test_case_id=link.test_case_id,
        order_index=link.order_index,
        created_at=link.created_at,
        test_case_name=link.test_case.name if link.test_case else None,
    )


@router.delete("/{suite_id}/cases/{case_id}", response_model=MessageResponse)
def delete_suite_case(
    suite_id: int,
    case_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    suite = db.query(ApiTestSuite).join(Project).filter(ApiTestSuite.id == suite_id).first()
    if not suite:
        raise AppException(404, ErrorCode.TEST_SUITE_NOT_FOUND, "Test suite not found")
    if not can_manage_test_case(db, user, suite.project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    link = (
        db.query(ApiTestSuiteCase)
        .filter(ApiTestSuiteCase.suite_id == suite_id, ApiTestSuiteCase.test_case_id == case_id)
        .first()
    )
    if not link:
        raise AppException(404, ErrorCode.TEST_SUITE_CASE_NOT_FOUND, "Suite case link not found")

    db.delete(link)
    suite.updated_at = int(__import__("time").time())
    db.commit()

    create_audit_log(
        db=db,
        request=request,
        action="test_suite.case.delete",
        resource_type="api_test_suite_case",
        resource_id=str(link.id),
        user_id=user.id,
        details={"suite_id": suite_id, "test_case_id": case_id},
    )
    return {"message": "Test suite case deleted"}
