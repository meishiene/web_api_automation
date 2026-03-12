import time
from typing import List

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.errors import AppException, ErrorCode
from app.models.organization import Organization
from app.models.organization_member import OrganizationMember
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user import User
from app.services.access_control import can_manage_organization, can_view_organization
from app.services.audit_service import create_audit_log
from app.schemas.common import MessageResponse
from app.schemas.organization import (
    CrossProjectMemberGovernanceRequest,
    CrossProjectMemberGovernanceResponse,
    OrganizationCreateRequest,
    OrganizationMemberCreateRequest,
    OrganizationMemberResponse,
    OrganizationProjectAttachRequest,
    OrganizationResponse,
)

router = APIRouter()


@router.get("/", response_model=List[OrganizationResponse])
def get_organizations(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[OrganizationResponse]:
    owned = db.query(Organization).filter(Organization.owner_id == user.id).all()
    member_org_ids = [
        row[0]
        for row in (
            db.query(OrganizationMember.organization_id)
            .filter(OrganizationMember.user_id == user.id)
            .all()
        )
    ]
    member_orgs = db.query(Organization).filter(Organization.id.in_(member_org_ids)).all() if member_org_ids else []
    deduped = {item.id: item for item in owned}
    for item in member_orgs:
        deduped[item.id] = item
    return list(deduped.values())


@router.post("/", response_model=OrganizationResponse)
def create_organization(
    payload: OrganizationCreateRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrganizationResponse:
    existing = db.query(Organization).filter(Organization.name == payload.name).first()
    if existing:
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "Organization name already exists")

    now = int(time.time())
    org = Organization(name=payload.name, owner_id=user.id, created_at=now)
    db.add(org)
    db.commit()
    db.refresh(org)
    create_audit_log(
        db=db,
        request=request,
        action="organization.create",
        resource_type="organization",
        resource_id=str(org.id),
        user_id=user.id,
        details={"name": org.name},
    )
    return org


@router.get("/{organization_id}/members", response_model=List[OrganizationMemberResponse])
def get_organization_members(
    organization_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[OrganizationMemberResponse]:
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if not org:
        raise AppException(404, ErrorCode.ORGANIZATION_NOT_FOUND, "Organization not found")
    if not can_view_organization(db, user, org):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")
    return (
        db.query(OrganizationMember)
        .filter(OrganizationMember.organization_id == organization_id)
        .order_by(OrganizationMember.id.asc())
        .all()
    )


@router.post("/{organization_id}/members", response_model=OrganizationMemberResponse)
def upsert_organization_member(
    organization_id: int,
    payload: OrganizationMemberCreateRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrganizationMemberResponse:
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if not org:
        raise AppException(404, ErrorCode.ORGANIZATION_NOT_FOUND, "Organization not found")
    if not can_manage_organization(db, user, org):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")
    if payload.user_id == org.owner_id:
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "Owner is already organization manager")

    target_user = db.query(User).filter(User.id == payload.user_id).first()
    if not target_user:
        raise AppException(404, ErrorCode.USER_NOT_FOUND, "User not found")

    member = (
        db.query(OrganizationMember)
        .filter(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.user_id == payload.user_id,
        )
        .first()
    )
    if member:
        member.role = payload.role
    else:
        member = OrganizationMember(
            organization_id=organization_id,
            user_id=payload.user_id,
            role=payload.role,
            created_at=int(time.time()),
        )
        db.add(member)
    db.commit()
    db.refresh(member)
    create_audit_log(
        db=db,
        request=request,
        action="organization.member.upsert",
        resource_type="organization_member",
        resource_id=str(member.id),
        user_id=user.id,
        details={"organization_id": organization_id, "target_user_id": payload.user_id, "role": payload.role},
    )
    return member


@router.post("/{organization_id}/projects/attach", response_model=MessageResponse)
def attach_project_to_organization(
    organization_id: int,
    payload: OrganizationProjectAttachRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if not org:
        raise AppException(404, ErrorCode.ORGANIZATION_NOT_FOUND, "Organization not found")
    if not can_manage_organization(db, user, org):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    project = db.query(Project).filter(Project.id == payload.project_id).first()
    if not project:
        raise AppException(404, ErrorCode.PROJECT_NOT_FOUND, "Project not found")
    if project.organization_id and project.organization_id != organization_id:
        raise AppException(400, ErrorCode.PROJECT_ORGANIZATION_MISMATCH, "Project already belongs to another organization")
    if user.id != project.owner_id and org.owner_id != project.owner_id:
        member = (
            db.query(OrganizationMember)
            .filter(OrganizationMember.organization_id == organization_id, OrganizationMember.user_id == project.owner_id)
            .first()
        )
        if not member:
            raise AppException(
                400,
                ErrorCode.PROJECT_ORGANIZATION_MISMATCH,
                "Project owner is not in organization",
            )

    project.organization_id = organization_id
    db.commit()
    create_audit_log(
        db=db,
        request=request,
        action="organization.project.attach",
        resource_type="project",
        resource_id=str(project.id),
        user_id=user.id,
        details={"organization_id": organization_id},
    )
    return {"message": "Project attached to organization"}


@router.post("/{organization_id}/members/governance/cross-project", response_model=CrossProjectMemberGovernanceResponse)
def apply_cross_project_member_governance(
    organization_id: int,
    payload: CrossProjectMemberGovernanceRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CrossProjectMemberGovernanceResponse:
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if not org:
        raise AppException(404, ErrorCode.ORGANIZATION_NOT_FOUND, "Organization not found")
    if not can_manage_organization(db, user, org):
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")

    target_user = db.query(User).filter(User.id == payload.user_id).first()
    if not target_user:
        raise AppException(404, ErrorCode.USER_NOT_FOUND, "User not found")

    projects = db.query(Project).filter(Project.organization_id == organization_id).all()
    affected_projects = 0
    for project in projects:
        if payload.user_id == project.owner_id:
            continue
        membership = (
            db.query(ProjectMember)
            .filter(ProjectMember.project_id == project.id, ProjectMember.user_id == payload.user_id)
            .first()
        )
        if membership:
            membership.role = payload.project_role
        else:
            membership = ProjectMember(
                project_id=project.id,
                user_id=payload.user_id,
                role=payload.project_role,
                created_at=int(time.time()),
            )
            db.add(membership)
        affected_projects += 1
    db.commit()
    create_audit_log(
        db=db,
        request=request,
        action="organization.member.cross_project_governance",
        resource_type="organization",
        resource_id=str(organization_id),
        user_id=user.id,
        details={
            "target_user_id": payload.user_id,
            "project_role": payload.project_role,
            "affected_projects": affected_projects,
        },
    )
    return {
        "organization_id": organization_id,
        "user_id": payload.user_id,
        "project_role": payload.project_role,
        "affected_projects": affected_projects,
    }
