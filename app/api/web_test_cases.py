import json
from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.errors import AppException, ErrorCode
from app.models.project import Project
from app.models.user import User
from app.models.web_step import WebStep
from app.models.web_test_case import WebTestCase
from app.schemas.common import MessageResponse
from app.schemas.web_test_case import (
    WebTestCaseCreateRequest,
    WebTestCaseResponse,
    WebTestCaseUpdateRequest,
    parse_params,
)
from app.services.access_control import can_manage_web_test_case, can_view_web_test_case

router = APIRouter()

_ALLOWED_ACTIONS = {"open", "click", "input", "wait", "assert", "screenshot"}


def _to_response(case: WebTestCase) -> WebTestCaseResponse:
    return WebTestCaseResponse(
        id=case.id,
        project_id=case.project_id,
        name=case.name,
        description=case.description,
        base_url=case.base_url,
        browser_name=case.browser_name,
        viewport_width=case.viewport_width,
        viewport_height=case.viewport_height,
        timeout_ms=case.timeout_ms,
        headless=bool(case.headless),
        capture_on_failure=bool(case.capture_on_failure),
        record_video=bool(case.record_video),
        steps=[
            {
                "id": step.id,
                "order_index": step.order_index,
                "action": step.action,
                "params": parse_params(step.params_json),
            }
            for step in case.steps
        ],
        created_at=case.created_at,
        updated_at=case.updated_at,
    )


def _normalize_action(action: str) -> str:
    return action.strip().lower()


def _serialize_params(params: Dict[str, Any]) -> str:
    # Keep ASCII to avoid db portability surprises; payload is still valid JSON.
    return json.dumps(params, ensure_ascii=True, separators=(",", ":"))


@router.get("/project/{project_id}", response_model=List[WebTestCaseResponse])
def list_web_test_cases(
    project_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[WebTestCaseResponse]:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise AppException(404, ErrorCode.PROJECT_NOT_FOUND, "Project not found")
    if not can_view_web_test_case(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    records = (
        db.query(WebTestCase)
        .filter(WebTestCase.project_id == project_id)
        .order_by(WebTestCase.updated_at.desc(), WebTestCase.id.desc())
        .all()
    )
    return [_to_response(item) for item in records]


@router.post("", response_model=WebTestCaseResponse)
def create_web_test_case(
    payload: WebTestCaseCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WebTestCaseResponse:
    project = db.query(Project).filter(Project.id == payload.project_id).first()
    if not project:
        raise AppException(404, ErrorCode.PROJECT_NOT_FOUND, "Project not found")
    if not can_manage_web_test_case(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    normalized_name = payload.name.strip()
    exists = (
        db.query(WebTestCase)
        .filter(WebTestCase.project_id == payload.project_id, WebTestCase.name == normalized_name)
        .first()
    )
    if exists:
        raise AppException(400, ErrorCode.WEB_TEST_CASE_ALREADY_EXISTS, "Web test case name already exists")

    case = WebTestCase(
        project_id=payload.project_id,
        name=normalized_name,
        description=payload.description,
        base_url=payload.base_url.strip() if payload.base_url else None,
        browser_name=payload.browser_name,
        viewport_width=payload.viewport_width,
        viewport_height=payload.viewport_height,
        timeout_ms=payload.timeout_ms,
        headless=1 if payload.headless else 0,
        capture_on_failure=1 if payload.capture_on_failure else 0,
        record_video=1 if payload.record_video else 0,
    )
    db.add(case)
    db.flush()

    case.steps = []
    for idx, step in enumerate(payload.steps):
        action = _normalize_action(step.action)
        if action not in _ALLOWED_ACTIONS:
            raise AppException(400, ErrorCode.VALIDATION_ERROR, f"Invalid step action: {step.action}")
        case.steps.append(
            WebStep(
                web_test_case_id=case.id,
                order_index=idx,
                action=action,
                params_json=_serialize_params(step.params or {}),
            )
        )

    db.commit()
    db.refresh(case)
    return _to_response(case)


@router.get("/{case_id}", response_model=WebTestCaseResponse)
def get_web_test_case(
    case_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WebTestCaseResponse:
    case = db.query(WebTestCase).filter(WebTestCase.id == case_id).first()
    if not case:
        raise AppException(404, ErrorCode.WEB_TEST_CASE_NOT_FOUND, "Web test case not found")

    project = db.query(Project).filter(Project.id == case.project_id).first()
    if not project:
        raise AppException(404, ErrorCode.PROJECT_NOT_FOUND, "Project not found")
    if not can_view_web_test_case(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    return _to_response(case)


@router.put("/{case_id}", response_model=WebTestCaseResponse)
def update_web_test_case(
    case_id: int,
    payload: WebTestCaseUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WebTestCaseResponse:
    case = db.query(WebTestCase).filter(WebTestCase.id == case_id).first()
    if not case:
        raise AppException(404, ErrorCode.WEB_TEST_CASE_NOT_FOUND, "Web test case not found")

    project = db.query(Project).filter(Project.id == case.project_id).first()
    if not project:
        raise AppException(404, ErrorCode.PROJECT_NOT_FOUND, "Project not found")
    if not can_manage_web_test_case(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    normalized_name = payload.name.strip()
    exists = (
        db.query(WebTestCase)
        .filter(
            WebTestCase.project_id == case.project_id,
            WebTestCase.name == normalized_name,
            WebTestCase.id != case.id,
        )
        .first()
    )
    if exists:
        raise AppException(400, ErrorCode.WEB_TEST_CASE_ALREADY_EXISTS, "Web test case name already exists")

    case.name = normalized_name
    case.description = payload.description
    case.base_url = payload.base_url.strip() if payload.base_url else None
    case.browser_name = payload.browser_name
    case.viewport_width = payload.viewport_width
    case.viewport_height = payload.viewport_height
    case.timeout_ms = payload.timeout_ms
    case.headless = 1 if payload.headless else 0
    case.capture_on_failure = 1 if payload.capture_on_failure else 0
    case.record_video = 1 if payload.record_video else 0

    # Replace steps to keep ordering deterministic.
    db.query(WebStep).filter(WebStep.web_test_case_id == case.id).delete(synchronize_session=False)
    db.flush()
    for idx, step in enumerate(payload.steps):
        action = _normalize_action(step.action)
        if action not in _ALLOWED_ACTIONS:
            raise AppException(400, ErrorCode.VALIDATION_ERROR, f"Invalid step action: {step.action}")
        case.steps.append(
            WebStep(
                web_test_case_id=case.id,
                order_index=idx,
                action=action,
                params_json=_serialize_params(step.params or {}),
            )
        )

    db.commit()
    db.refresh(case)
    return _to_response(case)


@router.delete("/{case_id}", response_model=MessageResponse)
def delete_web_test_case(
    case_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    case = db.query(WebTestCase).filter(WebTestCase.id == case_id).first()
    if not case:
        raise AppException(404, ErrorCode.WEB_TEST_CASE_NOT_FOUND, "Web test case not found")

    project = db.query(Project).filter(Project.id == case.project_id).first()
    if not project:
        raise AppException(404, ErrorCode.PROJECT_NOT_FOUND, "Project not found")
    if not can_manage_web_test_case(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    db.delete(case)
    db.commit()
    return MessageResponse(message="Web test case deleted")
