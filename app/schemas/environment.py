from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import ORMModel


class EnvironmentCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = ""

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Environment name must not be empty")
        return normalized


class EnvironmentResponse(ORMModel):
    id: int
    project_id: int
    name: str
    description: Optional[str]
    created_by: int
    created_at: int
    updated_at: int


class VariableUpsertRequest(BaseModel):
    key: str = Field(min_length=1, max_length=100)
    value: str
    is_secret: bool = False

    @field_validator("key")
    @classmethod
    def validate_key(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Variable key must not be empty")
        return normalized


class VariableResponse(ORMModel):
    id: int
    key: str
    value: str
    is_secret: bool
    created_at: int
    updated_at: int
