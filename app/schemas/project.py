from pydantic import BaseModel, Field, field_validator

from app.schemas.common import ORMModel


class ProjectCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = ""

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Project name must not be empty")
        return normalized


class ProjectResponse(ORMModel):
    id: int
    name: str
    description: str
    owner_id: int
    created_at: int
