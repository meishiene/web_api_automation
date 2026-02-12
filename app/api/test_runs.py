from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.test_run import TestRun
from app.models.api_test_case import ApiTestCase
from app.models.project import Project
from app.models.user import User
from app.dependencies import get_current_user
from app.services.test_executor import execute_test
from pydantic import BaseModel
import asyncio

router = APIRouter()


class TestRunResponse(BaseModel):
    id: int
    test_case_id: int
    status: str
    actual_status: int
    actual_body: str
    error_message: str
    duration_ms: int
    created_at: int


@router.post("/test-cases/{case_id}/run")
async def run_test_case(
    case_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TestRunResponse:
    # Verify user owns the test case's project
    test_case = db.query(ApiTestCase).join(Project).filter(
        ApiTestCase.id == case_id,
        Project.owner_id == user.id
    ).first()

    if not test_case:
        raise HTTPException(status_code=404, detail="Test case not found")

    # Execute the test
    result = await execute_test(test_case)

    # Save the result
    now = int(__import__('time').time())
    test_run = TestRun(
        test_case_id=case_id,
        status=result['status'],
        actual_status=result['actual_status'],
        actual_body=result['actual_body'],
        error_message=result['error_message'],
        duration_ms=result['duration_ms'],
        created_at=now
    )

    db.add(test_run)
    db.commit()
    db.refresh(test_run)

    return test_run


@router.get("/project/{project_id}")
def get_test_runs(
    project_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[TestRunResponse]:
    # Verify user owns the project
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    test_runs = db.query(TestRun).join(ApiTestCase).filter(
        ApiTestCase.project_id == project_id
    ).all()

    return test_runs