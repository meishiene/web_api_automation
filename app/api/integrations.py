import hashlib
import hmac
import json
import time
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.errors import AppException, ErrorCode
from app.models.integration_config import IntegrationConfig
from app.models.integration_event import IntegrationEvent
from app.models.notification_delivery import NotificationDelivery
from app.models.notification_subscription import NotificationSubscription
from app.models.project import Project
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.integration import (
    IntegrationCicdCallbackResponse,
    IntegrationCicdTriggerRequest,
    IntegrationCicdTriggerResponse,
    IntegrationConfigCreateRequest,
    IntegrationConfigResponse,
    IntegrationConfigUpdateRequest,
    IntegrationCredentialValueResponse,
    IntegrationEventListResponse,
    IntegrationEventResponse,
    IntegrationWebhookIngestResponse,
    NotificationDeliveryListResponse,
    NotificationDeliveryResponse,
    NotificationDispatchRequest,
    NotificationSubscriptionCreateRequest,
    NotificationSubscriptionListResponse,
    NotificationSubscriptionResponse,
)
from app.services.access_control import can_manage_test_case, can_view_test_case
from app.services.audit_service import create_audit_log
from app.services.variable_resolver import mask_secret_value

router = APIRouter()


def _serialize_config_json(raw: str | None) -> dict:
    if not raw:
        return {}
    try:
        value = json.loads(raw)
    except (TypeError, ValueError):
        return {}
    return value if isinstance(value, dict) else {}


def _serialize_event_json(raw: str | None) -> dict:
    if not raw:
        return {}
    try:
        value = json.loads(raw)
    except (TypeError, ValueError):
        return {}
    if isinstance(value, dict):
        return value
    return {"data": value}


