import json
import re
import time
from typing import Any

import httpx


_TEMPLATE_PATTERN = re.compile(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}")


def _stringify_template_value(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return "" if value is None else str(value)


def _apply_runtime_variables(raw: str | None, runtime_variables: dict[str, Any]) -> str | None:
    if raw is None:
        return None

    def _replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in runtime_variables:
            raise ValueError(f"Missing runtime variable: {key}")
        return _stringify_template_value(runtime_variables[key])

    return _TEMPLATE_PATTERN.sub(_replace, raw)


def _parse_json_path(path: str) -> list[Any]:
    if not path:
        raise ValueError("JSONPath is empty")
    normalized = path.strip()
    if normalized == "$":
        return []
    if not normalized.startswith("$"):
        raise ValueError("JSONPath must start with '$'")

    expr = normalized[1:]
    if expr.startswith("."):
        expr = expr[1:]

    tokens: list[Any] = []
    buf = ""
    i = 0
    while i < len(expr):
        ch = expr[i]
        if ch == ".":
            if buf:
                tokens.append(buf)
                buf = ""
            i += 1
            continue
        if ch == "[":
            if buf:
                tokens.append(buf)
                buf = ""
            end = expr.find("]", i)
            if end == -1:
                raise ValueError("JSONPath missing closing bracket")
            key = expr[i + 1 : end].strip()
            if (key.startswith("\"") and key.endswith("\"")) or (key.startswith("'") and key.endswith("'")):
                key = key[1:-1]
                tokens.append(key)
            elif key.isdigit():
                tokens.append(int(key))
            else:
                raise ValueError("JSONPath bracket token must be quoted key or index")
            i = end + 1
            continue

        buf += ch
        i += 1

    if buf:
        tokens.append(buf)
    return tokens


def _json_path_get(data: Any, path: str) -> Any:
    value = data
    for token in _parse_json_path(path):
        if isinstance(token, int):
            if not isinstance(value, list) or token >= len(value):
                raise KeyError(path)
            value = value[token]
            continue
        if not isinstance(value, dict) or token not in value:
            raise KeyError(path)
        value = value[token]
    return value


def _ensure_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _evaluate_assertions(
    response: httpx.Response,
    expected_status: int,
    expected_body: str | None,
    assertion_rules: str | None,
) -> tuple[bool, str | None]:
    if response.status_code != expected_status:
        return False, f"Expected status {expected_status}, got {response.status_code}"

    if assertion_rules:
        try:
            rules = json.loads(assertion_rules)
        except json.JSONDecodeError as exc:
            return False, f"Invalid assertion_rules JSON: {exc}"

        contains_values = _ensure_list(rules.get("contains") if isinstance(rules, dict) else None)
        for text in contains_values:
            if str(text) not in response.text:
                return False, f"Response body does not contain '{text}'"

        regex_values = _ensure_list(rules.get("regex") if isinstance(rules, dict) else None)
        for pattern in regex_values:
            if re.search(str(pattern), response.text) is None:
                return False, f"Response body does not match regex '{pattern}'"

        jsonpath_rules = _ensure_list(rules.get("jsonpath") if isinstance(rules, dict) else None)
        if jsonpath_rules:
            try:
                actual_json = response.json()
            except Exception as exc:
                return False, f"Response is not valid JSON for jsonpath assertion: {exc}"

            for item in jsonpath_rules:
                if not isinstance(item, dict):
                    return False, "jsonpath assertion must be an object"
                path = item.get("path")
                expected = item.get("equals")
                if not path:
                    return False, "jsonpath assertion requires 'path'"
                try:
                    actual = _json_path_get(actual_json, path)
                except KeyError:
                    return False, f"JSONPath not found: {path}"
                except Exception as exc:
                    return False, f"Invalid JSONPath '{path}': {exc}"
                if actual != expected:
                    return False, f"JSONPath {path} expected {expected}, got {actual}"

        return True, None

    if expected_body is not None:
        try:
            expected_json = json.loads(expected_body)
            actual_json = response.json()
            if actual_json != expected_json:
                return False, "Response JSON does not equal expected_body"
        except (json.JSONDecodeError, Exception):
            if response.text != expected_body:
                return False, "Response text does not equal expected_body"

    return True, None


def _extract_variables(actual_body: str | None, extraction_rules: str | None) -> dict[str, Any]:
    if not extraction_rules:
        return {}
    if actual_body is None:
        return {}

    try:
        rules = json.loads(extraction_rules)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid extraction_rules JSON: {exc}") from exc

    if not isinstance(rules, list):
        raise ValueError("extraction_rules must be a JSON array")

    try:
        payload = json.loads(actual_body)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Response body is not JSON for extraction: {exc}") from exc

    extracted: dict[str, Any] = {}
    for rule in rules:
        if not isinstance(rule, dict):
            raise ValueError("Each extraction rule must be an object")
        name = rule.get("name")
        path = rule.get("path")
        if not name or not path:
            raise ValueError("Extraction rule requires 'name' and 'path'")
        extracted[name] = _json_path_get(payload, path)

    return extracted


async def execute_test(test_case, runtime_variables: dict[str, Any] | None = None):
    """
    Execute a test case.

    Returns: {
        'status': 'success'|'failed'|'error',
        'actual_status': int,
        'actual_body': str,
        'error_message': str,
        'duration_ms': int,
        'extracted_variables': dict
    }
    """
    runtime_variables = runtime_variables or {}
    start_time = time.time()

    try:
        method = test_case.method.upper()
        url = _apply_runtime_variables(test_case.url, runtime_variables)
        raw_headers = _apply_runtime_variables(test_case.headers, runtime_variables)
        raw_body = _apply_runtime_variables(test_case.body, runtime_variables)
        raw_expected_body = _apply_runtime_variables(test_case.expected_body, runtime_variables)
        raw_assertion_rules = _apply_runtime_variables(getattr(test_case, "assertion_rules", None), runtime_variables)
        raw_extraction_rules = _apply_runtime_variables(getattr(test_case, "extraction_rules", None), runtime_variables)

        headers = {}
        if raw_headers:
            headers = json.loads(raw_headers)
            if not isinstance(headers, dict):
                raise ValueError("headers must be a JSON object")

        request_kwargs = {
            "method": method,
            "url": url,
            "headers": headers,
            "timeout": 30.0,
        }

        if raw_body and method in ["POST", "PUT", "PATCH"]:
            try:
                request_kwargs["json"] = json.loads(raw_body)
            except json.JSONDecodeError:
                request_kwargs["content"] = raw_body

        async with httpx.AsyncClient() as client:
            response = await client.request(**request_kwargs)

        ok, reason = _evaluate_assertions(
            response=response,
            expected_status=test_case.expected_status,
            expected_body=raw_expected_body,
            assertion_rules=raw_assertion_rules,
        )

        extracted_variables: dict[str, Any] = {}
        if ok:
            extracted_variables = _extract_variables(response.text, raw_extraction_rules)

        return {
            "status": "success" if ok else "failed",
            "actual_status": response.status_code,
            "actual_body": response.text,
            "error_message": reason,
            "duration_ms": int((time.time() - start_time) * 1000),
            "extracted_variables": extracted_variables,
        }

    except Exception as exc:
        return {
            "status": "error",
            "actual_status": None,
            "actual_body": None,
            "error_message": str(exc),
            "duration_ms": int((time.time() - start_time) * 1000),
            "extracted_variables": {},
        }
