#!/usr/bin/env python
"""
Check GitHub Actions workflow run status for CI (Stage-4 Gates).

Requires:
  - env GITHUB_TOKEN (PAT with repo read access is enough)
Optional:
  - env GITHUB_OWNER (default: meishiene)
  - env GITHUB_REPO  (default: web_api_automation)
  - env GITHUB_BRANCH (default: codex/stage4-gate-and-cleanup)
  - env GITHUB_PROXY (default: http://127.0.0.1:7890)
"""

from __future__ import annotations

import os
import sys
from typing import Any

import httpx


def _env(name: str, default: str | None = None) -> str | None:
    val = os.getenv(name)
    if val is None or val.strip() == "":
        return default
    return val.strip()


def _require(name: str) -> str:
    val = _env(name)
    if not val:
        raise SystemExit(f"Missing required env var: {name}")
    return val


def _get_json(client: httpx.Client, url: str) -> dict[str, Any]:
    resp = client.get(url, headers={"Accept": "application/vnd.github+json"})
    resp.raise_for_status()
    data = resp.json()
    if not isinstance(data, dict):
        raise RuntimeError(f"Unexpected JSON payload type: {type(data)}")
    return data


def main() -> int:
    token = _require("GITHUB_TOKEN")
    owner = _env("GITHUB_OWNER", "meishiene")
    repo = _env("GITHUB_REPO", "web_api_automation")
    branch = _env("GITHUB_BRANCH", "codex/stage4-gate-and-cleanup")
    proxy = _env("GITHUB_PROXY", "http://127.0.0.1:7890")

    base = f"https://api.github.com/repos/{owner}/{repo}"
    workflow_file = "ci-stage4-gates.yml"

    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "codex-stage4-gates-checker",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    proxies = None
    if proxy:
        proxies = {"http://": proxy, "https://": proxy}

    with httpx.Client(headers=headers, timeout=30.0, proxies=proxies) as client:
        runs = _get_json(
            client,
            f"{base}/actions/workflows/{workflow_file}/runs?branch={branch}&per_page=1",
        )
        items = runs.get("workflow_runs") or []
        if not items:
            print(f"[ci] no workflow runs found for {workflow_file} on branch {branch}")
            return 2

        run = items[0]
        run_id = run.get("id")
        status = run.get("status")
        conclusion = run.get("conclusion")
        html_url = run.get("html_url")
        print(f"[ci] run_id={run_id} status={status} conclusion={conclusion}")
        if html_url:
            print(f"[ci] url={html_url}")

        if not run_id:
            return 3

        jobs = _get_json(client, f"{base}/actions/runs/{run_id}/jobs?per_page=100")
        job_items = jobs.get("jobs") or []
        for job in job_items:
            name = job.get("name")
            j_status = job.get("status")
            j_conc = job.get("conclusion")
            print(f"[ci] job {name}: status={j_status} conclusion={j_conc}")

        # Exit code indicates "green-ness"
        if status != "completed":
            return 10
        if conclusion != "success":
            return 11
        # Also ensure all jobs succeeded (defensive)
        for job in job_items:
            if job.get("conclusion") != "success":
                return 12
        return 0


if __name__ == "__main__":
    raise SystemExit(main())

