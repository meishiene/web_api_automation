import json
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.errors import AppException, ErrorCode
from app.models.project import Project
from app.models.user import User
from app.models.web_step import WebStep
from app.models.web_test_case import WebTestCase
from app.schemas.common import BulkDeleteResponse, MessageResponse, TestCaseIdCollectionRequest
from app.schemas.web_test_case import (
    WebTestCaseCopyRequest,
    WebTestCaseCreateRequest,
    WebTestCaseExcelImportRequest,
    WebTestCaseExcelImportResponse,
    WebTestCaseResponse,
    WebTestCaseUpdateRequest,
    parse_params,
)
from app.services.access_control import can_manage_web_test_case, can_view_web_test_case
from app.services.audit_service import create_audit_log
from app.services.web_test_case_excel import (
    ALLOWED_ACTIONS as EXCEL_ALLOWED_ACTIONS,
    WORKBOOK_SHEET_NAME,
    build_rows_from_cases,
    build_template_rows,
    build_workbook,
    load_rows_from_base64,
    normalize_text,
    parse_bool,
    parse_int,
)

router = APIRouter()

_ALLOWED_ACTIONS = EXCEL_ALLOWED_ACTIONS


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


def _load_project_or_404(db: Session, project_id: int) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise AppException(404, ErrorCode.PROJECT_NOT_FOUND, "Project not found")
    return project


def _load_web_test_cases_by_ids(db: Session, project_id: int, case_ids: List[int]) -> List[WebTestCase]:
    records = (
        db.query(WebTestCase)
        .filter(WebTestCase.project_id == project_id, WebTestCase.id.in_(case_ids))
        .all()
    )
    record_map = {item.id: item for item in records}
    missing_ids = [case_id for case_id in case_ids if case_id not in record_map]
    if missing_ids:
        raise AppException(
            404,
            ErrorCode.WEB_TEST_CASE_NOT_FOUND,
            "Web test case not found",
            details={"missing_ids": missing_ids},
        )
    return [record_map[case_id] for case_id in case_ids]


def _ensure_unique_name(db: Session, project_id: int, name: str, exclude_case_id: int | None = None) -> None:
    query = db.query(WebTestCase).filter(WebTestCase.project_id == project_id, WebTestCase.name == name)
    if exclude_case_id is not None:
        query = query.filter(WebTestCase.id != exclude_case_id)
    if query.first():
        raise AppException(400, ErrorCode.WEB_TEST_CASE_ALREADY_EXISTS, "Web test case name already exists")


def _build_unique_name(db: Session, project_id: int, base_name: str) -> str:
    normalized = base_name.strip()
    if not normalized:
        normalized = "copied-web-case"
    candidate = normalized
    suffix = 2
    while db.query(WebTestCase).filter(WebTestCase.project_id == project_id, WebTestCase.name == candidate).first():
        candidate = f"{normalized}-{suffix}"
        suffix += 1
    return candidate


def _replace_case_steps(db: Session, case: WebTestCase, steps: List[Any]) -> None:
    db.query(WebStep).filter(WebStep.web_test_case_id == case.id).delete(synchronize_session=False)
    db.flush()
    for idx, step in enumerate(steps):
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


def _create_case_record(db: Session, payload: WebTestCaseCreateRequest) -> WebTestCase:
    normalized_name = payload.name.strip()
    _ensure_unique_name(db, payload.project_id, normalized_name)
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
    _replace_case_steps(db, case, payload.steps)
    return case


def _update_case_record(db: Session, case: WebTestCase, payload: WebTestCaseUpdateRequest) -> WebTestCase:
    normalized_name = payload.name.strip()
    _ensure_unique_name(db, case.project_id, normalized_name, exclude_case_id=case.id)
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
    _replace_case_steps(db, case, payload.steps)
    return case


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


def _first_non_empty(group_rows: List[Dict[str, Any]], key: str) -> Any:
    for row in group_rows:
        value = row.get(key)
        if normalize_text(value) is not None:
            return value
    return None


def _group_identity(row_payload: Dict[str, Any]) -> str:
    row_number = row_payload["_row_number"]
    case_id = parse_int(row_payload.get("case_id"), "case_id", row_number)
    case_name = normalize_text(row_payload.get("case_name"))
    if case_id is not None:
        return f"id:{case_id}"
    if case_name:
        return f"name:{case_name}"
    raise AppException(400, ErrorCode.VALIDATION_ERROR, f"Missing case identity at row {row_number}")


