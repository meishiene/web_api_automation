from enum import Enum
from typing import Iterable, Set


class Permission(str, Enum):
    ORG_MANAGE_ALL = "organization.manage_all"
    PROJECT_VIEW_ALL = "project.view_all"
    PROJECT_UPDATE_ALL = "project.update_all"
    PROJECT_DELETE_ALL = "project.delete_all"
    PROJECT_MEMBER_MANAGE_ALL = "project.member.manage_all"
    TEST_CASE_VIEW_ALL = "test_case.view_all"
    TEST_CASE_MANAGE_ALL = "test_case.manage_all"
    TEST_RUN_EXECUTE_ALL = "test_run.execute_all"
    TEST_RUN_VIEW_ALL = "test_run.view_all"
    AUDIT_LOG_VIEW_ALL = "audit_log.view_all"
    AUDIT_GOVERNANCE_RUN = "audit_log.governance.run"


ROLE_PERMISSIONS: dict[str, Set[str]] = {
    "user": set(),
    "admin": {permission.value for permission in Permission},
}


def has_permission(role: str, permission: Permission | str) -> bool:
    permission_name = permission.value if isinstance(permission, Permission) else str(permission)
    return permission_name in ROLE_PERMISSIONS.get((role or "").lower(), set())


def has_any_permission(role: str, permissions: Iterable[Permission | str]) -> bool:
    return any(has_permission(role, permission) for permission in permissions)
