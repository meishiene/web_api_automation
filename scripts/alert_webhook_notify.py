import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


def build_payload(
    *,
    title: str,
    source: str,
    status: str,
    summary: str,
    details: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "title": title,
        "source": source,
        "status": status,
        "summary": summary,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if details:
        payload["details"] = details
    return payload


def post_webhook(url: str, payload: Dict[str, Any], timeout_seconds: int) -> Dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url=url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        response_body = response.read().decode("utf-8", errors="ignore")
        return {
            "status_code": response.getcode(),
            "response_body": response_body,
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send alert payload to webhook")
    parser.add_argument("--webhook-url", required=True)
    parser.add_argument("--title", default="Audit Governance Alert")
    parser.add_argument("--source", default="web_api_automation")
    parser.add_argument("--status", default="alert")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--payload-file", default="")
    parser.add_argument("--timeout-seconds", type=int, default=10)
    return parser.parse_args()


def load_payload_file(path: str) -> Dict[str, Any] | None:
    if not path:
        return None
    payload_path = Path(path)
    if not payload_path.exists():
        return {"error": f"payload file not found: {path}"}
    with payload_path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def main() -> int:
    args = parse_args()
    details = load_payload_file(args.payload_file)
    payload = build_payload(
        title=args.title,
        source=args.source,
        status=args.status,
        summary=args.summary,
        details=details,
    )
    try:
        result = post_webhook(args.webhook_url, payload, args.timeout_seconds)
        print(json.dumps({"ok": True, **result}, ensure_ascii=False))
        return 0
    except urllib.error.URLError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
