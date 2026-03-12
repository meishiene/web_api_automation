from typing import Literal

from pydantic import BaseModel, Field


OrganizationMemberRole = Literal["admin", "member"]
ProjectMemberRole = Literal["maintainer", "editor", "viewer"]


class OrganizationCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class OrganizationResponse(BaseModel):
    id: int
    name: str
    owner_id: int
    created_at: int


class OrganizationMemberCreateRequest(BaseModel):
    user_id: int = Field(..., ge=1)
    role: OrganizationMemberRole = "member"


class OrganizationMemberResponse(BaseModel):
    id: int
    organization_id: int
    user_id: int
    role: OrganizationMemberRole
    created_at: int


class OrganizationProjectAttachRequest(BaseModel):
    project_id: int = Field(..., ge=1)


class CrossProjectMemberGovernanceRequest(BaseModel):
    user_id: int = Field(..., ge=1)
    project_role: ProjectMemberRole


class CrossProjectMemberGovernanceResponse(BaseModel):
    organization_id: int
    user_id: int
    project_role: ProjectMemberRole
    affected_projects: int
