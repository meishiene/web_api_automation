from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import ORMModel


class TestSuiteCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = ""

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Suite name must not be empty")
        return normalized


class TestSuiteCaseUpsertRequest(BaseModel):
    order_index: int = Field(default=0, ge=0)


class TestSuiteResponse(ORMModel):
    id: int
    project_id: int
    name: str
    description: Optional[str]
    created_by: int
    created_at: int
    updated_at: int
    case_count: int = 0


class TestSuiteCaseResponse(ORMModel):
    id: int
    suite_id: int
    test_case_id: int
    order_index: int
    created_at: int
    test_case_name: Optional[str] = None
