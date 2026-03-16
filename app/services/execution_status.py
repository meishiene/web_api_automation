from typing import Any, Tuple


def map_result_status(result: dict[str, Any]) -> Tuple[str, str | None]:
    raw_status = str(result.get("status", "")).lower()
    if raw_status == "success":
        return "success", None
    if raw_status == "failed":
        return "failed", "ASSERTION_FAILED"
    if raw_status == "error":
        return "error", "EXECUTION_ERROR"
    return "error", "EXECUTION_UNKNOWN_STATUS"
