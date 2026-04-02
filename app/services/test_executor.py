import json
import re
import time
from typing import Any

import httpx


_TEMPLATE_PATTERN = re.compile(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}")
_ALLOWED_SCHEMA_TYPES = {"object", "array", "string", "number", "integer", "boolean", "null"}


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


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _detect_placeholder_marker(value: str | None) -> str | None:
    normalized = _normalize_optional_text(value)
    if normalized is None:
        return None
    if normalized in {"{}", "[]"}:
        return normalized

    candidate = normalized
    for _ in range(3):
        try:
            loaded = json.loads(candidate)
        except json.JSONDecodeError:
            return None
        if not isinstance(loaded, str):
            return None
        candidate = loaded.strip()
        if not candidate:
            return ""
        if candidate in {"{}", "[]"}:
            return candidate
    return None


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
            if (key.startswith('"') and key.endswith('"')) or (key.startswith("'") and key.endswith("'")):
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


def _schema_path(base: str, token: Any) -> str:
    if isinstance(token, int):
        return f"{base}[{token}]"
    if token.isidentifier():
        return f"{base}.{token}"
    return f"{base}['{token}']"


def _json_type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def _matches_schema_type(value: Any, expected_type: str) -> bool:
    if expected_type == "object":
        return isinstance(value, dict)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "number":
        return (isinstance(value, (int, float)) and not isinstance(value, bool))
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "boolean":
        return isinstance(value, bool)
    if expected_type == "null":
        return value is None
    return False


def _validate_schema_rule(schema: Any, path: str = "$") -> None:
    if not isinstance(schema, dict):
        raise ValueError(f"Invalid schema assertion rule: schema at {path} must be an object")

    schema_type = schema.get("type")
    if schema_type is not None:
        if not isinstance(schema_type, str) or schema_type not in _ALLOWED_SCHEMA_TYPES:
            allowed = ", ".join(sorted(_ALLOWED_SCHEMA_TYPES))
            raise ValueError(f"Invalid schema assertion rule: 'type' at {path} must be one of [{allowed}]")

    required = schema.get("required")
    if required is not None:
        if not isinstance(required, list) or any(not isinstance(name, str) for name in required):
            raise ValueError(f"Invalid schema assertion rule: 'required' at {path} must be an array of strings")

    properties = schema.get("properties")
    if properties is not None:
        if not isinstance(properties, dict):
            raise ValueError(f"Invalid schema assertion rule: 'properties' at {path} must be an object")
        for key, sub_schema in properties.items():
            if not isinstance(key, str):
                raise ValueError(f"Invalid schema assertion rule: property key at {path} must be a string")
            _validate_schema_rule(sub_schema, f"{path}.properties.{key}")

    items = schema.get("items")
    if items is not None:
        _validate_schema_rule(items, f"{path}.items")

    enum_values = schema.get("enum")
    if enum_values is not None and not isinstance(enum_values, list):
        raise ValueError(f"Invalid schema assertion rule: 'enum' at {path} must be an array")

    additional_properties = schema.get("additionalProperties")
    if additional_properties is not None and not isinstance(additional_properties, bool):
        raise ValueError(f"Invalid schema assertion rule: 'additionalProperties' at {path} must be boolean")

    for key in ("minimum", "maximum"):
        if key in schema and not isinstance(schema[key], (int, float)):
            raise ValueError(f"Invalid schema assertion rule: '{key}' at {path} must be number")

    for key in ("minLength", "maxLength", "minItems", "maxItems"):
        if key in schema and (not isinstance(schema[key], int) or schema[key] < 0):
            raise ValueError(f"Invalid schema assertion rule: '{key}' at {path} must be non-negative integer")


