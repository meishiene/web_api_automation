from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.organization import Organization
from app.models.organization_member import OrganizationMember
from app.models.user import User
from app.permissions import Permission, has_permission
from sqlalchemy.orm import Session


def get_project_member_role(db: Session, project_id: int, user_id: int) -> str | None:
    membership = (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id)
        .first()
    )
    return membership.role if membership else None


def get_organization_member_role(db: Session, organization_id: int, user_id: int) -> str | None:
    membership = (
        db.query(OrganizationMember)
        .filter(OrganizationMember.organization_id == organization_id, OrganizationMember.user_id == user_id)
        .first()
    )
    return membership.role if membership else None


def can_view_organization(db: Session, user: User, organization: Organization) -> bool:
    if has_permission(user.role, Permission.ORG_MANAGE_ALL):
        return True
    if organization.owner_id == user.id:
        return True
    return get_organization_member_role(db, organization.id, user.id) is not None


def can_manage_organization(db: Session, user: User, organization: Organization) -> bool:
    if has_permission(user.role, Permission.ORG_MANAGE_ALL):
        return True
    if organization.owner_id == user.id:
        return True
    return get_organization_member_role(db, organization.id, user.id) == "admin"


def can_view_project(db: Session, user: User, project: Project) -> bool:
    if has_permission(user.role, Permission.PROJECT_VIEW_ALL):
        return True
    if project.owner_id == user.id:
        return True
    if project.organization_id and get_organization_member_role(db, project.organization_id, user.id) is not None:
        return True
    return get_project_member_role(db, project.id, user.id) is not None


def can_manage_project(db: Session, user: User, project: Project) -> bool:
    if has_permission(user.role, Permission.PROJECT_UPDATE_ALL):
        return True
    if project.owner_id == user.id:
        return True
    if project.organization_id and get_organization_member_role(db, project.organization_id, user.id) == "admin":
        return True
    return get_project_member_role(db, project.id, user.id) == "maintainer"


def can_delete_project(user: User, project: Project) -> bool:
    return has_permission(user.role, Permission.PROJECT_DELETE_ALL) or project.owner_id == user.id


def can_manage_project_members(db: Session, user: User, project: Project) -> bool:
    if has_permission(user.role, Permission.PROJECT_MEMBER_MANAGE_ALL):
        return True
    if project.owner_id == user.id:
        return True
    if project.organization_id and get_organization_member_role(db, project.organization_id, user.id) == "admin":
        return True
    return get_project_member_role(db, project.id, user.id) == "maintainer"


def can_manage_test_case(db: Session, user: User, project: Project) -> bool:
    if has_permission(user.role, Permission.TEST_CASE_MANAGE_ALL):
        return True
    if project.owner_id == user.id:
        return True
    if project.organization_id and get_organization_member_role(db, project.organization_id, user.id) == "admin":
        return True
    member_role = get_project_member_role(db, project.id, user.id)
    return member_role in {"maintainer", "editor"}


def can_view_test_case(db: Session, user: User, project: Project) -> bool:
    if has_permission(user.role, Permission.TEST_CASE_VIEW_ALL):
        return True
    if project.owner_id == user.id:
        return True
    if project.organization_id and get_organization_member_role(db, project.organization_id, user.id) is not None:
        return True
    return get_project_member_role(db, project.id, user.id) is not None


def can_execute_test_run(db: Session, user: User, project: Project) -> bool:
    if has_permission(user.role, Permission.TEST_RUN_EXECUTE_ALL):
        return True
    if project.owner_id == user.id:
        return True
    if project.organization_id and get_organization_member_role(db, project.organization_id, user.id) == "admin":
        return True
    member_role = get_project_member_role(db, project.id, user.id)
    return member_role in {"maintainer", "editor"}


def can_view_test_run(db: Session, user: User, project: Project) -> bool:
    if has_permission(user.role, Permission.TEST_RUN_VIEW_ALL):
        return True
    if project.owner_id == user.id:
        return True
    if project.organization_id and get_organization_member_role(db, project.organization_id, user.id) is not None:
        return True
    return get_project_member_role(db, project.id, user.id) is not None
