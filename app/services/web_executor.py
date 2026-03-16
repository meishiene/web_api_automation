import asyncio
import time
from pathlib import Path
from typing import Any, Dict, List

from app.models.web_step import WebStep
from app.models.web_test_case import WebTestCase


def _ensure_artifact_dir(artifact_dir: str) -> Path:
    path = Path(artifact_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _normalize_url(base_url: str | None, url: str) -> str:
    if url.startswith("http://") or url.startswith("https://"):
        return url
    base = (base_url or "").rstrip("/")
    suffix = url if url.startswith("/") else f"/{url}"
    return f"{base}{suffix}" if base else suffix


def _execute_with_playwright(test_case: WebTestCase, artifact_dir: str) -> Dict[str, Any]:
    from playwright.sync_api import Error as PlaywrightError
    from playwright.sync_api import sync_playwright

    artifact_path = _ensure_artifact_dir(artifact_dir)
    step_logs: List[Dict[str, Any]] = []
    artifacts: List[str] = []
    start_ms = int(time.time() * 1000)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            try:
                ordered_steps = sorted(test_case.steps, key=lambda item: item.order_index)
                for step in ordered_steps:
                    params = step.params_json or "{}"
                    try:
                        import json

                        parsed = json.loads(params)
                    except Exception:
                        parsed = {}

                    action = step.action
                    if action == "open":
                        url = _normalize_url(test_case.base_url, str(parsed.get("url", "")))
                        page.goto(url, wait_until="domcontentloaded")
                    elif action == "click":
                        selector = str(parsed.get("selector", ""))
                        page.click(selector)
                    elif action == "input":
                        selector = str(parsed.get("selector", ""))
                        value = str(parsed.get("value", ""))
                        page.fill(selector, value)
                    elif action == "wait":
                        wait_ms = int(parsed.get("timeout_ms", 500))
                        page.wait_for_timeout(wait_ms)
                    elif action == "assert":
                        selector = str(parsed.get("selector", ""))
                        expected = str(parsed.get("contains", ""))
                        content = page.text_content(selector) or ""
                        if expected not in content:
                            raise AssertionError(f"assert contains failed: '{expected}' not in element text")
                    elif action == "screenshot":
                        filename = str(parsed.get("filename", f"step_{step.order_index}.png"))
                        shot_path = artifact_path / filename
                        page.screenshot(path=str(shot_path))
                        artifacts.append(str(shot_path))
                    else:
                        raise ValueError(f"unsupported action: {action}")

                    step_logs.append(
                        {
                            "step": step.order_index,
                            "action": action,
                            "status": "success",
                        }
                    )

                duration = int(time.time() * 1000) - start_ms
                return {
                    "status": "success",
                    "duration_ms": duration,
                    "error_message": None,
                    "step_logs": step_logs,
                    "artifacts": artifacts,
                }
            except Exception as exc:
                failure_path = artifact_path / "failure.png"
                try:
                    page.screenshot(path=str(failure_path))
                    artifacts.append(str(failure_path))
                except Exception:
                    pass
                duration = int(time.time() * 1000) - start_ms
                step_logs.append({"status": "error", "error": str(exc)})
                return {
                    "status": "error",
                    "duration_ms": duration,
                    "error_message": str(exc),
                    "step_logs": step_logs,
                    "artifacts": artifacts,
                }
            finally:
                browser.close()
    except PlaywrightError as exc:
        duration = int(time.time() * 1000) - start_ms
        return {
            "status": "error",
            "duration_ms": duration,
            "error_message": str(exc),
            "step_logs": [{"status": "error", "error": str(exc)}],
            "artifacts": [],
        }


async def execute_web_test_case(test_case: WebTestCase, artifact_dir: str) -> Dict[str, Any]:
    return await asyncio.to_thread(_execute_with_playwright, test_case, artifact_dir)

