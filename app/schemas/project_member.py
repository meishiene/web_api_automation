from typing import Literal, Optional

from pydantic import BaseModel, Field


ProjectMemberRole = Literal["maintainer", "editor", "viewer"]


class ProjectMemberCreateRequest(BaseModel):
    user_id: int = Field(..., ge=1)
    role: ProjectMemberRole = "viewer"


class ProjectMemberResponse(BaseModel):
    id: int
    project_id: int
    user_id: int
    role: ProjectMemberRole
    created_at: int
    username: Optional[str] = None
