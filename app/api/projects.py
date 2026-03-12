from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.project_member import ProjectMember
from app.models.project import Project
from app.models.user import User
from app.dependencies import get_current_user
from app.errors import AppException, ErrorCode
from app.permissions import Permission, has_permission
from app.schemas.project_member import ProjectMemberCreateRequest, ProjectMemberResponse
from app.services.audit_service import create_audit_log
from app.services.access_control import (
    can_delete_project,
    can_manage_project,
    can_manage_project_members,
    can_view_project,
)
from app.schemas.common import MessageResponse
from app.schemas.project import ProjectCreateRequest, ProjectResponse

router = APIRouter()


@router.get("/", response_model=List[ProjectResponse])
def get_projects(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[ProjectResponse]:
    if has_permission(user.role, Permission.PROJECT_VIEW_ALL):
        return db.query(Project).all()

    owned_projects = db.query(Project).filter(Project.owner_id == user.id).all()
    member_project_ids = [
        row[0]
        for row in (
            db.query(ProjectMember.project_id)
            .filter(ProjectMember.user_id == user.id)
            .all()
        )
    ]
    member_projects = db.query(Project).filter(Project.id.in_(member_project_ids)).all() if member_project_ids else []

    deduped = {project.id: project for project in owned_projects}
    for project in member_projects:
        deduped[project.id] = project
    projects = list(deduped.values())
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
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise AppException(404, ErrorCode.PROJECT_NOT_FOUND, "Project not found")
    if not can_manage_project(db, user, db_project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

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
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise AppException(404, ErrorCode.PROJECT_NOT_FOUND, "Project not found")
    if not can_delete_project(user, db_project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

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


@router.get("/{project_id}/members", response_model=List[ProjectMemberResponse])
def get_project_members(
    project_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[ProjectMemberResponse]:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise AppException(404, ErrorCode.PROJECT_NOT_FOUND, "Project not found")
    if not can_view_project(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    return (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project_id)
        .order_by(ProjectMember.id.asc())
        .all()
    )


@router.post("/{project_id}/members", response_model=ProjectMemberResponse)
def add_project_member(
    project_id: int,
    payload: ProjectMemberCreateRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectMemberResponse:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise AppException(404, ErrorCode.PROJECT_NOT_FOUND, "Project not found")
    if not can_manage_project_members(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")
    if payload.user_id == project.owner_id:
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "Owner is already project manager")

    target_user = db.query(User).filter(User.id == payload.user_id).first()
    if not target_user:
        raise AppException(404, ErrorCode.USER_NOT_FOUND, "User not found")

    existing_member = (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project_id, ProjectMember.user_id == payload.user_id)
        .first()
    )
    if existing_member:
        existing_member.role = payload.role
        db.commit()
        db.refresh(existing_member)
        member = existing_member
    else:
        member = ProjectMember(project_id=project_id, user_id=payload.user_id, role=payload.role)
        db.add(member)
        db.commit()
        db.refresh(member)

    create_audit_log(
        db=db,
        request=request,
        action="project.member.upsert",
        resource_type="project_member",
        resource_id=str(member.id),
        user_id=user.id,
        details={"project_id": project_id, "target_user_id": payload.user_id, "role": payload.role},
    )
    return member


@router.delete("/{project_id}/members/{member_user_id}", response_model=MessageResponse)
def remove_project_member(
    project_id: int,
    member_user_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise AppException(404, ErrorCode.PROJECT_NOT_FOUND, "Project not found")
    if not can_manage_project_members(db, user, project):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")
    if member_user_id == project.owner_id:
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "Project owner cannot be removed")

    member = (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project_id, ProjectMember.user_id == member_user_id)
        .first()
    )
    if not member:
        raise AppException(404, ErrorCode.PROJECT_MEMBER_NOT_FOUND, "Project member not found")

    db.delete(member)
    db.commit()
    create_audit_log(
        db=db,
        request=request,
        action="project.member.remove",
        resource_type="project_member",
        resource_id=str(member.id),
        user_id=user.id,
        details={"project_id": project_id, "target_user_id": member_user_id},
    )
    return {"message": "Project member removed"}
