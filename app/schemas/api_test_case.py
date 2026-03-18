import json
from typing import Any, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.common import ORMModel


class TestCaseCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
    url: str = Field(min_length=1, max_length=500)
    case_group: Optional[str] = Field(default=None, max_length=100)
    tags: List[str] = Field(default_factory=list)
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

    @field_validator("case_group")
    @classmethod
    def normalize_case_group(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    @field_validator("tags", mode="before")
    @classmethod
    def normalize_tags(cls, value: Any) -> List[str]:
        if value is None or value == "":
            return []
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid tags JSON: {exc}")
        if not isinstance(value, list):
            raise ValueError("tags must be an array")

        normalized: List[str] = []
        seen: set[str] = set()
        for item in value:
            if not isinstance(item, str):
                raise ValueError("tags must be an array of strings")
            tag = item.strip()
            if not tag:
                continue
            if tag in seen:
                continue
            seen.add(tag)
            normalized.append(tag)
        return normalized

    @field_validator("method", mode="before")
    @classmethod
    def normalize_method(cls, value: str) -> str:
        if isinstance(value, str):
            return value.upper().strip()
        return value


class TestCaseCopyRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)


class TestCaseImportItem(TestCaseCreateRequest):
    model_config = ConfigDict(extra="ignore")


class TestCaseImportRequest(BaseModel):
    cases: List[TestCaseImportItem] = Field(default_factory=list)
    skip_duplicates: bool = True



class TestCaseOpenApiImportRequest(BaseModel):
    spec: dict[str, Any]
    base_url: Optional[str] = Field(default=None, max_length=500)
    case_group: Optional[str] = Field(default="openapi-import", max_length=100)
    tags: List[str] = Field(default_factory=list)
    skip_duplicates: bool = True

    @field_validator("base_url", "case_group", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    @field_validator("tags", mode="before")
    @classmethod
    def normalize_import_tags(cls, value: Any) -> List[str]:
        if value is None or value == "":
            return []
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid tags JSON: {exc}")
        if not isinstance(value, list):
            raise ValueError("tags must be an array")

        normalized: List[str] = []
        seen: set[str] = set()
        for item in value:
            if not isinstance(item, str):
                raise ValueError("tags must be an array of strings")
            tag = item.strip()
            if not tag:
                continue
            if tag in seen:
                continue
            seen.add(tag)
            normalized.append(tag)
        return normalized


class TestCaseProviderImportRequest(BaseModel):
    provider: Optional[str] = Field(default=None, max_length=50)
    payload: dict[str, Any] = Field(default_factory=dict)

    @field_validator("provider", mode="before")
    @classmethod
    def normalize_provider(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip().lower()
        return normalized or None
class TestCaseImportResponse(BaseModel):
    imported: int
    skipped: int
    created_case_ids: List[int]


class TestCaseImportProviderListResponse(BaseModel):
    providers: List[str]
    default_provider: Optional[str] = None


class TestCaseExportResponse(BaseModel):
    project_id: int
    total_cases: int
    cases: List[TestCaseCreateRequest]


class TestCaseResponse(ORMModel):
    id: int
    name: str
    project_id: int
    method: str
    url: str
    case_group: Optional[str]
    tags: List[str]
    headers: Optional[str]
    body: Optional[str]
    expected_status: int
    expected_body: Optional[str]
    assertion_rules: Optional[str]
    extraction_rules: Optional[str]
    created_at: int
    updated_at: int

