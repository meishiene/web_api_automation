import json
import logging
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        for attr in (
            "request_id",
            "event",
            "code",
            "method",
            "path",
            "status_code",
            "duration_ms",
            "client_ip",
            "user_id",
            "action",
            "resource_type",
            "resource_id",
            "result",
        ):
            value = getattr(record, attr, None)
            if value is not None:
                payload[attr] = value

        return json.dumps(payload, ensure_ascii=False)


def setup_logging() -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root_logger.handlers = [handler]
    root_logger.propagate = False
