import json
import time
from typing import List

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.errors import AppException, ErrorCode
from app.models.integration_config import IntegrationConfig
from app.models.project import Project
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.integration import (
    IntegrationConfigCreateRequest,
    IntegrationConfigResponse,
    IntegrationConfigUpdateRequest,
    IntegrationCredentialValueResponse,
)
from app.services.access_control import can_manage_test_case, can_view_test_case
from app.services.audit_service import create_audit_log
from app.services.variable_resolver import mask_secret_value

router = APIRouter()


def _serialize_config_json(raw: str | None) -> dict:
    if not raw:
        return {}
    try:
        value = json.loads(raw)
    except (TypeError, ValueError):
        return {}
    return value if isinstance(value, dict) else {}


def _to_response(item: IntegrationConfig) -> IntegrationConfigResponse:
    has_credential_value = bool(item.credential_value)
    return IntegrationConfigResponse(
        id=item.id,
        project_id=item.project_id,
        name=item.name,
        integration_type=item.integration_type,
        provider=item.provider,
        base_url=item.base_url,
        credential_ref=item.credential_ref,
        credential_value=mask_secret_value(item.credential_value or "", has_credential_value) if has_credential_value else None,
        has_credential_value=has_credential_value,
        config_json=_serialize_config_json(item.config_json),
        is_enabled=bool(item.is_enabled),
        created_by=item.created_by,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _ensure_project_and_permission(db: Session, project_id: int, user: User, manage: bool) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise AppException(404, ErrorCode.PROJECT_NOT_FOUND, "Project not found")

    allowed = can_manage_test_case(db, user, project) if manage else can_view_test_case(db, user, project)
    if not allowed:
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")
    return project


def _ensure_integration_and_permission(db: Session, config_id: int, user: User, manage: bool) -> tuple[IntegrationConfig, Project]:
    config = db.query(IntegrationConfig).filter(IntegrationConfig.id == config_id).first()
    if not config:
        raise AppException(404, ErrorCode.INTEGRATION_CONFIG_NOT_FOUND, "Integration config not found")

    project = _ensure_project_and_permission(db, config.project_id, user, manage=manage)
    return config, project


@router.get("/project/{project_id}", response_model=List[IntegrationConfigResponse])
def list_integrations(
    project_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[IntegrationConfigResponse]:
    _ensure_project_and_permission(db, project_id, user, manage=False)
    items = (
        db.query(IntegrationConfig)
        .filter(IntegrationConfig.project_id == project_id)
        .order_by(IntegrationConfig.id.asc())
        .all()
    )

    create_audit_log(
        db=db,
        request=request,
        action="integration_config.list",
        resource_type="integration_config",
        resource_id=str(project_id),
        user_id=user.id,
        details={"project_id": project_id, "count": len(items)},
    )
    return [_to_response(item) for item in items]


@router.get("/{config_id}", response_model=IntegrationConfigResponse)
def get_integration(
    config_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> IntegrationConfigResponse:
    config, _project = _ensure_integration_and_permission(db, config_id, user, manage=False)
    create_audit_log(
        db=db,
        request=request,
        action="integration_config.get",
        resource_type="integration_config",
        resource_id=str(config.id),
        user_id=user.id,
        details={"project_id": config.project_id},
    )
    return _to_response(config)


@router.post("/project/{project_id}", response_model=IntegrationConfigResponse)
def create_integration(
    project_id: int,
    payload: IntegrationConfigCreateRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> IntegrationConfigResponse:
    _ensure_project_and_permission(db, project_id, user, manage=True)

    duplicated = (
        db.query(IntegrationConfig)
        .filter(IntegrationConfig.project_id == project_id, IntegrationConfig.name == payload.name)
        .first()
    )
    if duplicated:
        raise AppException(400, ErrorCode.INTEGRATION_CONFIG_ALREADY_EXISTS, "Integration config name already exists")

    now = int(time.time())
    config = IntegrationConfig(
        project_id=project_id,
        name=payload.name,
        integration_type=payload.integration_type,
        provider=payload.provider,
        base_url=payload.base_url,
        credential_ref=payload.credential_ref,
        credential_value=payload.credential_value,
        config_json=json.dumps(payload.config_json, ensure_ascii=False),
        is_enabled=1 if payload.is_enabled else 0,
        created_by=user.id,
        created_at=now,
        updated_at=now,
    )
    db.add(config)
    db.commit()
    db.refresh(config)

    create_audit_log(
        db=db,
        request=request,
        action="integration_config.create",
        resource_type="integration_config",
        resource_id=str(config.id),
        user_id=user.id,
        details={"project_id": project_id, "integration_type": payload.integration_type, "provider": payload.provider},
    )
    return _to_response(config)


@router.put("/{config_id}", response_model=IntegrationConfigResponse)
def update_integration(
    config_id: int,
    payload: IntegrationConfigUpdateRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> IntegrationConfigResponse:
    config, _project = _ensure_integration_and_permission(db, config_id, user, manage=True)

    duplicated = (
        db.query(IntegrationConfig)
        .filter(
            IntegrationConfig.project_id == config.project_id,
            IntegrationConfig.name == payload.name,
            IntegrationConfig.id != config.id,
        )
        .first()
    )
    if duplicated:
        raise AppException(400, ErrorCode.INTEGRATION_CONFIG_ALREADY_EXISTS, "Integration config name already exists")

    config.name = payload.name
    config.integration_type = payload.integration_type
    config.provider = payload.provider
    config.base_url = payload.base_url
    config.credential_ref = payload.credential_ref
    config.credential_value = payload.credential_value
    config.config_json = json.dumps(payload.config_json, ensure_ascii=False)
    config.is_enabled = 1 if payload.is_enabled else 0
    config.updated_at = int(time.time())
    db.commit()
    db.refresh(config)

    create_audit_log(
        db=db,
        request=request,
        action="integration_config.update",
        resource_type="integration_config",
        resource_id=str(config.id),
        user_id=user.id,
        details={"project_id": config.project_id, "integration_type": payload.integration_type, "provider": payload.provider},
    )
    return _to_response(config)


@router.delete("/{config_id}", response_model=MessageResponse)
def delete_integration(
    config_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    config, _project = _ensure_integration_and_permission(db, config_id, user, manage=True)

    db.delete(config)
    db.commit()

    create_audit_log(
        db=db,
        request=request,
        action="integration_config.delete",
        resource_type="integration_config",
        resource_id=str(config_id),
        user_id=user.id,
        details={"project_id": config.project_id},
    )
    return {"message": "Integration config deleted"}


@router.get("/{config_id}/credential-value", response_model=IntegrationCredentialValueResponse)
def reveal_credential_value(
    config_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> IntegrationCredentialValueResponse:
    config, _project = _ensure_integration_and_permission(db, config_id, user, manage=True)
    if not config.credential_value:
        raise AppException(404, ErrorCode.VARIABLE_NOT_FOUND, "Credential value not found")

    create_audit_log(
        db=db,
        request=request,
        action="integration_config.reveal_credential",
        resource_type="integration_config",
        resource_id=str(config.id),
        user_id=user.id,
        details={"project_id": config.project_id},
    )
    return IntegrationCredentialValueResponse(value=config.credential_value)
