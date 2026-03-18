from __future__ import annotations

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