def _build_import_payload(
    group_rows: List[Dict[str, Any]],
    existing_case: WebTestCase | None,
    project_id: int,
) -> WebTestCaseCreateRequest | WebTestCaseUpdateRequest:
    first_row_number = group_rows[0]["_row_number"]
    case_name = normalize_text(_first_non_empty(group_rows, "case_name")) or (existing_case.name if existing_case else None)
    description = normalize_text(_first_non_empty(group_rows, "description"))
    base_url = normalize_text(_first_non_empty(group_rows, "base_url"))
    browser_name = normalize_text(_first_non_empty(group_rows, "browser_name")) or (existing_case.browser_name if existing_case else "chromium")
    viewport_width = parse_int(_first_non_empty(group_rows, "viewport_width"), "viewport_width", first_row_number) or (existing_case.viewport_width if existing_case else 1920)
    viewport_height = parse_int(_first_non_empty(group_rows, "viewport_height"), "viewport_height", first_row_number) or (existing_case.viewport_height if existing_case else 1080)
    timeout_ms = parse_int(_first_non_empty(group_rows, "timeout_ms"), "timeout_ms", first_row_number) or (existing_case.timeout_ms if existing_case else 30000)
    headless = parse_bool(_first_non_empty(group_rows, "headless"), "headless", first_row_number)
    capture_on_failure = parse_bool(_first_non_empty(group_rows, "capture_on_failure"), "capture_on_failure", first_row_number)
    record_video = parse_bool(_first_non_empty(group_rows, "record_video"), "record_video", first_row_number)

    sorted_rows = sorted(
        group_rows,
        key=lambda item: (
            parse_int(item.get("step_order"), "step_order", item["_row_number"])
            if normalize_text(item.get("step_order"))
            else 10_000 + item["_row_number"],
            item["_row_number"],
        ),
    )

    steps = []
    for row in sorted_rows:
        row_number = row["_row_number"]
        action = normalize_text(row.get("action"))
        if action is None:
            continue
        normalized_action = _normalize_action(action)
        if normalized_action not in _ALLOWED_ACTIONS:
            raise AppException(400, ErrorCode.VALIDATION_ERROR, f"Invalid step action at row {row_number}: {action}")

        params: Dict[str, Any] = {}
        if normalized_action == "open":
            open_url = normalize_text(row.get("open_url"))
            if not open_url:
                raise AppException(400, ErrorCode.VALIDATION_ERROR, f"Missing open_url at row {row_number}")
            params["url"] = open_url
        elif normalized_action == "screenshot":
            filename = normalize_text(row.get("screenshot_filename"))
            if filename:
                params["filename"] = filename
        else:
            locator_strategy = (normalize_text(row.get("locator_strategy")) or "css").lower()
            locator = normalize_text(row.get("locator"))
            if normalized_action != "wait" and not locator:
                raise AppException(400, ErrorCode.VALIDATION_ERROR, f"Missing locator at row {row_number}")
            if locator:
                params["locator_type"] = locator_strategy
                params["locator"] = locator
            if normalized_action == "input":
                params["value"] = normalize_text(row.get("input_value")) or ""
            elif normalized_action == "assert":
                expected_text = normalize_text(row.get("expected_text"))
                if not expected_text:
                    raise AppException(400, ErrorCode.VALIDATION_ERROR, f"Missing expected_text at row {row_number}")
                params["contains"] = expected_text
            elif normalized_action == "wait":
                params["timeout_ms"] = parse_int(row.get("wait_ms"), "wait_ms", row_number) or 500

        steps.append({"action": normalized_action, "params": params})

    payload_data = {
        "name": case_name,
        "description": description if description is not None else (existing_case.description if existing_case else None),
        "base_url": base_url if base_url is not None else (existing_case.base_url if existing_case else None),
        "browser_name": browser_name,
        "viewport_width": viewport_width,
        "viewport_height": viewport_height,
        "timeout_ms": timeout_ms,
        "headless": headless if headless is not None else (bool(existing_case.headless) if existing_case else True),
        "capture_on_failure": capture_on_failure if capture_on_failure is not None else (bool(existing_case.capture_on_failure) if existing_case else True),
        "record_video": record_video if record_video is not None else (bool(existing_case.record_video) if existing_case else False),
        "steps": steps,
    }

    try:
        if existing_case:
            return WebTestCaseUpdateRequest(**payload_data)
        return WebTestCaseCreateRequest(project_id=project_id, **payload_data)
    except ValidationError as exc:
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "Invalid workbook payload", details=exc.errors()) from exc


