from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Protocol

from app.errors import AppException, ErrorCode
from app.schemas.api_test_case import TestCaseImportItem, TestCaseOpenApiImportRequest


class TestCaseImportProvider(Protocol):
    name: str

    def supports(self, payload: dict[str, Any]) -> bool:
        ...

    def build_candidates(self, payload: dict[str, Any]) -> list[TestCaseImportItem]:
        ...


@dataclass
class ResolvedProvider:
    provider: TestCaseImportProvider
    resolved_by_fallback: bool


class ImportProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, TestCaseImportProvider] = {}

    def register(self, provider: TestCaseImportProvider) -> None:
        key = provider.name.strip().lower()
        if not key:
            raise ValueError("Provider name must not be blank")
        if key in self._providers:
            raise ValueError(f"Provider already registered: {key}")
        self._providers[key] = provider

    def get(self, provider_name: str) -> TestCaseImportProvider | None:
        key = provider_name.strip().lower()
        if not key:
            return None
        return self._providers.get(key)

    def list_names(self) -> list[str]:
        return sorted(self._providers.keys())

    def resolve(self, provider_name: str | None, payload: dict[str, Any]) -> ResolvedProvider:
        if provider_name:
            provider = self.get(provider_name)
            if provider is None:
                raise AppException(400, ErrorCode.VALIDATION_ERROR, f"Provider not registered: {provider_name}")
            return ResolvedProvider(provider=provider, resolved_by_fallback=False)

        for provider in self._providers.values():
            if provider.supports(payload):
                return ResolvedProvider(provider=provider, resolved_by_fallback=True)

        raise AppException(
            400,
            ErrorCode.VALIDATION_ERROR,
            "Unable to resolve import provider from payload",
        )


class OpenApiImportProvider:
    name = "openapi"

    def supports(self, payload: dict[str, Any]) -> bool:
        if not isinstance(payload, dict):
            return False
        spec = payload.get("spec")
        if not isinstance(spec, dict):
            return False
        openapi_version = spec.get("openapi")
        return isinstance(openapi_version, str) and openapi_version.strip().startswith("3.")

    def build_candidates(self, payload: dict[str, Any]) -> list[TestCaseImportItem]:
        request = TestCaseOpenApiImportRequest(**payload)
        return _build_openapi_import_candidates(request)


class PostmanImportProvider:
    name = "postman"

    def supports(self, payload: dict[str, Any]) -> bool:
        if not isinstance(payload, dict):
            return False
        collection = payload.get("collection")
        if not isinstance(collection, dict):
            return False
        schema = collection.get("info", {}).get("schema")
        if isinstance(schema, str) and "postman" in schema.lower():
            return True
        return isinstance(collection.get("item"), list)

    def build_candidates(self, payload: dict[str, Any]) -> list[TestCaseImportItem]:
        collection = payload.get("collection")
        if not isinstance(collection, dict):
            raise AppException(400, ErrorCode.VALIDATION_ERROR, "Postman collection must be an object")

        items = collection.get("item")
        if not isinstance(items, list) or not items:
            raise AppException(400, ErrorCode.VALIDATION_ERROR, "Postman collection items must not be empty")

        case_group = _normalize_optional_text(payload.get("case_group")) or "postman-import"
        tags = _normalize_tags(payload.get("tags"))
        skip_empty = bool(payload.get("skip_empty_folder", True))
        candidates = _build_postman_candidates(items, case_group=case_group, tags=tags, skip_empty=skip_empty)
        if not candidates:
            raise AppException(400, ErrorCode.VALIDATION_ERROR, "No importable requests found in Postman collection")
        return candidates


def _choose_expected_status(operation: dict[str, Any]) -> int:
    responses = operation.get("responses")
    if not isinstance(responses, dict) or not responses:
        return 200

    numeric_codes: list[int] = []
    for code in responses.keys():
        if isinstance(code, int):
            numeric_codes.append(code)
            continue
        if isinstance(code, str) and code.isdigit():
            numeric_codes.append(int(code))

    if not numeric_codes:
        return 200

    success_codes = sorted([code for code in numeric_codes if 200 <= code < 300])
    if success_codes:
        return success_codes[0]
    return sorted(numeric_codes)[0]


def _resolve_import_base_url(payload: TestCaseOpenApiImportRequest) -> str:
    if payload.base_url:
        return payload.base_url.rstrip("/")

    servers = payload.spec.get("servers")
    if isinstance(servers, list):
        for item in servers:
            if not isinstance(item, dict):
                continue
            raw_url = item.get("url")
            if isinstance(raw_url, str) and raw_url.strip():
                return raw_url.strip().rstrip("/")

    return ""


def _normalize_optional_text(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        value = str(value)
    normalized = value.strip()
    return normalized or None


def _normalize_tags(value: Any) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, str):
        try:
            value = value.split(",")
        except Exception:
            value = [value]
    if not isinstance(value, list):
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "tags must be an array of strings")
    tags: list[str] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, str):
            continue
        tag = item.strip()
        if not tag or tag in seen:
            continue
        seen.add(tag)
        tags.append(tag)
    return tags


