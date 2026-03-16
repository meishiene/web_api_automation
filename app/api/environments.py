import time
from typing import List

from fastapi import APIRouter, Depends, Request
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.errors import AppException, ErrorCode
from app.models.environment_variable import EnvironmentVariable
from app.models.environment_variable_group_binding import EnvironmentVariableGroupBinding
from app.models.project import Project
from app.models.project_environment import ProjectEnvironment
from app.models.project_variable import ProjectVariable
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.environment import (
    EnvironmentCreateRequest,
    EnvironmentResponse,
    EnvironmentVariableGroupResponse,
    SecretValueResponse,
    VariableGroupBindRequest,
    VariableGroupSummaryResponse,
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


def _ensure_environment_and_permission(db: Session, environment_id: int, user: User, manage: bool) -> ProjectEnvironment:
    environment = db.query(ProjectEnvironment).join(Project).filter(ProjectEnvironment.id == environment_id).first()
    if not environment:
        raise AppException(404, ErrorCode.ENVIRONMENT_NOT_FOUND, "Environment not found")

    allowed = can_manage_test_case(db, user, environment.project) if manage else can_view_test_case(db, user, environment.project)
    if not allowed:
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")
    return environment


def _to_variable_response(variable: ProjectVariable | EnvironmentVariable) -> VariableResponse:
    return VariableResponse(
        id=variable.id,
        key=variable.key,
        value=mask_secret_value(variable.value, bool(variable.is_secret)),
        is_secret=bool(variable.is_secret),
        group_name=getattr(variable, "group_name", None),
        created_at=variable.created_at,
        updated_at=variable.updated_at,
    )


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

    now = int(time.time())
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
    environment = _ensure_environment_and_permission(db, environment_id, user, manage=True)

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
    environment.updated_at = int(time.time())
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
    _ensure_environment_and_permission(db, environment_id, user, manage=True)

    db.query(ProjectEnvironment).filter(ProjectEnvironment.id == environment_id).delete()
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
    return [_to_variable_response(v) for v in variables]


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
    now = int(time.time())
    if variable:
        variable.value = payload.value
        variable.group_name = payload.group_name
        variable.is_secret = 1 if payload.is_secret else 0
        variable.updated_at = now
    else:
        variable = ProjectVariable(
            project_id=project_id,
            key=payload.key,
            group_name=payload.group_name,
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
        details={
            "project_id": project_id,
            "key": payload.key,
            "group_name": payload.group_name,
            "is_secret": payload.is_secret,
        },
    )
    return _to_variable_response(variable)


@router.get("/project/{project_id}/variable-groups", response_model=List[VariableGroupSummaryResponse])
def list_project_variable_groups(
    project_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[VariableGroupSummaryResponse]:
    _ensure_project_and_permission(db, project_id, user, manage=False)

    rows = (
        db.query(
            ProjectVariable.group_name.label("group_name"),
            func.count(ProjectVariable.id).label("variable_count"),
            func.sum(ProjectVariable.is_secret).label("secret_count"),
        )
        .filter(ProjectVariable.project_id == project_id, ProjectVariable.group_name.is_not(None))
        .group_by(ProjectVariable.group_name)
        .order_by(ProjectVariable.group_name.asc())
        .all()
    )
    return [
        VariableGroupSummaryResponse(
            group_name=row.group_name,
            variable_count=int(row.variable_count or 0),
            secret_count=int(row.secret_count or 0),
        )
        for row in rows
    ]


@router.get("/{environment_id}/variables", response_model=List[VariableResponse])
def list_environment_variables(
    environment_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[VariableResponse]:
    _ensure_environment_and_permission(db, environment_id, user, manage=False)
    variables = (
        db.query(EnvironmentVariable)
        .filter(EnvironmentVariable.environment_id == environment_id)
        .order_by(EnvironmentVariable.id.asc())
        .all()
    )
    return [_to_variable_response(v) for v in variables]


@router.post("/{environment_id}/variables", response_model=VariableResponse)
def upsert_environment_variable(
    environment_id: int,
    payload: VariableUpsertRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> VariableResponse:
    _ensure_environment_and_permission(db, environment_id, user, manage=True)

    variable = (
        db.query(EnvironmentVariable)
        .filter(EnvironmentVariable.environment_id == environment_id, EnvironmentVariable.key == payload.key)
        .first()
    )
    now = int(time.time())
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
    return _to_variable_response(variable)


@router.get("/{environment_id}/variable-groups", response_model=List[EnvironmentVariableGroupResponse])
def list_environment_variable_groups(
    environment_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[EnvironmentVariableGroupResponse]:
    _ensure_environment_and_permission(db, environment_id, user, manage=False)
    return (
        db.query(EnvironmentVariableGroupBinding)
        .filter(EnvironmentVariableGroupBinding.environment_id == environment_id)
        .order_by(EnvironmentVariableGroupBinding.id.asc())
        .all()
    )


@router.post("/{environment_id}/variable-groups/bind", response_model=EnvironmentVariableGroupResponse)
def bind_environment_variable_group(
    environment_id: int,
    payload: VariableGroupBindRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> EnvironmentVariableGroupResponse:
    environment = _ensure_environment_and_permission(db, environment_id, user, manage=True)

    group_exists = (
        db.query(ProjectVariable.id)
        .filter(ProjectVariable.project_id == environment.project_id, ProjectVariable.group_name == payload.group_name)
        .first()
    )
    if not group_exists:
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "Variable group not found in project")

    binding = (
        db.query(EnvironmentVariableGroupBinding)
        .filter(
            EnvironmentVariableGroupBinding.environment_id == environment_id,
            EnvironmentVariableGroupBinding.group_name == payload.group_name,
        )
        .first()
    )
    now = int(time.time())
    if not binding:
        binding = EnvironmentVariableGroupBinding(
            environment_id=environment_id,
            group_name=payload.group_name,
            created_at=now,
            updated_at=now,
        )
        db.add(binding)
        db.commit()
        db.refresh(binding)

    create_audit_log(
        db=db,
        request=request,
        action="environment.variable_group.bind",
        resource_type="environment_variable_group_binding",
        resource_id=str(binding.id),
        user_id=user.id,
        details={"environment_id": environment_id, "group_name": payload.group_name},
    )
    return binding


@router.delete("/{environment_id}/variable-groups/bind/{group_name}", response_model=MessageResponse)
def unbind_environment_variable_group(
    environment_id: int,
    group_name: str,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    normalized_group_name = group_name.strip()
    if not normalized_group_name:
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "Group name must not be empty")

    _ensure_environment_and_permission(db, environment_id, user, manage=True)

    binding = (
        db.query(EnvironmentVariableGroupBinding)
        .filter(
            EnvironmentVariableGroupBinding.environment_id == environment_id,
            EnvironmentVariableGroupBinding.group_name == normalized_group_name,
        )
        .first()
    )
    if not binding:
        raise AppException(404, ErrorCode.VARIABLE_NOT_FOUND, "Variable group binding not found")

    db.delete(binding)
    db.commit()
    create_audit_log(
        db=db,
        request=request,
        action="environment.variable_group.unbind",
        resource_type="environment_variable_group_binding",
        resource_id=str(binding.id),
        user_id=user.id,
        details={"environment_id": environment_id, "group_name": normalized_group_name},
    )
    return {"message": "Variable group unbound"}


@router.get("/project/{project_id}/variables/{key}/secret-value", response_model=SecretValueResponse)
def reveal_project_variable_secret(
    project_id: int,
    key: str,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SecretValueResponse:
    _ensure_project_and_permission(db, project_id, user, manage=True)
    variable = (
        db.query(ProjectVariable)
        .filter(ProjectVariable.project_id == project_id, ProjectVariable.key == key)
        .first()
    )
    if not variable:
        raise AppException(404, ErrorCode.VARIABLE_NOT_FOUND, "Variable not found")
    if not bool(variable.is_secret):
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "Variable is not a secret")

    create_audit_log(
        db=db,
        request=request,
        action="project.variable.reveal_secret",
        resource_type="project_variable",
        resource_id=str(variable.id),
        user_id=user.id,
        details={"project_id": project_id, "key": key},
    )
    return SecretValueResponse(key=variable.key, value=variable.value, scope="project")


@router.get("/{environment_id}/variables/{key}/secret-value", response_model=SecretValueResponse)
def reveal_environment_variable_secret(
    environment_id: int,
    key: str,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SecretValueResponse:
    _ensure_environment_and_permission(db, environment_id, user, manage=True)
    variable = (
        db.query(EnvironmentVariable)
        .filter(EnvironmentVariable.environment_id == environment_id, EnvironmentVariable.key == key)
        .first()
    )
    if not variable:
        raise AppException(404, ErrorCode.VARIABLE_NOT_FOUND, "Variable not found")
    if not bool(variable.is_secret):
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "Variable is not a secret")

    create_audit_log(
        db=db,
        request=request,
        action="environment.variable.reveal_secret",
        resource_type="environment_variable",
        resource_id=str(variable.id),
        user_id=user.id,
        details={"environment_id": environment_id, "key": key},
    )
    return SecretValueResponse(key=variable.key, value=variable.value, scope="environment")