def _to_response(item: IntegrationConfig) -> IntegrationConfigResponse:
    has_credential_value = bool(item.credential_value)
    return IntegrationConfigResponse(
        id=item.id,
        project_id=item.project_id,
        name=item.name,
        integration_type=item.integration_type,
        provider=item.provider,
        base_url=item.base_url,
        credential_ref=item.credential_ref,
        credential_value=mask_secret_value(item.credential_value or "", has_credential_value) if has_credential_value else None,
        has_credential_value=has_credential_value,
        config_json=_serialize_config_json(item.config_json),
        is_enabled=bool(item.is_enabled),
        created_by=item.created_by,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _to_event_response(item: IntegrationEvent) -> IntegrationEventResponse:
    return IntegrationEventResponse(
        id=item.id,
        integration_config_id=item.integration_config_id,
        project_id=item.project_id,
        event_type=item.event_type,
        direction=item.direction,
        status=item.status,
        payload_json=_serialize_event_json(item.payload_json),
        headers_json=_serialize_event_json(item.headers_json),
        signature=item.signature,
        idempotency_key=item.idempotency_key,
        attempt_count=item.attempt_count,
        max_attempts=item.max_attempts,
        next_retry_at=item.next_retry_at,
        last_error=item.last_error,
        last_processed_at=item.last_processed_at,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _to_subscription_response(item: NotificationSubscription) -> NotificationSubscriptionResponse:
    return NotificationSubscriptionResponse(
        id=item.id,
        project_id=item.project_id,
        name=item.name,
        event_type=item.event_type,
        channel_type=item.channel_type,
        destination=item.destination,
        is_enabled=bool(item.is_enabled),
        max_attempts=item.max_attempts,
        created_by=item.created_by,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _to_delivery_response(item: NotificationDelivery) -> NotificationDeliveryResponse:
    return NotificationDeliveryResponse(
        id=item.id,
        subscription_id=item.subscription_id,
        project_id=item.project_id,
        event_type=item.event_type,
        channel_type=item.channel_type,
        destination=item.destination,
        payload_json=_serialize_event_json(item.payload_json),
        status=item.status,
        attempt_count=item.attempt_count,
        max_attempts=item.max_attempts,
        next_retry_at=item.next_retry_at,
        last_error=item.last_error,
        last_attempt_at=item.last_attempt_at,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _ensure_project_and_permission(db: Session, project_id: int, user: User, manage: bool) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise AppException(404, ErrorCode.PROJECT_NOT_FOUND, "Project not found")

    allowed = can_manage_test_case(db, user, project) if manage else can_view_test_case(db, user, project)
    if not allowed:
        raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")
    return project


def _ensure_integration_and_permission(db: Session, config_id: int, user: User, manage: bool) -> tuple[IntegrationConfig, Project]:
    config = db.query(IntegrationConfig).filter(IntegrationConfig.id == config_id).first()
    if not config:
        raise AppException(404, ErrorCode.INTEGRATION_CONFIG_NOT_FOUND, "Integration config not found")

    project = _ensure_project_and_permission(db, config.project_id, user, manage=manage)
    return config, project


def _ensure_event_and_permission(db: Session, event_id: int, user: User, manage: bool) -> tuple[IntegrationEvent, Project]:
    event = db.query(IntegrationEvent).filter(IntegrationEvent.id == event_id).first()
    if not event:
        raise AppException(404, ErrorCode.INTEGRATION_EVENT_NOT_FOUND, "Integration event not found")
    project = _ensure_project_and_permission(db, event.project_id, user, manage=manage)
    return event, project


def _ensure_subscription_and_permission(
    db: Session,
    subscription_id: int,
    user: User,
    manage: bool,
) -> tuple[NotificationSubscription, Project]:
    subscription = db.query(NotificationSubscription).filter(NotificationSubscription.id == subscription_id).first()
    if not subscription:
        raise AppException(404, ErrorCode.NOTIFICATION_SUBSCRIPTION_NOT_FOUND, "Notification subscription not found")
    project = _ensure_project_and_permission(db, subscription.project_id, user, manage=manage)
    return subscription, project


def _ensure_delivery_and_permission(
    db: Session,
    delivery_id: int,
    user: User,
    manage: bool,
) -> tuple[NotificationDelivery, Project]:
    delivery = db.query(NotificationDelivery).filter(NotificationDelivery.id == delivery_id).first()
    if not delivery:
        raise AppException(404, ErrorCode.NOTIFICATION_DELIVERY_NOT_FOUND, "Notification delivery not found")
    project = _ensure_project_and_permission(db, delivery.project_id, user, manage=manage)
    return delivery, project


def _normalize_signature(raw_signature: str) -> str:
    normalized = raw_signature.strip()
    if normalized.startswith("sha256="):
        return normalized.split("=", 1)[1].strip()
    return normalized


def _calculate_hmac_sha256(secret: str, body: bytes) -> str:
    return hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()


def _build_idempotency_key(request: Request, body: bytes) -> str:
    header_key = (request.headers.get("X-Idempotency-Key") or "").strip()
    if header_key:
        return header_key
    return hashlib.sha256(body).hexdigest()


def _build_headers_snapshot(request: Request) -> dict[str, str]:
    allowed = ["content-type", "user-agent", "x-request-id", "x-webhook-signature", "x-idempotency-key"]
    output: dict[str, str] = {}
    for key in allowed:
        value = request.headers.get(key)
        if value is not None:
            output[key] = value
    return output


def _extract_payload(raw_body: bytes) -> dict[str, Any]:
    if not raw_body:
        return {}
    text = raw_body.decode("utf-8", errors="replace")
    try:
        parsed = json.loads(text)
    except ValueError:
        return {"raw": text}
    if isinstance(parsed, dict):
        return parsed
    return {"data": parsed}


def _resolve_max_attempts(config: IntegrationConfig) -> int:
    config_json = _serialize_config_json(config.config_json)
    raw_value = config_json.get("max_attempts", 3)
    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        return 3
    if value < 1:
        return 1
    if value > 10:
        return 10
    return value


def _process_event(event: IntegrationEvent, payload: dict[str, Any], now: int) -> None:
    event.attempt_count += 1
    event.last_processed_at = now
    event.next_retry_at = None
    event.last_error = None

    if payload.get("force_fail"):
        event.last_error = "forced failure for testing"
        if event.attempt_count < event.max_attempts:
            event.status = "retry_pending"
            event.next_retry_at = now + 60
        else:
            event.status = "failed"
        return

    event.status = "processed"


def _ensure_cicd_config(config: IntegrationConfig) -> None:
    if config.integration_type != "cicd":
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "Integration config is not cicd type")
    if not bool(config.is_enabled):
        raise AppException(400, ErrorCode.INTEGRATION_CONFIG_DISABLED, "Integration config is disabled")


def _build_cicd_trigger_idempotency_key(config_id: int, payload: IntegrationCicdTriggerRequest) -> str:
    if payload.idempotency_key:
        return payload.idempotency_key
    base = json.dumps(
        {
            "pipeline_name": payload.pipeline_name,
            "ref": payload.ref,
            "inputs": payload.inputs,
        },
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha256(f"{config_id}:{base}".encode("utf-8")).hexdigest()


def _map_cicd_status(trigger_event: IntegrationEvent, callback_status: str, message: str | None, external_run_id: str | None, now: int) -> None:
    normalized = callback_status.strip().lower()
    payload = _serialize_event_json(trigger_event.payload_json)
    payload["callback_status"] = normalized
    if external_run_id:
        payload["external_run_id"] = external_run_id
    if message:
        payload["callback_message"] = message
    trigger_event.payload_json = json.dumps(payload, ensure_ascii=False)
    trigger_event.last_processed_at = now
    trigger_event.next_retry_at = None
    trigger_event.last_error = None

    if normalized in {"success", "succeeded", "completed"}:
        trigger_event.status = "processed"
        return
    if normalized in {"failed", "error", "cancelled"}:
        trigger_event.status = "failed"
        trigger_event.last_error = message or f"cicd callback status: {normalized}"
        return
    trigger_event.status = "retry_pending"
    trigger_event.next_retry_at = now + 60
    trigger_event.last_error = message or f"cicd callback status: {normalized}"


def _mock_notification_send(destination: str, attempt_count: int) -> tuple[bool, str | None]:
    if destination.startswith("mock://success"):
        return True, None
    if destination.startswith("mock://flaky"):
        if attempt_count >= 2:
            return True, None
        return False, "flaky channel temporary failure"
    if destination.startswith("mock://always-fail") or destination.startswith("mock://fail"):
        return False, "mock channel failure"
    # For non-mock destinations we keep optimistic success in this stage.
    return True, None


def _apply_notification_delivery_result(delivery: NotificationDelivery, success: bool, error: str | None, now: int) -> None:
    if success:
        delivery.status = "sent"
        delivery.last_error = None
        delivery.next_retry_at = None
        return

    delivery.last_error = error or "notification delivery failed"
    if delivery.attempt_count < delivery.max_attempts:
        delivery.status = "retry_pending"
        delivery.next_retry_at = now + 60
        return
    delivery.status = "dead_letter"
    delivery.next_retry_at = None


@router.get("/project/{project_id}", response_model=List[IntegrationConfigResponse])
def list_integrations(
    project_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[IntegrationConfigResponse]:
    _ensure_project_and_permission(db, project_id, user, manage=False)
    items = (
        db.query(IntegrationConfig)
        .filter(IntegrationConfig.project_id == project_id)
        .order_by(IntegrationConfig.id.asc())
        .all()
    )

    create_audit_log(
        db=db,
        request=request,
        action="integration_config.list",
        resource_type="integration_config",
        resource_id=str(project_id),
        user_id=user.id,
        details={"project_id": project_id, "count": len(items)},
    )
    return [_to_response(item) for item in items]


@router.get("/{config_id}", response_model=IntegrationConfigResponse)
def get_integration(
    config_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> IntegrationConfigResponse:
    config, _project = _ensure_integration_and_permission(db, config_id, user, manage=False)
    create_audit_log(
        db=db,
        request=request,
        action="integration_config.get",
        resource_type="integration_config",
        resource_id=str(config.id),
        user_id=user.id,
        details={"project_id": config.project_id},
    )
    return _to_response(config)


@router.post("/project/{project_id}", response_model=IntegrationConfigResponse)
def create_integration(
    project_id: int,
    payload: IntegrationConfigCreateRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> IntegrationConfigResponse:
    _ensure_project_and_permission(db, project_id, user, manage=True)

    duplicated = (
        db.query(IntegrationConfig)
        .filter(IntegrationConfig.project_id == project_id, IntegrationConfig.name == payload.name)
        .first()
    )
    if duplicated:
        raise AppException(400, ErrorCode.INTEGRATION_CONFIG_ALREADY_EXISTS, "Integration config name already exists")

    now = int(time.time())
    config = IntegrationConfig(
        project_id=project_id,
        name=payload.name,
        integration_type=payload.integration_type,
        provider=payload.provider,
        base_url=payload.base_url,
        credential_ref=payload.credential_ref,
        credential_value=payload.credential_value,
        config_json=json.dumps(payload.config_json, ensure_ascii=False),
        is_enabled=1 if payload.is_enabled else 0,
        created_by=user.id,
        created_at=now,
        updated_at=now,
    )
    db.add(config)
    db.commit()
    db.refresh(config)

    create_audit_log(
        db=db,
        request=request,
        action="integration_config.create",
        resource_type="integration_config",
        resource_id=str(config.id),
        user_id=user.id,
        details={"project_id": project_id, "integration_type": payload.integration_type, "provider": payload.provider},
    )
    return _to_response(config)


@router.put("/{config_id}", response_model=IntegrationConfigResponse)
def update_integration(
    config_id: int,
    payload: IntegrationConfigUpdateRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> IntegrationConfigResponse:
    config, _project = _ensure_integration_and_permission(db, config_id, user, manage=True)

    duplicated = (
        db.query(IntegrationConfig)
        .filter(
            IntegrationConfig.project_id == config.project_id,
            IntegrationConfig.name == payload.name,
            IntegrationConfig.id != config.id,
        )
        .first()
    )
    if duplicated:
        raise AppException(400, ErrorCode.INTEGRATION_CONFIG_ALREADY_EXISTS, "Integration config name already exists")

    config.name = payload.name
    config.integration_type = payload.integration_type
    config.provider = payload.provider
    config.base_url = payload.base_url
    config.credential_ref = payload.credential_ref
    config.credential_value = payload.credential_value
    config.config_json = json.dumps(payload.config_json, ensure_ascii=False)
    config.is_enabled = 1 if payload.is_enabled else 0
    config.updated_at = int(time.time())
    db.commit()
    db.refresh(config)

    create_audit_log(
        db=db,
        request=request,
        action="integration_config.update",
        resource_type="integration_config",
        resource_id=str(config.id),
        user_id=user.id,
        details={"project_id": config.project_id, "integration_type": payload.integration_type, "provider": payload.provider},
    )
    return _to_response(config)


@router.delete("/{config_id}", response_model=MessageResponse)
def delete_integration(
    config_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    config, _project = _ensure_integration_and_permission(db, config_id, user, manage=True)

    db.delete(config)
    db.commit()

    create_audit_log(
        db=db,
        request=request,
        action="integration_config.delete",
        resource_type="integration_config",
        resource_id=str(config_id),
        user_id=user.id,
        details={"project_id": config.project_id},
    )
    return {"message": "Integration config deleted"}


@router.get("/{config_id}/credential-value", response_model=IntegrationCredentialValueResponse)
def reveal_credential_value(
    config_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> IntegrationCredentialValueResponse:
    config, _project = _ensure_integration_and_permission(db, config_id, user, manage=True)
    if not config.credential_value:
        raise AppException(404, ErrorCode.VARIABLE_NOT_FOUND, "Credential value not found")

    create_audit_log(
        db=db,
        request=request,
        action="integration_config.reveal_credential",
        resource_type="integration_config",
        resource_id=str(config.id),
        user_id=user.id,
        details={"project_id": config.project_id},
    )
    return IntegrationCredentialValueResponse(value=config.credential_value)


@router.post("/project/{project_id}/notification-subscriptions", response_model=NotificationSubscriptionResponse)
def create_notification_subscription(
    project_id: int,
    payload: NotificationSubscriptionCreateRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NotificationSubscriptionResponse:
    _ensure_project_and_permission(db, project_id, user, manage=True)

    duplicated = (
        db.query(NotificationSubscription)
        .filter(
            NotificationSubscription.project_id == project_id,
            NotificationSubscription.name == payload.name,
        )
        .first()
    )
    if duplicated:
        raise AppException(400, ErrorCode.INTEGRATION_CONFIG_ALREADY_EXISTS, "Notification subscription name already exists")

    now = int(time.time())
    subscription = NotificationSubscription(
        project_id=project_id,
        name=payload.name,
        event_type=payload.event_type,
        channel_type=payload.channel_type,
        destination=payload.destination,
        is_enabled=1 if payload.is_enabled else 0,
        max_attempts=payload.max_attempts,
        created_by=user.id,
        created_at=now,
        updated_at=now,
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)

    create_audit_log(
        db=db,
        request=request,
        action="notification_subscription.create",
        resource_type="notification_subscription",
        resource_id=str(subscription.id),
        user_id=user.id,
        details={"project_id": project_id, "event_type": payload.event_type, "channel_type": payload.channel_type},
    )
    return _to_subscription_response(subscription)


@router.get("/project/{project_id}/notification-subscriptions", response_model=NotificationSubscriptionListResponse)
def list_notification_subscriptions(
    project_id: int,
    request: Request,
    page: int = 1,
    page_size: int = 20,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NotificationSubscriptionListResponse:
    _ensure_project_and_permission(db, project_id, user, manage=False)
    if page < 1 or page_size < 1 or page_size > 100:
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "Invalid pagination params")

    query = db.query(NotificationSubscription).filter(NotificationSubscription.project_id == project_id)
    total = query.count()
    items = (
        query.order_by(NotificationSubscription.created_at.desc(), NotificationSubscription.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    create_audit_log(
        db=db,
        request=request,
        action="notification_subscription.list",
        resource_type="notification_subscription",
        resource_id=str(project_id),
        user_id=user.id,
        details={"project_id": project_id, "count": len(items), "total": total},
    )
    return NotificationSubscriptionListResponse(total=total, items=[_to_subscription_response(item) for item in items])


@router.post("/notification-subscriptions/{subscription_id}/dispatch", response_model=NotificationDeliveryResponse)
def dispatch_notification(
    subscription_id: int,
    payload: NotificationDispatchRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NotificationDeliveryResponse:
    subscription, _project = _ensure_subscription_and_permission(db, subscription_id, user, manage=True)
    if not bool(subscription.is_enabled):
        raise AppException(400, ErrorCode.INTEGRATION_CONFIG_DISABLED, "Notification subscription is disabled")

    now = int(time.time())
    delivery = NotificationDelivery(
        subscription_id=subscription.id,
        project_id=subscription.project_id,
        event_type=payload.event_type,
        channel_type=subscription.channel_type,
        destination=subscription.destination,
        payload_json=json.dumps(payload.payload, ensure_ascii=False),
        status="pending",
        attempt_count=0,
        max_attempts=subscription.max_attempts,
        next_retry_at=None,
        last_error=None,
        last_attempt_at=None,
        created_at=now,
        updated_at=now,
    )
    db.add(delivery)
    db.flush()

    delivery.attempt_count += 1
    delivery.last_attempt_at = now
    success, error = _mock_notification_send(subscription.destination, delivery.attempt_count)
    _apply_notification_delivery_result(delivery, success, error, now)
    delivery.updated_at = now
    db.commit()
    db.refresh(delivery)

    create_audit_log(
        db=db,
        request=request,
        action="notification_subscription.dispatch",
        resource_type="notification_delivery",
        resource_id=str(delivery.id),
        user_id=user.id,
        details={"project_id": subscription.project_id, "subscription_id": subscription.id, "status": delivery.status},
    )
    return _to_delivery_response(delivery)


@router.post("/notification-deliveries/{delivery_id}/retry", response_model=NotificationDeliveryResponse)
def retry_notification_delivery(
    delivery_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NotificationDeliveryResponse:
    delivery, _project = _ensure_delivery_and_permission(db, delivery_id, user, manage=True)
    if delivery.status not in {"retry_pending", "dead_letter"}:
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "Delivery is not retryable")

    now = int(time.time())
    delivery.attempt_count += 1
    delivery.last_attempt_at = now
    success, error = _mock_notification_send(delivery.destination, delivery.attempt_count)
    _apply_notification_delivery_result(delivery, success, error, now)
    delivery.updated_at = now
    db.commit()
    db.refresh(delivery)

    create_audit_log(
        db=db,
        request=request,
        action="notification_delivery.retry",
        resource_type="notification_delivery",
        resource_id=str(delivery.id),
        user_id=user.id,
        details={"project_id": delivery.project_id, "status": delivery.status, "attempt_count": delivery.attempt_count},
    )
    return _to_delivery_response(delivery)


@router.get("/project/{project_id}/notification-deliveries", response_model=NotificationDeliveryListResponse)
def list_notification_deliveries(
    project_id: int,
    request: Request,
    subscription_id: int | None = None,
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NotificationDeliveryListResponse:
    _ensure_project_and_permission(db, project_id, user, manage=False)
    if page < 1 or page_size < 1 or page_size > 100:
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "Invalid pagination params")

    query = db.query(NotificationDelivery).filter(NotificationDelivery.project_id == project_id)
    if subscription_id is not None:
        query = query.filter(NotificationDelivery.subscription_id == subscription_id)
    if status:
        query = query.filter(NotificationDelivery.status == status.strip())
    total = query.count()
    items = (
        query.order_by(NotificationDelivery.created_at.desc(), NotificationDelivery.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    create_audit_log(
        db=db,
        request=request,
        action="notification_delivery.list",
        resource_type="notification_delivery",
        resource_id=str(project_id),
        user_id=user.id,
        details={"project_id": project_id, "count": len(items), "total": total},
    )
    return NotificationDeliveryListResponse(total=total, items=[_to_delivery_response(item) for item in items])


@router.post("/{config_id}/cicd/trigger", response_model=IntegrationCicdTriggerResponse)
def trigger_cicd_pipeline(
    config_id: int,
    payload: IntegrationCicdTriggerRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> IntegrationCicdTriggerResponse:
    config, _project = _ensure_integration_and_permission(db, config_id, user, manage=True)
    _ensure_cicd_config(config)

    idempotency_key = _build_cicd_trigger_idempotency_key(config.id, payload)
    existing = (
        db.query(IntegrationEvent)
        .filter(
            IntegrationEvent.integration_config_id == config.id,
            IntegrationEvent.idempotency_key == idempotency_key,
            IntegrationEvent.event_type == "cicd.trigger",
            IntegrationEvent.direction == "outbound",
        )
        .first()
    )
    if existing:
        create_audit_log(
            db=db,
            request=request,
            action="integration_cicd.trigger",
            resource_type="integration_event",
            resource_id=str(existing.id),
            user_id=user.id,
            details={"project_id": config.project_id, "idempotent_reused": True},
        )
        return IntegrationCicdTriggerResponse(event=_to_event_response(existing), idempotent_reused=True)

    now = int(time.time())
    event_payload: Dict[str, Any] = {
        "pipeline_name": payload.pipeline_name,
        "ref": payload.ref,
        "inputs": payload.inputs,
    }
    event = IntegrationEvent(
        integration_config_id=config.id,
        project_id=config.project_id,
        event_type="cicd.trigger",
        direction="outbound",
        status="received",
        payload_json=json.dumps(event_payload, ensure_ascii=False),
        headers_json=json.dumps({"triggered_by": user.username, "request_id": getattr(request.state, "request_id", "-")}, ensure_ascii=False),
        signature=None,
        idempotency_key=idempotency_key,
        attempt_count=1,
        max_attempts=1,
        next_retry_at=None,
        last_error=None,
        last_processed_at=now,
        created_at=now,
        updated_at=now,
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    create_audit_log(
        db=db,
        request=request,
        action="integration_cicd.trigger",
        resource_type="integration_event",
        resource_id=str(event.id),
        user_id=user.id,
        details={"project_id": config.project_id, "idempotent_reused": False, "pipeline_name": payload.pipeline_name},
    )
    return IntegrationCicdTriggerResponse(event=_to_event_response(event), idempotent_reused=False)


@router.post("/webhooks/{config_id}/cicd/callback", response_model=IntegrationCicdCallbackResponse)
async def receive_cicd_callback(
    config_id: int,
    request: Request,
    db: Session = Depends(get_db),
) -> IntegrationCicdCallbackResponse:
    config = db.query(IntegrationConfig).filter(IntegrationConfig.id == config_id).first()
    if not config:
        raise AppException(404, ErrorCode.INTEGRATION_CONFIG_NOT_FOUND, "Integration config not found")
    _ensure_cicd_config(config)
    if not config.credential_value:
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "Webhook secret is not configured")

    raw_body = await request.body()
    provided_signature = request.headers.get("X-Webhook-Signature")
    if not provided_signature:
        raise AppException(401, ErrorCode.INVALID_WEBHOOK_SIGNATURE, "Missing webhook signature")

    expected_signature = _calculate_hmac_sha256(config.credential_value, raw_body)
    normalized_signature = _normalize_signature(provided_signature)
    if not hmac.compare_digest(expected_signature, normalized_signature):
        raise AppException(401, ErrorCode.INVALID_WEBHOOK_SIGNATURE, "Invalid webhook signature")

    payload = _extract_payload(raw_body)
    trigger_event_id = payload.get("trigger_event_id")
    if trigger_event_id is None:
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "trigger_event_id is required")
    try:
        trigger_event_id = int(trigger_event_id)
    except (TypeError, ValueError):
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "trigger_event_id must be integer")

    trigger_event = (
        db.query(IntegrationEvent)
        .filter(
            IntegrationEvent.id == trigger_event_id,
            IntegrationEvent.integration_config_id == config.id,
            IntegrationEvent.event_type == "cicd.trigger",
            IntegrationEvent.direction == "outbound",
        )
        .first()
    )
    if not trigger_event:
        raise AppException(404, ErrorCode.INTEGRATION_EVENT_NOT_FOUND, "Trigger event not found")

    callback_idempotency_key = _build_idempotency_key(request, raw_body)
    existing_callback = (
        db.query(IntegrationEvent)
        .filter(
            IntegrationEvent.integration_config_id == config.id,
            IntegrationEvent.idempotency_key == callback_idempotency_key,
            IntegrationEvent.event_type == "cicd.callback",
            IntegrationEvent.direction == "inbound",
        )
        .first()
    )
    if existing_callback:
        create_audit_log(
            db=db,
            request=request,
            action="integration_cicd.callback",
            resource_type="integration_event",
            resource_id=str(existing_callback.id),
            details={"project_id": config.project_id, "idempotent_reused": True, "trigger_event_id": trigger_event.id},
        )
        return IntegrationCicdCallbackResponse(
            callback_event=_to_event_response(existing_callback),
            trigger_event=_to_event_response(trigger_event),
            idempotent_reused=True,
        )

    now = int(time.time())
    callback_event = IntegrationEvent(
        integration_config_id=config.id,
        project_id=config.project_id,
        event_type="cicd.callback",
        direction="inbound",
        status="processed",
        payload_json=json.dumps(payload, ensure_ascii=False),
        headers_json=json.dumps(_build_headers_snapshot(request), ensure_ascii=False),
        signature=normalized_signature,
        idempotency_key=callback_idempotency_key,
        attempt_count=1,
        max_attempts=1,
        next_retry_at=None,
        last_error=None,
        last_processed_at=now,
        created_at=now,
        updated_at=now,
    )
    db.add(callback_event)

    callback_status = str(payload.get("status", "unknown"))
    message = payload.get("message")
    external_run_id = payload.get("external_run_id")
    _map_cicd_status(trigger_event, callback_status, message, external_run_id, now)
    trigger_event.updated_at = now
    db.commit()
    db.refresh(callback_event)
    db.refresh(trigger_event)

    create_audit_log(
        db=db,
        request=request,
        action="integration_cicd.callback",
        resource_type="integration_event",
        resource_id=str(callback_event.id),
        details={
            "project_id": config.project_id,
            "idempotent_reused": False,
            "trigger_event_id": trigger_event.id,
            "trigger_event_status": trigger_event.status,
        },
    )
    return IntegrationCicdCallbackResponse(
        callback_event=_to_event_response(callback_event),
        trigger_event=_to_event_response(trigger_event),
        idempotent_reused=False,
    )


@router.post("/webhooks/{config_id}/events/{event_type}", response_model=IntegrationWebhookIngestResponse)
async def ingest_webhook_event(
    config_id: int,
    event_type: str,
    request: Request,
    db: Session = Depends(get_db),
) -> IntegrationWebhookIngestResponse:
    config = db.query(IntegrationConfig).filter(IntegrationConfig.id == config_id).first()
    if not config:
        raise AppException(404, ErrorCode.INTEGRATION_CONFIG_NOT_FOUND, "Integration config not found")
    if not bool(config.is_enabled):
        raise AppException(400, ErrorCode.INTEGRATION_CONFIG_DISABLED, "Integration config is disabled")
    if not config.credential_value:
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "Webhook secret is not configured")

    raw_body = await request.body()
    provided_signature = request.headers.get("X-Webhook-Signature")
    if not provided_signature:
        raise AppException(401, ErrorCode.INVALID_WEBHOOK_SIGNATURE, "Missing webhook signature")

    expected_signature = _calculate_hmac_sha256(config.credential_value, raw_body)
    normalized_signature = _normalize_signature(provided_signature)
    if not hmac.compare_digest(expected_signature, normalized_signature):
        raise AppException(401, ErrorCode.INVALID_WEBHOOK_SIGNATURE, "Invalid webhook signature")

    idempotency_key = _build_idempotency_key(request, raw_body)
    existed = (
        db.query(IntegrationEvent)
        .filter(
            IntegrationEvent.integration_config_id == config.id,
            IntegrationEvent.idempotency_key == idempotency_key,
        )
        .first()
    )
    if existed:
        create_audit_log(
            db=db,
            request=request,
            action="integration_event.ingest",
            resource_type="integration_event",
            resource_id=str(existed.id),
            details={"idempotent_reused": True, "project_id": config.project_id, "event_type": event_type},
        )
        return IntegrationWebhookIngestResponse(event=_to_event_response(existed), idempotent_reused=True)

    payload = _extract_payload(raw_body)
    now = int(time.time())
    event = IntegrationEvent(
        integration_config_id=config.id,
        project_id=config.project_id,
        event_type=event_type.strip(),
        direction="inbound",
        status="received",
        payload_json=json.dumps(payload, ensure_ascii=False),
        headers_json=json.dumps(_build_headers_snapshot(request), ensure_ascii=False),
        signature=normalized_signature,
        idempotency_key=idempotency_key,
        attempt_count=0,
        max_attempts=_resolve_max_attempts(config),
        created_at=now,
        updated_at=now,
    )
    db.add(event)
    db.flush()

    _process_event(event, payload, now)
    event.updated_at = now
    db.commit()
    db.refresh(event)

    create_audit_log(
        db=db,
        request=request,
        action="integration_event.ingest",
        resource_type="integration_event",
        resource_id=str(event.id),
        details={
            "idempotent_reused": False,
            "project_id": config.project_id,
            "event_type": event_type,
            "status": event.status,
        },
    )
    return IntegrationWebhookIngestResponse(event=_to_event_response(event), idempotent_reused=False)


@router.get("/{config_id}/cicd/runs", response_model=IntegrationEventListResponse)
def list_cicd_runs(
    config_id: int,
    request: Request,
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> IntegrationEventListResponse:
    config, _project = _ensure_integration_and_permission(db, config_id, user, manage=False)
    _ensure_cicd_config(config)
    if page < 1 or page_size < 1 or page_size > 100:
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "Invalid pagination params")

    query = db.query(IntegrationEvent).filter(
        IntegrationEvent.integration_config_id == config.id,
        IntegrationEvent.event_type == "cicd.trigger",
        IntegrationEvent.direction == "outbound",
    )
    if status:
        query = query.filter(IntegrationEvent.status == status.strip())
    total = query.count()
    items = (
        query.order_by(IntegrationEvent.created_at.desc(), IntegrationEvent.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    create_audit_log(
        db=db,
        request=request,
        action="integration_cicd.run.list",
        resource_type="integration_event",
        resource_id=str(config.id),
        user_id=user.id,
        details={"project_id": config.project_id, "count": len(items), "total": total},
    )
    return IntegrationEventListResponse(total=total, items=[_to_event_response(item) for item in items])


@router.get("/project/{project_id}/events", response_model=IntegrationEventListResponse)
def list_integration_events(
    project_id: int,
    request: Request,
    integration_config_id: int | None = None,
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> IntegrationEventListResponse:
    _ensure_project_and_permission(db, project_id, user, manage=False)
    if page < 1 or page_size < 1 or page_size > 100:
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "Invalid pagination params")

    query = db.query(IntegrationEvent).filter(IntegrationEvent.project_id == project_id)
    if integration_config_id is not None:
        query = query.filter(IntegrationEvent.integration_config_id == integration_config_id)
    if status:
        query = query.filter(IntegrationEvent.status == status.strip())

    total = query.count()
    items = (
        query.order_by(IntegrationEvent.created_at.desc(), IntegrationEvent.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    create_audit_log(
        db=db,
        request=request,
        action="integration_event.list",
        resource_type="integration_event",
        resource_id=str(project_id),
        user_id=user.id,
        details={"project_id": project_id, "count": len(items), "total": total},
    )
    return IntegrationEventListResponse(total=total, items=[_to_event_response(item) for item in items])


@router.get("/events/{event_id}", response_model=IntegrationEventResponse)
def get_integration_event(
    event_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> IntegrationEventResponse:
    event, _project = _ensure_event_and_permission(db, event_id, user, manage=False)
    create_audit_log(
        db=db,
        request=request,
        action="integration_event.get",
        resource_type="integration_event",
        resource_id=str(event.id),
        user_id=user.id,
        details={"project_id": event.project_id},
    )
    return _to_event_response(event)


@router.post("/events/{event_id}/replay", response_model=IntegrationEventResponse)
def replay_integration_event(
    event_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> IntegrationEventResponse:
    event, _project = _ensure_event_and_permission(db, event_id, user, manage=True)
    payload = _serialize_event_json(event.payload_json)
    now = int(time.time())
    _process_event(event, payload, now)
    event.updated_at = now
    db.commit()
    db.refresh(event)

    create_audit_log(
        db=db,
        request=request,
        action="integration_event.replay",
        resource_type="integration_event",
        resource_id=str(event.id),
        user_id=user.id,
        details={"project_id": event.project_id, "status": event.status, "attempt_count": event.attempt_count},
    )
    return _to_event_response(event)
