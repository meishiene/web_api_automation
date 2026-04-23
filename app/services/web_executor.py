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


def _normalize_locator_strategy(params: Dict[str, Any]) -> str:
    raw = str(params.get("locator_type") or params.get("strategy") or "css").strip().lower()
    if raw in {"css", "xpath", "text", "testid", "role"}:
        return raw
    raise ValueError(f"unsupported locator strategy: {raw}")


def _resolve_locator(page, params: Dict[str, Any]):
    locator_value = str(params.get("locator") or params.get("selector") or "").strip()
    if not locator_value:
        raise ValueError("locator is required")

    strategy = _normalize_locator_strategy(params)
    if strategy == "css":
        return page.locator(locator_value)
    if strategy == "xpath":
        expression = locator_value if locator_value.startswith("xpath=") else f"xpath={locator_value}"
        return page.locator(expression)
    if strategy == "text":
        return page.get_by_text(locator_value)
    if strategy == "testid":
        return page.get_by_test_id(locator_value)

    role, _, name = locator_value.partition("|")
    role = role.strip()
    name = name.strip()
    if not role:
        raise ValueError("role locator must provide a role name")
    if name:
        return page.get_by_role(role, name=name)
    return page.get_by_role(role)


def _execute_with_playwright(test_case: WebTestCase, artifact_dir: str) -> Dict[str, Any]:
    from playwright.sync_api import Error as PlaywrightError
    from playwright.sync_api import sync_playwright

    artifact_path = _ensure_artifact_dir(artifact_dir)
    step_logs: List[Dict[str, Any]] = []
    artifacts: List[str] = []
    start_ms = int(time.time() * 1000)
    browser_name = getattr(test_case, "browser_name", "chromium") or "chromium"
    timeout_ms = int(getattr(test_case, "timeout_ms", 30000) or 30000)
    viewport_width = getattr(test_case, "viewport_width", None)
    viewport_height = getattr(test_case, "viewport_height", None)
    headless = bool(getattr(test_case, "headless", 1))
    capture_on_failure = bool(getattr(test_case, "capture_on_failure", 1))
    record_video = bool(getattr(test_case, "record_video", 0))

    try:
        with sync_playwright() as p:
            browser_launcher = getattr(p, browser_name, None) or p.chromium
            browser = browser_launcher.launch(headless=headless)
            context_kwargs: Dict[str, Any] = {}
            if viewport_width and viewport_height:
                context_kwargs["viewport"] = {"width": int(viewport_width), "height": int(viewport_height)}
            video_dir = artifact_path / "video" if record_video else None
            if video_dir is not None:
                video_dir.mkdir(parents=True, exist_ok=True)
                context_kwargs["record_video_dir"] = str(video_dir)
            context = browser.new_context(**context_kwargs)
            page = context.new_page()
            page.set_default_timeout(timeout_ms)
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
                        locator = _resolve_locator(page, parsed)
                        locator.click()
                    elif action == "input":
                        value = str(parsed.get("value", ""))
                        locator = _resolve_locator(page, parsed)
                        locator.fill(value)
                    elif action == "wait":
                        wait_ms = int(parsed.get("timeout_ms", 500))
                        locator_value = str(parsed.get("locator") or parsed.get("selector") or "").strip()
                        if locator_value:
                            locator = _resolve_locator(page, parsed)
                            locator.wait_for(state="visible", timeout=wait_ms)
                        else:
                            page.wait_for_timeout(wait_ms)
                    elif action == "assert":
                        expected = str(parsed.get("contains", ""))
                        locator = _resolve_locator(page, parsed)
                        content = locator.text_content() or ""
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
                if capture_on_failure:
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
                try:
                    context.close()
                finally:
                    if video_dir is not None and video_dir.exists():
                        artifacts.extend(str(path) for path in video_dir.glob("*.webm"))
                        artifacts.extend(str(path) for path in video_dir.glob("*.mp4"))
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
