import json
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import ORMModel


class WebStepIn(BaseModel):
    action: str = Field(..., min_length=1)
    params: Dict[str, Any] = Field(default_factory=dict)


class WebStepResponse(ORMModel):
    id: int
    order_index: int
    action: str
    params: Dict[str, Any] = Field(default_factory=dict)


class WebTestCaseCreateRequest(BaseModel):
    project_id: int
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    base_url: Optional[str] = Field(default=None, max_length=500)
    browser_name: Literal["chromium", "firefox", "webkit"] = "chromium"
    viewport_width: Optional[int] = Field(default=1920, ge=320, le=4096)
    viewport_height: Optional[int] = Field(default=1080, ge=320, le=4096)
    timeout_ms: Optional[int] = Field(default=30000, ge=100, le=300000)
    headless: bool = True
    capture_on_failure: bool = True
    record_video: bool = False
    steps: List[WebStepIn] = Field(default_factory=list)

    @field_validator("name", "description", "base_url", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        if not isinstance(value, str):
            return value
        normalized = value.strip()
        return normalized or None


class WebTestCaseUpdateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    base_url: Optional[str] = Field(default=None, max_length=500)
    browser_name: Literal["chromium", "firefox", "webkit"] = "chromium"
    viewport_width: Optional[int] = Field(default=1920, ge=320, le=4096)
    viewport_height: Optional[int] = Field(default=1080, ge=320, le=4096)
    timeout_ms: Optional[int] = Field(default=30000, ge=100, le=300000)
    headless: bool = True
    capture_on_failure: bool = True
    record_video: bool = False
    steps: List[WebStepIn] = Field(default_factory=list)

    @field_validator("name", "description", "base_url", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        if not isinstance(value, str):
            return value
        normalized = value.strip()
        return normalized or None


class WebTestCaseResponse(ORMModel):
    id: int
    project_id: int
    name: str
    description: Optional[str] = None
    base_url: Optional[str] = None
    browser_name: Literal["chromium", "firefox", "webkit"] = "chromium"
    viewport_width: Optional[int] = None
    viewport_height: Optional[int] = None
    timeout_ms: Optional[int] = None
    headless: bool = True
    capture_on_failure: bool = True
    record_video: bool = False
    steps: List[WebStepResponse] = Field(default_factory=list)
    created_at: int
    updated_at: int


def parse_params(raw: str | None) -> Dict[str, Any]:
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}
