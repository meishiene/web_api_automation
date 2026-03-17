from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Literal

from app.services.reporting_input import (
    ReportInputRun,
    build_report_summary,
    map_api_row_to_report_input,
    map_web_row_to_report_input,
)


def build_report_inputs_from_rows(
    api_rows: List[tuple[Any, Any]],
    web_rows: List[tuple[Any, Any]],
    project_id: int,
) -> List[ReportInputRun]:
    report_inputs: List[ReportInputRun] = []
    for run, case in api_rows:
        report_inputs.append(map_api_row_to_report_input(run=run, case=case, project_id=project_id))
    for run, case in web_rows:
        report_inputs.append(map_web_row_to_report_input(run=run, case=case, project_id=project_id))
    return report_inputs


def build_top_failures(items: List[ReportInputRun], top_n: int) -> list[Dict[str, Any]]:
    grouped: Dict[tuple[int, str, str, str], Dict[str, Any]] = {}
    for item in items:
        if not item.failure_category:
            continue
        key = (item.case_id, item.case_name, item.run_type, item.failure_category)
        current = grouped.get(key)
        if current is None:
            grouped[key] = {
                "case_id": item.case_id,
                "case_name": item.case_name,
                "run_type": item.run_type,
                "failure_category": item.failure_category,
                "count": 1,
                "last_error_message": item.error_message,
                "last_seen_at": item.created_at,
            }
            continue

        current["count"] += 1
        if item.created_at >= current["last_seen_at"]:
            current["last_seen_at"] = item.created_at
            current["last_error_message"] = item.error_message

    ordered = sorted(grouped.values(), key=lambda row: (row["count"], row["last_seen_at"]), reverse=True)
    return ordered[:top_n]


def build_project_report_summary(project_id: int, items: List[ReportInputRun], top_n: int) -> Dict[str, Any]:
    summary = build_report_summary([item.status for item in items])
    return {
        "project_id": project_id,
        **summary,
        "top_failures": build_top_failures(items, top_n=top_n),
    }


def _build_bucket(item: ReportInputRun, granularity: Literal["day", "week"]) -> tuple[int, str]:
    dt = datetime.fromtimestamp(item.created_at, tz=timezone.utc)
    if granularity == "day":
        start = datetime(dt.year, dt.month, dt.day, tzinfo=timezone.utc)
        return int(start.timestamp()), start.strftime("%Y-%m-%d")

    week_start_date = dt.date() - timedelta(days=dt.weekday())
    week_start = datetime(
        week_start_date.year,
        week_start_date.month,
        week_start_date.day,
        tzinfo=timezone.utc,
    )
    return int(week_start.timestamp()), week_start.strftime("%Y-%m-%d")


def build_project_trends(
    project_id: int,
    items: List[ReportInputRun],
    granularity: Literal["day", "week"],
) -> Dict[str, Any]:
    buckets: dict[tuple[int, str], list[str]] = defaultdict(list)

    for item in items:
        bucket_key = _build_bucket(item=item, granularity=granularity)
        buckets[bucket_key].append(item.status)

    trend_items = []
    for (bucket_start, bucket_label), statuses in sorted(buckets.items(), key=lambda row: row[0][0]):
        summary = build_report_summary(statuses)
        trend_items.append(
            {
                "bucket_start": bucket_start,
                "bucket_label": bucket_label,
                **summary,
            }
        )

    return {
        "project_id": project_id,
        "granularity": granularity,
        "items": trend_items,
    }


def build_failure_governance_items(
    items: List[ReportInputRun],
    run_type: str | None,
    failure_category: str | None,
    page: int,
    page_size: int,
) -> Dict[str, Any]:
    filtered = [item for item in items if item.failure_category is not None and item.status in {"failed", "error"}]

    if run_type:
        filtered = [item for item in filtered if item.run_type == run_type]
    if failure_category:
        filtered = [item for item in filtered if item.failure_category == failure_category]

    filtered.sort(key=lambda row: (row.created_at, row.run_id), reverse=True)
    total = len(filtered)
    start = (page - 1) * page_size
    end = start + page_size
    page_items = filtered[start:end]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "run_type": item.run_type,
                "run_id": item.run_id,
                "project_id": item.project_id,
                "case_id": item.case_id,
                "case_name": item.case_name,
                "status": item.status,
                "failure_category": item.failure_category,
                "error_message": item.error_message,
                "created_at": item.created_at,
                "detail_api_path": item.detail_api_path,
            }
            for item in page_items
        ],
    }
