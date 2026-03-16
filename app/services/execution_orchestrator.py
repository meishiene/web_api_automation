import json
import time
from typing import Any

from sqlalchemy.orm import Session

from app.models.execution_job import ExecutionJob
from app.models.execution_task import ExecutionTask
from app.services.execution_contract import ExecutionAdapter
from app.services.execution_status import map_result_status


def _to_json_text(payload: dict[str, Any] | None) -> str | None:
    if payload is None:
        return None
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


async def run_execution_task(
    db: Session,
    *,
    project_id: int,
    run_type: str,
    target_type: str,
    target_id: int,
    adapter: ExecutionAdapter,
    created_by: int | None = None,
    trigger_mode: str = "manual",
    context: dict[str, Any] | None = None,
) -> tuple[ExecutionTask, ExecutionJob, dict[str, Any]]:
    now = int(time.time())
    task = ExecutionTask(
        project_id=project_id,
        run_type=run_type,
        target_type=target_type,
        target_id=target_id,
        status="running",
        trigger_mode=trigger_mode,
        context_json=_to_json_text(context),
        created_by=created_by,
        started_at=now,
        created_at=now,
        updated_at=now,
    )
    db.add(task)
    db.flush()

    job = ExecutionJob(
        task_id=task.id,
        attempt_no=1,
        executor_type=run_type,
        status="running",
        started_at=now,
        created_at=now,
    )
    db.add(job)
    db.flush()

    try:
        result = await adapter.execute()
        final_status, error_code = map_result_status(result)
        error_message = result.get("error_message")
    except Exception as exc:
        result = {
            "status": "error",
            "actual_status": None,
            "actual_body": None,
            "error_message": str(exc),
            "duration_ms": 0,
            "extracted_variables": {},
        }
        final_status = "error"
        error_code = "EXECUTION_EXCEPTION"
        error_message = str(exc)

    finished_at = int(time.time())
    task.status = final_status
    task.error_code = error_code
    task.error_message = error_message
    task.finished_at = finished_at
    task.updated_at = finished_at

    job.status = final_status
    job.error_code = error_code
    job.error_message = error_message
    job.output_json = _to_json_text(result)
    job.finished_at = finished_at

    db.flush()
    return task, job, result
