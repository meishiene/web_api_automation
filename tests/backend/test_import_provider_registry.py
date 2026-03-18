import pytest

from app.services.test_case_import_providers import (
    OpenApiImportProvider,
    ImportProviderRegistry,
)


def test_register_provider_conflict_raises_value_error():
    registry = ImportProviderRegistry()
    provider = OpenApiImportProvider()
    registry.register(provider)

    with pytest.raises(ValueError):
        registry.register(provider)


def test_get_unregistered_provider_returns_none():
    registry = ImportProviderRegistry()
    assert registry.get("missing-provider") is None

