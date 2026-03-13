from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.dependencies import get_current_user
from app.errors import AppException, ErrorCode
from app.models.environment_variable import EnvironmentVariable
from app.models.project import Project
from app.models.project_environment import ProjectEnvironment
from app.models.project_variable import ProjectVariable
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.environment import (
    EnvironmentCreateRequest,
    EnvironmentResponse,
    VariableResponse,
    VariableUpsertRequest,
)
from app.services.access_control import can_manage_test_case, can_view_test_case
from app.services.audit_service import create_audit_log
from app.services.variable_resolver import mask_secret_value

router = APIRouter()


def _ensure_project_and_permission(db: Session, project_id: int, user: User, manage: bool) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise AppException(404, ErrorCode.PROJECT_NOT_FOUND, "Project not found")

    allowed = can_manage_test_case(db, user, project) if manage else can_view_test_case(db, user, project)
    if not allowed:
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")
    return project


@router.get("/project/{project_id}", response_model=List[EnvironmentResponse])
def list_project_environments(
    project_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[EnvironmentResponse]:
    _ensure_project_and_permission(db, project_id, user, manage=False)
    return (
        db.query(ProjectEnvironment)
        .filter(ProjectEnvironment.project_id == project_id)
        .order_by(ProjectEnvironment.id.asc())
        .all()
    )


@router.post("/project/{project_id}", response_model=EnvironmentResponse)
def create_project_environment(
    project_id: int,
    payload: EnvironmentCreateRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> EnvironmentResponse:
    _ensure_project_and_permission(db, project_id, user, manage=True)

    duplicated = (
        db.query(ProjectEnvironment)
        .filter(ProjectEnvironment.project_id == project_id, ProjectEnvironment.name == payload.name)
        .first()
    )
    if duplicated:
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "Environment name already exists")

    now = int(__import__("time").time())
    environment = ProjectEnvironment(
        project_id=project_id,
        name=payload.name,
        description=payload.description,
        created_by=user.id,
        created_at=now,
        updated_at=now,
    )
    db.add(environment)
    db.commit()
    db.refresh(environment)

    create_audit_log(
        db=db,
        request=request,
        action="environment.create",
        resource_type="project_environment",
        resource_id=str(environment.id),
        user_id=user.id,
        details={"project_id": project_id, "name": payload.name},
    )
    return environment


@router.put("/{environment_id}", response_model=EnvironmentResponse)
def update_project_environment(
    environment_id: int,
    payload: EnvironmentCreateRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> EnvironmentResponse:
    environment = db.query(ProjectEnvironment).join(Project).filter(ProjectEnvironment.id == environment_id).first()
    if not environment:
        raise AppException(404, ErrorCode.ENVIRONMENT_NOT_FOUND, "Environment not found")
    if not can_manage_test_case(db, user, environment.project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    duplicated = (
        db.query(ProjectEnvironment)
        .filter(
            ProjectEnvironment.project_id == environment.project_id,
            ProjectEnvironment.name == payload.name,
            ProjectEnvironment.id != environment.id,
        )
        .first()
    )
    if duplicated:
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "Environment name already exists")

    environment.name = payload.name
    environment.description = payload.description
    environment.updated_at = int(__import__("time").time())
    db.commit()
    db.refresh(environment)

    create_audit_log(
        db=db,
        request=request,
        action="environment.update",
        resource_type="project_environment",
        resource_id=str(environment.id),
        user_id=user.id,
        details={"name": payload.name},
    )
    return environment


@router.delete("/{environment_id}", response_model=MessageResponse)
def delete_project_environment(
    environment_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    environment = db.query(ProjectEnvironment).join(Project).filter(ProjectEnvironment.id == environment_id).first()
    if not environment:
        raise AppException(404, ErrorCode.ENVIRONMENT_NOT_FOUND, "Environment not found")
    if not can_manage_test_case(db, user, environment.project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    db.delete(environment)
    db.commit()
    create_audit_log(
        db=db,
        request=request,
        action="environment.delete",
        resource_type="project_environment",
        resource_id=str(environment_id),
        user_id=user.id,
    )
    return {"message": "Environment deleted"}


@router.get("/project/{project_id}/variables", response_model=List[VariableResponse])
def list_project_variables(
    project_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[VariableResponse]:
    _ensure_project_and_permission(db, project_id, user, manage=False)

    variables = (
        db.query(ProjectVariable)
        .filter(ProjectVariable.project_id == project_id)
        .order_by(ProjectVariable.id.asc())
        .all()
    )
    return [
        VariableResponse(
            id=v.id,
            key=v.key,
            value=mask_secret_value(v.value, bool(v.is_secret)),
            is_secret=bool(v.is_secret),
            created_at=v.created_at,
            updated_at=v.updated_at,
        )
        for v in variables
    ]


@router.post("/project/{project_id}/variables", response_model=VariableResponse)
def upsert_project_variable(
    project_id: int,
    payload: VariableUpsertRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> VariableResponse:
    _ensure_project_and_permission(db, project_id, user, manage=True)

    variable = (
        db.query(ProjectVariable)
        .filter(ProjectVariable.project_id == project_id, ProjectVariable.key == payload.key)
        .first()
    )
    now = int(__import__("time").time())
    if variable:
        variable.value = payload.value
        variable.is_secret = 1 if payload.is_secret else 0
        variable.updated_at = now
    else:
        variable = ProjectVariable(
            project_id=project_id,
            key=payload.key,
            value=payload.value,
            is_secret=1 if payload.is_secret else 0,
            created_at=now,
            updated_at=now,
        )
        db.add(variable)

    db.commit()
    db.refresh(variable)

    create_audit_log(
        db=db,
        request=request,
        action="project.variable.upsert",
        resource_type="project_variable",
        resource_id=str(variable.id),
        user_id=user.id,
        details={"project_id": project_id, "key": payload.key, "is_secret": payload.is_secret},
    )

    return VariableResponse(
        id=variable.id,
        key=variable.key,
        value=mask_secret_value(variable.value, bool(variable.is_secret)),
        is_secret=bool(variable.is_secret),
        created_at=variable.created_at,
        updated_at=variable.updated_at,
    )


@router.get("/{environment_id}/variables", response_model=List[VariableResponse])
def list_environment_variables(
    environment_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[VariableResponse]:
    environment = db.query(ProjectEnvironment).join(Project).filter(ProjectEnvironment.id == environment_id).first()
    if not environment:
        raise AppException(404, ErrorCode.ENVIRONMENT_NOT_FOUND, "Environment not found")
    if not can_view_test_case(db, user, environment.project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    variables = (
        db.query(EnvironmentVariable)
        .filter(EnvironmentVariable.environment_id == environment_id)
        .order_by(EnvironmentVariable.id.asc())
        .all()
    )
    return [
        VariableResponse(
            id=v.id,
            key=v.key,
            value=mask_secret_value(v.value, bool(v.is_secret)),
            is_secret=bool(v.is_secret),
            created_at=v.created_at,
            updated_at=v.updated_at,
        )
        for v in variables
    ]


@router.post("/{environment_id}/variables", response_model=VariableResponse)
def upsert_environment_variable(
    environment_id: int,
    payload: VariableUpsertRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> VariableResponse:
    environment = db.query(ProjectEnvironment).join(Project).filter(ProjectEnvironment.id == environment_id).first()
    if not environment:
        raise AppException(404, ErrorCode.ENVIRONMENT_NOT_FOUND, "Environment not found")
    if not can_manage_test_case(db, user, environment.project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    variable = (
        db.query(EnvironmentVariable)
        .filter(EnvironmentVariable.environment_id == environment_id, EnvironmentVariable.key == payload.key)
        .first()
    )
    now = int(__import__("time").time())
    if variable:
        variable.value = payload.value
        variable.is_secret = 1 if payload.is_secret else 0
        variable.updated_at = now
    else:
        variable = EnvironmentVariable(
            environment_id=environment_id,
            key=payload.key,
            value=payload.value,
            is_secret=1 if payload.is_secret else 0,
            created_at=now,
            updated_at=now,
        )
        db.add(variable)

    db.commit()
    db.refresh(variable)

    create_audit_log(
        db=db,
        request=request,
        action="environment.variable.upsert",
        resource_type="environment_variable",
        resource_id=str(variable.id),
        user_id=user.id,
        details={"environment_id": environment_id, "key": payload.key, "is_secret": payload.is_secret},
    )

    return VariableResponse(
        id=variable.id,
        key=variable.key,
        value=mask_secret_value(variable.value, bool(variable.is_secret)),
        is_secret=bool(variable.is_secret),
        created_at=variable.created_at,
        updated_at=variable.updated_at,
    )
