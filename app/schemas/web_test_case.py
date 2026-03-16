import json
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

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
    steps: List[WebStepIn] = Field(default_factory=list)


class WebTestCaseUpdateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    base_url: Optional[str] = Field(default=None, max_length=500)
    steps: List[WebStepIn] = Field(default_factory=list)


class WebTestCaseResponse(ORMModel):
    id: int
    project_id: int
    name: str
    description: Optional[str] = None
    base_url: Optional[str] = None
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

