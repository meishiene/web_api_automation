from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.project import Project
from app.models.user import User
from app.dependencies import get_current_user
from app.errors import AppException, ErrorCode
from app.services.audit_service import create_audit_log
from app.schemas.common import MessageResponse
from app.schemas.project import ProjectCreateRequest, ProjectResponse

router = APIRouter()


@router.get("/", response_model=List[ProjectResponse])
def get_projects(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[ProjectResponse]:
    projects = db.query(Project).filter(Project.owner_id == user.id).all()
    return projects


@router.post("/", response_model=ProjectResponse)
def create_project(
    project: ProjectCreateRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ProjectResponse:
    existing_project = (
        db.query(Project)
        .filter(Project.owner_id == user.id, Project.name == project.name)
        .first()
    )
    if existing_project:
        raise AppException(400, ErrorCode.PROJECT_ALREADY_EXISTS, "Project name already exists")

    new_project = Project(
        name=project.name,
        description=project.description,
        owner_id=user.id,
        created_at=int(__import__('time').time())
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    create_audit_log(
        db=db,
        request=request,
        action="project.create",
        resource_type="project",
        resource_id=str(new_project.id),
        user_id=user.id,
        details={"name": new_project.name},
    )
    return new_project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project: ProjectCreateRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ProjectResponse:
    db_project = db.query(Project).filter(Project.id == project_id, Project.owner_id == user.id).first()
    if not db_project:
        raise AppException(404, ErrorCode.PROJECT_NOT_FOUND, "Project not found")

    duplicated_name = (
        db.query(Project)
        .filter(
            Project.owner_id == user.id,
            Project.name == project.name,
            Project.id != project_id,
        )
        .first()
    )
    if duplicated_name:
        raise AppException(400, ErrorCode.PROJECT_ALREADY_EXISTS, "Project name already exists")

    db_project.name = project.name
    db_project.description = project.description
    db.commit()
    db.refresh(db_project)
    create_audit_log(
        db=db,
        request=request,
        action="project.update",
        resource_type="project",
        resource_id=str(db_project.id),
        user_id=user.id,
        details={"name": db_project.name},
    )
    return db_project


@router.delete("/{project_id}", response_model=MessageResponse)
def delete_project(
    project_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_project = db.query(Project).filter(Project.id == project_id, Project.owner_id == user.id).first()
    if not db_project:
        raise AppException(404, ErrorCode.PROJECT_NOT_FOUND, "Project not found")

    db.delete(db_project)
    db.commit()
    create_audit_log(
        db=db,
        request=request,
        action="project.delete",
        resource_type="project",
        resource_id=str(project_id),
        user_id=user.id,
    )
    return {"message": "Project deleted"}
