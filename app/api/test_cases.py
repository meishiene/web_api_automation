from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.api_test_case import ApiTestCase
from app.models.project import Project
from app.models.user import User
from app.dependencies import get_current_user
from pydantic import BaseModel

router = APIRouter()


class TestCaseCreate(BaseModel):
    name: str
    method: str
    url: str
    headers: Optional[str] = None
    body: Optional[str] = None
    expected_status: int = 200
    expected_body: Optional[str] = None


class TestCaseResponse(BaseModel):
    id: int
    name: str
    project_id: int
    method: str
    url: str
    headers: Optional[str]
    body: Optional[str]
    expected_status: int
    expected_body: Optional[str]
    created_at: int
    updated_at: int


@router.get("/project/{project_id}")
def get_test_cases(
    project_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[TestCaseResponse]:
    # Verify user owns the project
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    test_cases = db.query(ApiTestCase).filter(ApiTestCase.project_id == project_id).all()
    return test_cases


@router.post("/project/{project_id}")
def create_test_case(
    project_id: int,
    test_case: TestCaseCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TestCaseResponse:
    # Verify user owns the project
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    now = int(__import__('time').time())
    new_test_case = ApiTestCase(
        name=test_case.name,
        project_id=project_id,
        method=test_case.method,
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
    return new_test_case


@router.put("/{case_id}")
def update_test_case(
    case_id: int,
    test_case: TestCaseCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TestCaseResponse:
    # Verify user owns the project
    existing_case = db.query(ApiTestCase).join(Project).filter(
        ApiTestCase.id == case_id,
        Project.owner_id == user.id
    ).first()
    if not existing_case:
        raise HTTPException(status_code=404, detail="Test case not found")

    existing_case.name = test_case.name
    existing_case.method = test_case.method
    existing_case.url = test_case.url
    existing_case.headers = test_case.headers
    existing_case.body = test_case.body
    existing_case.expected_status = test_case.expected_status
    existing_case.expected_body = test_case.expected_body
    existing_case.updated_at = int(__import__('time').time())

    db.commit()
    db.refresh(existing_case)
    return existing_case


@router.delete("/{case_id}")
def delete_test_case(
    case_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify user owns the project
    existing_case = db.query(ApiTestCase).join(Project).filter(
        ApiTestCase.id == case_id,
        Project.owner_id == user.id
    ).first()
    if not existing_case:
        raise HTTPException(status_code=404, detail="Test case not found")

    db.delete(existing_case)
    db.commit()
    return {"message": "Test case deleted"}