@router.get("/project/{project_id}/template.xlsx")
def download_web_test_case_template(
    project_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = _load_project_or_404(db, project_id)
    if not can_view_web_test_case(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    stream = build_workbook(build_template_rows())
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="web-test-cases-project-{project_id}-template.xlsx"'},
    )


@router.get("/project/{project_id}/export.xlsx")
def export_web_test_cases(
    project_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = _load_project_or_404(db, project_id)
    if not can_view_web_test_case(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    records = (
        db.query(WebTestCase)
        .filter(WebTestCase.project_id == project_id)
        .order_by(WebTestCase.updated_at.desc(), WebTestCase.id.desc())
        .all()
    )
    stream = build_workbook(build_rows_from_cases(records, parse_params))
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="web-test-cases-project-{project_id}-export.xlsx"'},
    )


@router.post("/project/{project_id}/import/xlsx", response_model=WebTestCaseExcelImportResponse)
def import_web_test_cases_from_excel(
    project_id: int,
    payload: WebTestCaseExcelImportRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WebTestCaseExcelImportResponse:
    project = _load_project_or_404(db, project_id)
    if not can_manage_web_test_case(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    parsed_rows = load_rows_from_base64(payload.file_content_base64)
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for row in parsed_rows:
        groups.setdefault(_group_identity(row), []).append(row)

    imported = 0
    updated = 0
    created_case_ids: List[int] = []
    updated_case_ids: List[int] = []

    for group_key, group_rows in groups.items():
        existing_case = None
        if group_key.startswith("id:"):
            case_id = int(group_key.split(":", 1)[1])
            existing_case = db.query(WebTestCase).filter(WebTestCase.project_id == project_id, WebTestCase.id == case_id).first()
            if not existing_case:
                raise AppException(404, ErrorCode.WEB_TEST_CASE_NOT_FOUND, f"Web test case id {case_id} not found in project")
        else:
            case_name = normalize_text(_first_non_empty(group_rows, "case_name"))
            if case_name:
                existing_case = db.query(WebTestCase).filter(WebTestCase.project_id == project_id, WebTestCase.name == case_name).first()

        import_payload = _build_import_payload(group_rows, existing_case, project_id)
        if existing_case:
            _update_case_record(db, existing_case, import_payload)
            db.flush()
            updated += 1
            updated_case_ids.append(existing_case.id)
        else:
            created_case = _create_case_record(db, import_payload)
            db.flush()
            imported += 1
            created_case_ids.append(created_case.id)

    db.commit()
    create_audit_log(
        db=db,
        request=request,
        action="web_test_case.import_excel",
        resource_type="project",
        resource_id=str(project_id),
        user_id=user.id,
        details={
            "imported": imported,
            "updated": updated,
            "created_case_ids": created_case_ids,
            "updated_case_ids": updated_case_ids,
            "sheet_name": WORKBOOK_SHEET_NAME,
            "file_name": payload.file_name,
        },
    )
    return WebTestCaseExcelImportResponse(
        imported=imported,
        updated=updated,
        created_case_ids=created_case_ids,
        updated_case_ids=updated_case_ids,
    )


@router.post("", response_model=WebTestCaseResponse)
def create_web_test_case(
    payload: WebTestCaseCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WebTestCaseResponse:
    project = _load_project_or_404(db, payload.project_id)
    if not can_manage_web_test_case(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")
    case = _create_case_record(db, payload)
    db.commit()
    db.refresh(case)
    return _to_response(case)


@router.post("/{case_id}/copy", response_model=WebTestCaseResponse)
def copy_web_test_case(
    case_id: int,
    payload: WebTestCaseCopyRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WebTestCaseResponse:
    source = db.query(WebTestCase).join(Project).filter(WebTestCase.id == case_id).first()
    if not source:
        raise AppException(404, ErrorCode.WEB_TEST_CASE_NOT_FOUND, "Web test case not found")
    if not can_manage_web_test_case(db, user, source.project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    target_name = _build_unique_name(db, source.project_id, payload.name or f"{source.name}-copy")
    copied = WebTestCase(
        project_id=source.project_id,
        name=target_name,
        description=source.description,
        base_url=source.base_url,
        browser_name=source.browser_name,
        viewport_width=source.viewport_width,
        viewport_height=source.viewport_height,
        timeout_ms=source.timeout_ms,
        headless=source.headless,
        capture_on_failure=source.capture_on_failure,
        record_video=source.record_video,
    )
    db.add(copied)
    db.flush()
    copied.steps = []
    for step in source.steps:
        copied.steps.append(
            WebStep(
                web_test_case_id=copied.id,
                order_index=step.order_index,
                action=step.action,
                params_json=step.params_json,
            )
        )

    db.commit()
    db.refresh(copied)
    create_audit_log(
        db=db,
        request=request,
        action="web_test_case.copy",
        resource_type="web_test_case",
        resource_id=str(copied.id),
        user_id=user.id,
        details={"source_case_id": source.id, "name": copied.name},
    )
    return _to_response(copied)


@router.post("/project/{project_id}/bulk-delete", response_model=BulkDeleteResponse)
def bulk_delete_web_test_cases(
    project_id: int,
    payload: TestCaseIdCollectionRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BulkDeleteResponse:
    project = _load_project_or_404(db, project_id)
    if not can_manage_web_test_case(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    records = _load_web_test_cases_by_ids(db, project_id, payload.test_case_ids)
    deleted_ids = [item.id for item in records]
    for item in records:
        db.delete(item)
    db.commit()

    create_audit_log(
        db=db,
        request=request,
        action="web_test_case.bulk_delete",
        resource_type="project",
        resource_id=str(project_id),
        user_id=user.id,
        details={"deleted_count": len(deleted_ids), "deleted_ids": deleted_ids},
    )
    return BulkDeleteResponse(
        message="Web test cases deleted",
        deleted_count=len(deleted_ids),
        deleted_ids=deleted_ids,
    )


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

    project = _load_project_or_404(db, case.project_id)
    if not can_manage_web_test_case(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")
    _update_case_record(db, case, payload)
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
