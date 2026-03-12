import json
import logging

from app.logging_config import JsonFormatter


def test_json_formatter_includes_base_fields():
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="app.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="hello",
        args=(),
        exc_info=None,
    )

    payload = json.loads(formatter.format(record))

    assert payload["level"] == "INFO"
    assert payload["logger"] == "app.test"
    assert payload["message"] == "hello"
    assert "timestamp" in payload


def test_json_formatter_includes_request_and_audit_fields():
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="app.request",
        level=logging.INFO,
        pathname=__file__,
        lineno=20,
        msg="request_completed",
        args=(),
        exc_info=None,
    )
    record.request_id = "rid-1"
    record.event = "http_request"
    record.method = "GET"
    record.path = "/ping"
    record.status_code = 200
    record.duration_ms = 12
    record.client_ip = "127.0.0.1"
    record.user_id = 1
    record.action = "project.create"
    record.resource_type = "project"
    record.resource_id = "3"
    record.result = "success"

    payload = json.loads(formatter.format(record))

    assert payload["request_id"] == "rid-1"
    assert payload["event"] == "http_request"
    assert payload["method"] == "GET"
    assert payload["path"] == "/ping"
    assert payload["status_code"] == 200
    assert payload["duration_ms"] == 12
    assert payload["client_ip"] == "127.0.0.1"
    assert payload["user_id"] == 1
    assert payload["action"] == "project.create"
    assert payload["resource_type"] == "project"
    assert payload["resource_id"] == "3"
    assert payload["result"] == "success"
