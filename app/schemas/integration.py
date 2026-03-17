from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import ORMModel

INTEGRATION_TYPES = {"cicd", "notification", "defect", "identity", "webhook"}


class IntegrationConfigBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    integration_type: str = Field(min_length=1, max_length=20)
    provider: str = Field(min_length=1, max_length=100)
    base_url: Optional[str] = Field(default=None, max_length=500)
    credential_ref: Optional[str] = Field(default=None, max_length=200)
    credential_value: Optional[str] = None
    config_json: Dict[str, Any] = Field(default_factory=dict)
    is_enabled: bool = True

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Integration config name must not be empty")
        return normalized

    @field_validator("integration_type")
    @classmethod
    def validate_integration_type(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in INTEGRATION_TYPES:
            raise ValueError("Unsupported integration type")
        return normalized

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not normalized:
            raise ValueError("Provider must not be empty")
        return normalized

    @field_validator("base_url", "credential_ref", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class IntegrationConfigCreateRequest(IntegrationConfigBase):
    pass


class IntegrationConfigUpdateRequest(IntegrationConfigBase):
    pass


class IntegrationConfigResponse(ORMModel):
    id: int
    project_id: int
    name: str
    integration_type: str
    provider: str
    base_url: Optional[str]
    credential_ref: Optional[str]
    credential_value: Optional[str]
    has_credential_value: bool
    config_json: Dict[str, Any]
    is_enabled: bool
    created_by: Optional[int]
    created_at: int
    updated_at: int


class IntegrationCredentialValueResponse(BaseModel):
    value: str


class IntegrationEventResponse(ORMModel):
    id: int
    integration_config_id: int
    project_id: int
    event_type: str
    direction: str
    status: str
    payload_json: Dict[str, Any]
    headers_json: Dict[str, Any]
    signature: Optional[str]
    idempotency_key: str
    attempt_count: int
    max_attempts: int
    next_retry_at: Optional[int]
    last_error: Optional[str]
    last_processed_at: Optional[int]
    created_at: int
    updated_at: int


class IntegrationWebhookIngestResponse(BaseModel):
    event: IntegrationEventResponse
    idempotent_reused: bool = False


class IntegrationEventListResponse(BaseModel):
    total: int
    items: List[IntegrationEventResponse]