def _validate_schema_value(value: Any, schema: dict[str, Any], path: str = "$") -> None:
    schema_type = schema.get("type")
    if schema_type and not _matches_schema_type(value, schema_type):
        actual = _json_type_name(value)
        raise ValueError(f"{path} expected type {schema_type}, got {actual}")

    if "const" in schema and value != schema["const"]:
        raise ValueError(f"{path} expected const {schema['const']}, got {value}")

    if "enum" in schema and value not in schema["enum"]:
        raise ValueError(f"{path} value {value} not in enum {schema['enum']}")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        minimum = schema.get("minimum")
        maximum = schema.get("maximum")
        if minimum is not None and value < minimum:
            raise ValueError(f"{path} expected >= {minimum}, got {value}")
        if maximum is not None and value > maximum:
            raise ValueError(f"{path} expected <= {maximum}, got {value}")

    if isinstance(value, str):
        min_length = schema.get("minLength")
        max_length = schema.get("maxLength")
        if min_length is not None and len(value) < min_length:
            raise ValueError(f"{path} length expected >= {min_length}, got {len(value)}")
        if max_length is not None and len(value) > max_length:
            raise ValueError(f"{path} length expected <= {max_length}, got {len(value)}")

    if isinstance(value, list):
        min_items = schema.get("minItems")
        max_items = schema.get("maxItems")
        if min_items is not None and len(value) < min_items:
            raise ValueError(f"{path} item count expected >= {min_items}, got {len(value)}")
        if max_items is not None and len(value) > max_items:
            raise ValueError(f"{path} item count expected <= {max_items}, got {len(value)}")

        item_schema = schema.get("items")
        if item_schema is not None:
            for idx, item in enumerate(value):
                _validate_schema_value(item, item_schema, _schema_path(path, idx))

    if isinstance(value, dict):
        required = schema.get("required") or []
        for key in required:
            if key not in value:
                raise ValueError(f"{path} missing required field '{key}'")

        properties = schema.get("properties") or {}
        for key, sub_schema in properties.items():
            if key in value:
                _validate_schema_value(value[key], sub_schema, _schema_path(path, key))

        additional_properties = schema.get("additionalProperties")
        if additional_properties is False:
            extra_keys = [key for key in value.keys() if key not in properties]
            if extra_keys:
                raise ValueError(f"{path} has unexpected fields {extra_keys}")


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

        schema_rule = rules.get("schema") if isinstance(rules, dict) else None
        if schema_rule is not None:
            try:
                actual_json = response.json()
            except Exception as exc:
                return False, f"Response is not valid JSON for schema assertion: {exc}"
            try:
                _validate_schema_rule(schema_rule)
                _validate_schema_value(actual_json, schema_rule)
            except ValueError as exc:
                message = str(exc)
                if message.startswith("Invalid schema assertion rule:"):
                    return False, message
                return False, f"Schema assertion failed: {message}"

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
        raw_headers = _normalize_optional_text(_apply_runtime_variables(test_case.headers, runtime_variables))
        raw_body = _normalize_optional_text(_apply_runtime_variables(test_case.body, runtime_variables))
        raw_assertion_rules = _normalize_optional_text(
            _apply_runtime_variables(getattr(test_case, "assertion_rules", None), runtime_variables)
        )
        raw_extraction_rules = _normalize_optional_text(
            _apply_runtime_variables(getattr(test_case, "extraction_rules", None), runtime_variables)
        )
        raw_expected_body = _normalize_optional_text(_apply_runtime_variables(test_case.expected_body, runtime_variables))

        headers_placeholder = _detect_placeholder_marker(raw_headers)
        body_placeholder = _detect_placeholder_marker(raw_body)
        expected_body_placeholder = _detect_placeholder_marker(raw_expected_body)
        assertion_rules_placeholder = _detect_placeholder_marker(raw_assertion_rules)
        extraction_rules_placeholder = _detect_placeholder_marker(raw_extraction_rules)

        if headers_placeholder:
            raw_headers = None
        if assertion_rules_placeholder:
            raw_assertion_rules = None
        if extraction_rules_placeholder:
            raw_extraction_rules = None
        if method not in ["POST", "PUT", "PATCH"] and body_placeholder:
            raw_body = None
        if (
            method == "GET"
            and expected_body_placeholder
            and raw_assertion_rules is None
            and (raw_headers is None or headers_placeholder is not None)
            and (raw_body is None or body_placeholder is not None)
        ):
            raw_expected_body = None

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
