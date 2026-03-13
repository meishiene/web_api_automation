from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.environment_variable import EnvironmentVariable
from app.models.project_environment import ProjectEnvironment
from app.models.project_variable import ProjectVariable


def mask_secret_value(value: str, is_secret: bool) -> str:
    if is_secret:
        return "******"
    return value


def resolve_runtime_variables(db: Session, project_id: int, environment_id: int | None = None) -> dict[str, str]:
    values: dict[str, str] = {}

    project_variables = (
        db.query(ProjectVariable)
        .filter(ProjectVariable.project_id == project_id)
        .order_by(ProjectVariable.id.asc())
        .all()
    )
    for variable in project_variables:
        values[variable.key] = variable.value

    if environment_id is None:
        return values

    environment = (
        db.query(ProjectEnvironment)
        .filter(ProjectEnvironment.id == environment_id, ProjectEnvironment.project_id == project_id)
        .first()
    )
    if not environment:
        return values

    env_variables = (
        db.query(EnvironmentVariable)
        .filter(EnvironmentVariable.environment_id == environment_id)
        .order_by(EnvironmentVariable.id.asc())
        .all()
    )
    for variable in env_variables:
        values[variable.key] = variable.value

    return values
