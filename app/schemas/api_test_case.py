from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import ORMModel


class TestCaseCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
    url: str = Field(min_length=1, max_length=500)
    headers: Optional[str] = None
    body: Optional[str] = None
    expected_status: int = Field(default=200, ge=100, lt=600)
    expected_body: Optional[str] = None
    assertion_rules: Optional[str] = None
    extraction_rules: Optional[str] = None

    @field_validator("name", "url")
    @classmethod
    def validate_non_blank_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Field must not be empty")
        return normalized

    @field_validator("method", mode="before")
    @classmethod
    def normalize_method(cls, value: str) -> str:
        if isinstance(value, str):
            return value.upper().strip()
        return value


class TestCaseResponse(ORMModel):
    id: int
    name: str
    project_id: int
    method: str
    url: str
    headers: Optional[str]
    body: Optional[str]
    expected_status: int
    expected_body: Optional[str]
    assertion_rules: Optional[str]
    extraction_rules: Optional[str]
    created_at: int
    updated_at: int
