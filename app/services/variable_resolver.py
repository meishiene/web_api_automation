from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.environment_variable import EnvironmentVariable
from app.models.environment_variable_group_binding import EnvironmentVariableGroupBinding
from app.models.project_environment import ProjectEnvironment
from app.models.project_variable import ProjectVariable


def mask_secret_value(value: str, is_secret: bool) -> str:
    if is_secret:
        return "******"
    return value


def resolve_runtime_variables_with_meta(
    db: Session,
    project_id: int,
    environment_id: int | None = None,
) -> tuple[dict[str, str], dict[str, str], set[str]]:
    values: dict[str, str] = {}
    sources: dict[str, str] = {}
    secret_keys: set[str] = set()

    project_variables = (
        db.query(ProjectVariable)
        .filter(ProjectVariable.project_id == project_id, ProjectVariable.group_name.is_(None))
        .order_by(ProjectVariable.id.asc())
        .all()
    )
    for variable in project_variables:
        values[variable.key] = variable.value
        sources[variable.key] = "project"
        if bool(variable.is_secret):
            secret_keys.add(variable.key)

    if environment_id is None:
        return values, sources, secret_keys

    environment = (
        db.query(ProjectEnvironment)
        .filter(ProjectEnvironment.id == environment_id, ProjectEnvironment.project_id == project_id)
        .first()
    )
    if not environment:
        return values, sources, secret_keys

    group_bindings = (
        db.query(EnvironmentVariableGroupBinding)
        .filter(EnvironmentVariableGroupBinding.environment_id == environment_id)
        .order_by(EnvironmentVariableGroupBinding.id.asc())
        .all()
    )
    bound_group_names = [item.group_name for item in group_bindings]
    if bound_group_names:
        group_variables = (
            db.query(ProjectVariable)
            .filter(ProjectVariable.project_id == project_id, ProjectVariable.group_name.in_(bound_group_names))
            .order_by(ProjectVariable.id.asc())
            .all()
        )
        for variable in group_variables:
            values[variable.key] = variable.value
            sources[variable.key] = f"group:{variable.group_name}"
            if bool(variable.is_secret):
                secret_keys.add(variable.key)
            else:
                secret_keys.discard(variable.key)

    env_variables = (
        db.query(EnvironmentVariable)
        .filter(EnvironmentVariable.environment_id == environment_id)
        .order_by(EnvironmentVariable.id.asc())
        .all()
    )
    for variable in env_variables:
        values[variable.key] = variable.value
        sources[variable.key] = "environment"
        if bool(variable.is_secret):
            secret_keys.add(variable.key)
        else:
            secret_keys.discard(variable.key)

    return values, sources, secret_keys


def resolve_runtime_variables(db: Session, project_id: int, environment_id: int | None = None) -> dict[str, str]:
    values, _sources, _secret_keys = resolve_runtime_variables_with_meta(db, project_id, environment_id)
    return values
