from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import ORMModel
from app.schemas.user import UserPublic

INTEGRATION_TYPES = {"cicd", "notification", "defect", "identity", "webhook"}
NOTIFICATION_CHANNEL_TYPES = {"webhook", "email"}


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


class IntegrationCicdTriggerRequest(BaseModel):
    pipeline_name: str = Field(min_length=1, max_length=200)
    ref: Optional[str] = Field(default=None, max_length=200)
    idempotency_key: Optional[str] = Field(default=None, max_length=128)
    inputs: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("pipeline_name")
    @classmethod
    def validate_pipeline_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Pipeline name must not be empty")
        return normalized

    @field_validator("ref", "idempotency_key", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class IntegrationCicdTriggerResponse(BaseModel):
    event: IntegrationEventResponse
    idempotent_reused: bool = False


class IntegrationCicdCallbackResponse(BaseModel):
    callback_event: IntegrationEventResponse
    trigger_event: IntegrationEventResponse
    idempotent_reused: bool = False


class NotificationSubscriptionCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    event_type: str = Field(min_length=1, max_length=100)
    channel_type: str = Field(min_length=1, max_length=20)
    destination: str = Field(min_length=1, max_length=500)
    is_enabled: bool = True
    max_attempts: int = Field(default=3, ge=1, le=10)

    @field_validator("name", "event_type", "destination")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Field must not be empty")
        return normalized

    @field_validator("channel_type")
    @classmethod
    def validate_channel_type(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in NOTIFICATION_CHANNEL_TYPES:
            raise ValueError("Unsupported notification channel type")
        return normalized


class NotificationSubscriptionResponse(ORMModel):
    id: int
    project_id: int
    name: str
    event_type: str
    channel_type: str
    destination: str
    is_enabled: bool
    max_attempts: int
    created_by: Optional[int]
    created_at: int
    updated_at: int


class NotificationSubscriptionListResponse(BaseModel):
    total: int
    items: List[NotificationSubscriptionResponse]


class NotificationDispatchRequest(BaseModel):
    event_type: str = Field(min_length=1, max_length=100)
    payload: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("event_type must not be empty")
        return normalized


class NotificationDeliveryResponse(ORMModel):
    id: int
    subscription_id: int
    project_id: int
    event_type: str
    channel_type: str
    destination: str
    payload_json: Dict[str, Any]
    status: str
    attempt_count: int
    max_attempts: int
    next_retry_at: Optional[int]
    last_error: Optional[str]
    last_attempt_at: Optional[int]
    created_at: int
    updated_at: int


class NotificationDeliveryListResponse(BaseModel):
    total: int
    items: List[NotificationDeliveryResponse]

DEFECT_RUN_TYPES = {"api", "web"}


class IntegrationDefectSyncRequest(BaseModel):
    run_type: str = Field(min_length=1, max_length=20)
    run_id: int = Field(ge=1)
    case_id: Optional[int] = Field(default=None, ge=1)
    case_name: str = Field(min_length=1, max_length=255)
    status: str = Field(min_length=1, max_length=20)
    failure_message: Optional[str] = None
    failure_category: Optional[str] = Field(default=None, max_length=100)
    failure_fingerprint: Optional[str] = Field(default=None, max_length=128)
    detail_api_path: Optional[str] = Field(default=None, max_length=500)
    tags: List[str] = Field(default_factory=list)
    extra: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("run_type")
    @classmethod
    def validate_run_type(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in DEFECT_RUN_TYPES:
            raise ValueError("Unsupported run type")
        return normalized

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in {"failed", "error"}:
            raise ValueError("status must be failed or error")
        return normalized

    @field_validator("case_name")
    @classmethod
    def validate_case_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("case_name must not be empty")
        return normalized

    @field_validator("failure_fingerprint", "detail_api_path", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class DefectSyncRecordResponse(ORMModel):
    id: int
    integration_config_id: int
    project_id: int
    run_type: str
    last_run_id: int
    case_id: Optional[int]
    case_name: str
    failure_fingerprint: str
    failure_category: Optional[str]
    failure_message: Optional[str]
    issue_key: str
    issue_url: Optional[str]
    issue_status: str
    summary: str
    detail_api_path: Optional[str]
    tags: List[str]
    occurrence_count: int
    created_by: Optional[int]
    created_at: int
    updated_at: int


class IntegrationDefectSyncResponse(BaseModel):
    mode: str
    record: DefectSyncRecordResponse
    event: IntegrationEventResponse


class DefectSyncRecordListResponse(BaseModel):
    total: int
    items: List[DefectSyncRecordResponse]


class IntegrationIdentityOAuthStartRequest(BaseModel):
    redirect_uri: Optional[str] = Field(default=None, max_length=500)

    @field_validator("redirect_uri", mode="before")
    @classmethod
    def normalize_redirect_uri(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class IntegrationIdentityOAuthStartResponse(BaseModel):
    state: str
    authorize_url: str
    expires_at: int


class IntegrationIdentityOAuthCallbackRequest(BaseModel):
    state: str = Field(min_length=8, max_length=128)
    code: str = Field(min_length=1, max_length=500)
    mock_userinfo: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("state", "code")
    @classmethod
    def normalize_required_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Field must not be empty")
        return normalized


class IdentityProviderBindingResponse(ORMModel):
    id: int
    integration_config_id: int
    project_id: int
    provider: str
    user_id: int
    external_subject: str
    external_email: Optional[str]
    last_login_at: Optional[int]
    created_at: int
    updated_at: int


class IdentityProviderBindingListResponse(BaseModel):
    total: int
    items: List[IdentityProviderBindingResponse]


class IntegrationIdentityOAuthCallbackResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: UserPublic
    binding_mode: str
    binding: IdentityProviderBindingResponse



class IntegrationGovernanceBulkRetryRequest(BaseModel):
    max_events: int = Field(default=20, ge=1, le=200)
    max_deliveries: int = Field(default=20, ge=1, le=200)


class IntegrationGovernanceFailureItem(BaseModel):
    source: str
    record_id: int
    status: str
    message: Optional[str]
    updated_at: int


class IntegrationGovernanceHealthResponse(BaseModel):
    project_id: int
    generated_at: int
    config_counts: Dict[str, int]
    event_status_counts: Dict[str, int]
    delivery_status_counts: Dict[str, int]
    retry_backlog: Dict[str, int]
    identity_binding_count: int
    defect_open_count: int
    recent_failures: List[IntegrationGovernanceFailureItem]


class IntegrationGovernanceBulkRetryResponse(BaseModel):
    project_id: int
    retried_events: int
    retried_deliveries: int
    skipped_events: int
    skipped_deliveries: int


class IntegrationGovernanceEventRetryResponse(BaseModel):
    event: IntegrationEventResponse
