import asyncio

from app.services.test_executor import execute_test


class _DummyResponse:
    def __init__(self, status_code, text, json_data=None):
        self.status_code = status_code
        self.text = text
        self._json_data = json_data

    def json(self):
        if self._json_data is None:
            raise ValueError("no json")
        return self._json_data


class _DummyClient:
    def __init__(self, response, capture):
        self._response = response
        self._capture = capture

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def request(self, **kwargs):
        self._capture.append(kwargs)
        return self._response


class _DummyCase:
    def __init__(self, **kwargs):
        self.method = kwargs.get("method", "GET")
        self.url = kwargs.get("url", "https://example.com")
        self.headers = kwargs.get("headers")
        self.body = kwargs.get("body")
        self.expected_status = kwargs.get("expected_status", 200)
        self.expected_body = kwargs.get("expected_body")
        self.assertion_rules = kwargs.get("assertion_rules")
        self.extraction_rules = kwargs.get("extraction_rules")


def test_execute_test_supports_contains_regex_and_jsonpath(monkeypatch):
    capture = []
    response = _DummyResponse(200, '{"msg":"hello world","user":{"id":7}}', json_data={"msg": "hello world", "user": {"id": 7}})

    monkeypatch.setattr(
        "app.services.test_executor.httpx.AsyncClient",
        lambda: _DummyClient(response, capture),
    )

    case = _DummyCase(
        method="GET",
        url="https://example.com",
        expected_status=200,
        assertion_rules='{"contains":["hello"],"regex":["world"],"jsonpath":[{"path":"$.user.id","equals":7}]}'
    )

    result = asyncio.run(execute_test(case))
    assert result["status"] == "success"


def test_execute_test_replaces_runtime_variables_and_extracts_values(monkeypatch):
    capture = []
    response = _DummyResponse(200, '{"token":"abc-123"}', json_data={"token": "abc-123"})

    monkeypatch.setattr(
        "app.services.test_executor.httpx.AsyncClient",
        lambda: _DummyClient(response, capture),
    )

    case = _DummyCase(
        method="POST",
        url="{{base_url}}/login",
        headers='{"X-User":"{{username}}"}',
        body='{"username":"{{username}}"}',
        expected_status=200,
        extraction_rules='[{"name":"auth_token","path":"$.token"}]',
    )

    result = asyncio.run(execute_test(case, runtime_variables={"base_url": "https://api.example.com", "username": "owner"}))
    assert result["status"] == "success"
    assert result["extracted_variables"]["auth_token"] == "abc-123"

    sent = capture[0]
    assert sent["url"] == "https://api.example.com/login"
    assert sent["headers"]["X-User"] == "owner"
    assert sent["json"]["username"] == "owner"


def test_execute_test_supports_schema_assertion_success(monkeypatch):
    capture = []
    response = _DummyResponse(
        200,
        '{"user":{"id":7,"name":"Tom"}}',
        json_data={"user": {"id": 7, "name": "Tom"}},
    )

    monkeypatch.setattr(
        "app.services.test_executor.httpx.AsyncClient",
        lambda: _DummyClient(response, capture),
    )

    case = _DummyCase(
        method="GET",
        url="https://example.com/user",
        expected_status=200,
        assertion_rules=(
            '{"schema":{"type":"object","required":["user"],'
            '"properties":{"user":{"type":"object","required":["id","name"],'
            '"properties":{"id":{"type":"integer"},"name":{"type":"string"}}}}}}'
        ),
    )

    result = asyncio.run(execute_test(case))
    assert result["status"] == "success"


def test_execute_test_schema_assertion_failed_when_payload_mismatch(monkeypatch):
    capture = []
    response = _DummyResponse(
        200,
        '{"user":{"id":"oops"}}',
        json_data={"user": {"id": "oops"}},
    )

    monkeypatch.setattr(
        "app.services.test_executor.httpx.AsyncClient",
        lambda: _DummyClient(response, capture),
    )

    case = _DummyCase(
        method="GET",
        url="https://example.com/user",
        expected_status=200,
        assertion_rules='{"schema":{"type":"object","properties":{"user":{"type":"object","properties":{"id":{"type":"integer"}}}}}}',
    )

    result = asyncio.run(execute_test(case))
    assert result["status"] == "failed"
    assert "Schema assertion failed" in (result["error_message"] or "")


def test_execute_test_schema_assertion_rejects_invalid_schema_rule(monkeypatch):
    capture = []
    response = _DummyResponse(
        200,
        '{"user":{"id":7}}',
        json_data={"user": {"id": 7}},
    )

    monkeypatch.setattr(
        "app.services.test_executor.httpx.AsyncClient",
        lambda: _DummyClient(response, capture),
    )

    case = _DummyCase(
        method="GET",
        url="https://example.com/user",
        expected_status=200,
        assertion_rules='{"schema":{"type":"object","required":"user"}}',
    )

    result = asyncio.run(execute_test(case))
    assert result["status"] == "failed"
    assert "Invalid schema assertion rule" in (result["error_message"] or "")