def _build_postman_candidates(
    items: list[dict[str, Any]],
    *,
    case_group: str,
    tags: list[str],
    skip_empty: bool,
) -> list[TestCaseImportItem]:
    candidates: list[TestCaseImportItem] = []

    def walk(nodes: list[dict[str, Any]], prefix: list[str]) -> None:
        for node in nodes:
            if not isinstance(node, dict):
                continue
            name = _normalize_optional_text(node.get("name")) or "unnamed-request"
            children = node.get("item")
            if isinstance(children, list):
                next_prefix = [*prefix, name]
                if not children and not skip_empty:
                    candidates.append(
                        TestCaseImportItem(
                            name=" / ".join(next_prefix),
                            method="GET",
                            url="/",
                            case_group=case_group,
                            tags=tags,
                            expected_status=200,
                        )
                    )
                walk(children, next_prefix)
                continue

            request = node.get("request")
            if not isinstance(request, dict):
                continue

            method = _normalize_optional_text(request.get("method")) or "GET"
            url = _extract_postman_url(request.get("url"))
            if url is None:
                continue

            headers = _extract_postman_headers(request.get("header"))
            body = _extract_postman_body(request.get("body"))
            candidate_name = " / ".join([*prefix, name]) if prefix else name

            candidates.append(
                TestCaseImportItem(
                    name=candidate_name[:100],
                    method=method.upper(),
                    url=url,
                    case_group=case_group,
                    tags=tags,
                    headers=headers,
                    body=body,
                    expected_status=200,
                )
            )

    walk(items, [])
    return candidates


def _extract_postman_url(raw_url: Any) -> str | None:
    if isinstance(raw_url, str):
        return raw_url.strip() or None
    if not isinstance(raw_url, dict):
        return None
    raw_value = raw_url.get("raw")
    if isinstance(raw_value, str) and raw_value.strip():
        return raw_value.strip()

    host = raw_url.get("host") or []
    path = raw_url.get("path") or []
    protocol = _normalize_optional_text(raw_url.get("protocol")) or "https"
    host_text = ".".join([part for part in host if isinstance(part, str) and part.strip()])
    path_text = "/".join([part for part in path if isinstance(part, str) and part.strip()])
    if not host_text:
        return None
    return f"{protocol}://{host_text}/{path_text}".rstrip("/")


def _extract_postman_headers(raw_headers: Any) -> str | None:
    if not isinstance(raw_headers, list):
        return None
    headers: dict[str, str] = {}
    for item in raw_headers:
        if not isinstance(item, dict):
            continue
        if item.get("disabled") is True:
            continue
        key = _normalize_optional_text(item.get("key"))
        value = _normalize_optional_text(item.get("value"))
        if key is None or value is None:
            continue
        headers[key] = value
    return json.dumps(headers, ensure_ascii=False) if headers else None


def _extract_postman_body(raw_body: Any) -> str | None:
    if not isinstance(raw_body, dict):
        return None
    mode = _normalize_optional_text(raw_body.get("mode"))
    if mode == "raw":
        value = _normalize_optional_text(raw_body.get("raw"))
        return value
    if mode == "urlencoded" and isinstance(raw_body.get("urlencoded"), list):
        payload = {
            item.get("key"): item.get("value")
            for item in raw_body["urlencoded"]
            if isinstance(item, dict) and item.get("disabled") is not True and _normalize_optional_text(item.get("key"))
        }
        return json.dumps(payload, ensure_ascii=False) if payload else None
    return None


def _build_openapi_import_candidates(payload: TestCaseOpenApiImportRequest) -> list[TestCaseImportItem]:
    spec = payload.spec
    paths = spec.get("paths")
    if not isinstance(paths, dict) or not paths:
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "OpenAPI spec paths must not be empty")

    openapi_version = spec.get("openapi")
    if not isinstance(openapi_version, str) or not openapi_version.strip().startswith("3."):
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "Only OpenAPI 3.x is supported")

    base_url = _resolve_import_base_url(payload)
    allowed_methods = {"get", "post", "put", "patch", "delete"}
    candidates: list[TestCaseImportItem] = []

    for raw_path, path_item in paths.items():
        if not isinstance(raw_path, str) or not raw_path.strip():
            continue
        if not isinstance(path_item, dict):
            continue

        normalized_path = raw_path.strip()
        for method, operation in path_item.items():
            if not isinstance(method, str):
                continue
            lowered_method = method.lower().strip()
            if lowered_method not in allowed_methods:
                continue
            if not isinstance(operation, dict):
                operation = {}

            method_upper = lowered_method.upper()
            operation_id = operation.get("operationId")
            if isinstance(operation_id, str) and operation_id.strip():
                name = operation_id.strip()
            else:
                name = f"{method_upper} {normalized_path}"
            if len(name) > 100:
                name = name[:100]

            if base_url:
                url = f"{base_url}{normalized_path}"
            else:
                url = normalized_path

            expected_status = _choose_expected_status(operation)
            candidates.append(
                TestCaseImportItem(
                    name=name,
                    method=method_upper,
                    url=url,
                    case_group=payload.case_group,
                    tags=payload.tags,
                    expected_status=expected_status,
                )
            )

    if not candidates:
        raise AppException(400, ErrorCode.VALIDATION_ERROR, "No importable API operations found in OpenAPI spec")

    return candidates

