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
    group_name: Optional[str] = Field(default=None, max_length=100)

    @field_validator("key")
    @classmethod
    def validate_key(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Variable key must not be empty")
        return normalized

    @field_validator("group_name")
    @classmethod
    def validate_group_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("Variable group name must not be empty")
        return normalized


class VariableResponse(ORMModel):
    id: int
    key: str
    value: str
    is_secret: bool
    group_name: Optional[str]
    created_at: int
    updated_at: int


class VariableGroupBindRequest(BaseModel):
    group_name: str = Field(min_length=1, max_length=100)

    @field_validator("group_name")
    @classmethod
    def validate_group_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Group name must not be empty")
        return normalized


class VariableGroupSummaryResponse(ORMModel):
    group_name: str
    variable_count: int
    secret_count: int


class EnvironmentVariableGroupResponse(ORMModel):
    id: int
    environment_id: int
    group_name: str
    created_at: int
    updated_at: int


class SecretValueResponse(ORMModel):
    key: str
    value: str
    scope: str
