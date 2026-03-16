import inspect
import json
import time
from pathlib import Path
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models.api_batch_run import ApiBatchRun
from app.models.api_batch_run_item import ApiBatchRunItem
from app.models.api_test_case import ApiTestCase
from app.models.api_test_suite import ApiTestSuite
from app.models.api_test_suite_case import ApiTestSuiteCase
from app.models.project_environment import ProjectEnvironment
from app.models.run_queue import RunQueue
from app.models.test_run import TestRun
from app.models.web_test_case import WebTestCase
from app.models.web_test_run import WebTestRun
from app.models.worker_heartbeat import WorkerHeartbeat
from app.services.execution_contract import ExecutionAdapter
from app.services.execution_orchestrator import run_execution_task
from app.services.test_executor import execute_test
from app.services.variable_resolver import mask_secret_value, resolve_runtime_variables_with_meta
from app.services.web_executor import execute_web_test_case


def claim_one_queue_item(
    db: Session,
    *,
    project_id: int,
    worker_id: str,
    run_type: Optional[str],
) -> Optional[RunQueue]:
    query = db.query(RunQueue).filter(
        RunQueue.project_id == project_id,
        RunQueue.status == "queued",
    )
    if run_type:
        query = query.filter(RunQueue.run_type == run_type)

    queue_item = (
        query.order_by(
            RunQueue.priority.asc(),
            RunQueue.created_at.asc(),
            RunQueue.id.asc(),
        )
        .first()
    )
    if not queue_item:
        return None

    queue_item.status = "running"
    queue_item.worker_id = worker_id
    queue_item.started_at = int(time.time())
    db.commit()
    db.refresh(queue_item)
    return queue_item


def upsert_worker_heartbeat(
    db: Session,
    *,
    project_id: int,
    worker_id: str,
    run_type: Optional[str],
    status: str,
    current_queue_item_id: Optional[int] = None,
) -> WorkerHeartbeat:
    now = int(time.time())
    heartbeat = (
        db.query(WorkerHeartbeat)
        .filter(
            WorkerHeartbeat.project_id == project_id,
            WorkerHeartbeat.worker_id == worker_id,
        )
        .first()
    )
    if heartbeat:
        heartbeat.run_type = run_type
        heartbeat.status = status
        heartbeat.current_queue_item_id = current_queue_item_id
        heartbeat.last_heartbeat_at = now
        heartbeat.updated_at = now
    else:
        heartbeat = WorkerHeartbeat(
            project_id=project_id,
            worker_id=worker_id,
            run_type=run_type,
            status=status,
            current_queue_item_id=current_queue_item_id,
            last_heartbeat_at=now,
            created_at=now,
            updated_at=now,
        )
        db.add(heartbeat)

    db.commit()
    db.refresh(heartbeat)
    return heartbeat


def complete_queue_item(
    db: Session,
    *,
    queue_item: RunQueue,
    worker_id: str,
    status: str,
    result: dict[str, Any],
) -> RunQueue:
    now = int(time.time())
    if queue_item.started_at is None:
        queue_item.started_at = now
    queue_item.worker_id = worker_id
    queue_item.status = status
    queue_item.finished_at = now
    queue_item.payload = json.dumps(
        {
            "input": _safe_json_loads(queue_item.payload),
            "result": result,
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    db.commit()
    db.refresh(queue_item)
    return queue_item


async def consume_queue_item_once(
    db: Session,
    *,
    project_id: int,
    worker_id: str,
    run_type: Optional[str],
) -> dict[str, Any]:
    queue_item = claim_one_queue_item(
        db=db,
        project_id=project_id,
        worker_id=worker_id,
        run_type=run_type,
    )
    if not queue_item:
        upsert_worker_heartbeat(
            db=db,
            project_id=project_id,
            worker_id=worker_id,
            run_type=run_type,
            status="online",
            current_queue_item_id=None,
        )
        return {"executed": False}

    upsert_worker_heartbeat(
        db=db,
        project_id=project_id,
        worker_id=worker_id,
        run_type=run_type,
        status="busy",
        current_queue_item_id=queue_item.id,
    )

    try:
        result = await execute_queue_item(db=db, queue_item=queue_item)
        final_status = result.get("status", "error")
        if final_status not in {"success", "failed", "error"}:
            final_status = "error"
    except Exception as exc:
        final_status = "error"
        result = {"status": "error", "error_message": str(exc)}

    complete_queue_item(
        db=db,
        queue_item=queue_item,
        worker_id=worker_id,
        status=final_status,
        result=result,
    )
    upsert_worker_heartbeat(
        db=db,
        project_id=project_id,
        worker_id=worker_id,
        run_type=run_type,
        status="online",
        current_queue_item_id=None,
    )
    return {
        "executed": True,
        "queue_item_id": queue_item.id,
        "status": final_status,
        "result": result,
    }


async def execute_queue_item(db: Session, *, queue_item: RunQueue) -> dict[str, Any]:
    if queue_item.run_type == "api" and queue_item.target_type == "test_case":
        return await _execute_api_test_case_queue_item(db=db, queue_item=queue_item)
    if queue_item.run_type == "api" and queue_item.target_type == "test_suite":
        return await _execute_api_test_suite_queue_item(db=db, queue_item=queue_item)
    if queue_item.run_type == "web" and queue_item.target_type == "test_case":
        return await _execute_web_test_case_queue_item(db=db, queue_item=queue_item)
    return {
        "status": "error",
        "error_message": f"Unsupported queue target: {queue_item.run_type}/{queue_item.target_type}",
    }


def _safe_json_loads(raw: Optional[str]) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _to_json_text(payload: dict[str, Any] | None) -> str | None:
    if payload is None:
        return None
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _build_masked_runtime_snapshot(runtime_variables: dict[str, Any], secret_keys: set[str]) -> dict[str, str]:
    return {
        key: mask_secret_value(str(value), key in secret_keys)
        for key, value in runtime_variables.items()
    }


def _persist_test_run(
    db: Session,
    *,
    case_id: int,
    result: dict[str, Any],
    runtime_variables: dict[str, Any],
    variable_sources: dict[str, str],
    secret_keys: set[str],
) -> TestRun:
    test_run = TestRun(
        test_case_id=case_id,
        status=result["status"],
        actual_status=result.get("actual_status"),
        actual_body=result.get("actual_body"),
        error_message=result.get("error_message"),
        duration_ms=result.get("duration_ms"),
        runtime_variables=_to_json_text(_build_masked_runtime_snapshot(runtime_variables, secret_keys)),
        variable_sources=_to_json_text(variable_sources),
        created_at=int(time.time()),
    )
    db.add(test_run)
    db.flush()
    return test_run


async def _execute_api_test_case_queue_item(db: Session, *, queue_item: RunQueue) -> dict[str, Any]:
    payload = _safe_json_loads(queue_item.payload)
    environment_id = _read_int(payload.get("environment_id"))

    test_case = (
        db.query(ApiTestCase)
        .filter(ApiTestCase.id == queue_item.target_id, ApiTestCase.project_id == queue_item.project_id)
        .first()
    )
    if not test_case:
        return {"status": "error", "error_message": "API test case not found in project"}

    runtime_variables, variable_sources, secret_keys = resolve_runtime_variables_with_meta(
        db=db,
        project_id=queue_item.project_id,
        environment_id=environment_id,
    )

    class _ApiCaseExecutionAdapter(ExecutionAdapter):
        async def execute(self) -> dict[str, Any]:
            execute_signature = inspect.signature(execute_test)
            if "runtime_variables" in execute_signature.parameters:
                return await execute_test(test_case, runtime_variables=runtime_variables)
            return await execute_test(test_case)

    _task, _job, result = await run_execution_task(
        db=db,
        project_id=queue_item.project_id,
        run_type="api",
        target_type="test_case",
        target_id=test_case.id,
        adapter=_ApiCaseExecutionAdapter(),
        created_by=None,
        trigger_mode=queue_item.scheduled_by,
        context={"queue_item_id": queue_item.id},
    )

    test_run = _persist_test_run(
        db=db,
        case_id=test_case.id,
        result=result,
        runtime_variables=runtime_variables,
        variable_sources=variable_sources,
        secret_keys=secret_keys,
    )
    db.commit()
    db.refresh(test_run)
    return {
        "status": test_run.status,
        "run_id": test_run.id,
        "target_type": "test_case",
    }


async def _execute_api_test_suite_queue_item(db: Session, *, queue_item: RunQueue) -> dict[str, Any]:
    payload = _safe_json_loads(queue_item.payload)
    environment_id = _read_int(payload.get("environment_id"))
    retry_count = max(_read_int(payload.get("retry_count"), default=0), 0)
    retry_on = _parse_retry_on(payload.get("retry_on"))

    suite = (
        db.query(ApiTestSuite)
        .filter(ApiTestSuite.id == queue_item.target_id, ApiTestSuite.project_id == queue_item.project_id)
        .first()
    )
    if not suite:
        return {"status": "error", "error_message": "API test suite not found in project"}

    if environment_id is not None:
        environment = (
            db.query(ProjectEnvironment)
            .filter(ProjectEnvironment.id == environment_id, ProjectEnvironment.project_id == queue_item.project_id)
            .first()
        )
        if not environment:
            return {"status": "error", "error_message": "Environment not found in project"}

    links = (
        db.query(ApiTestSuiteCase)
        .filter(ApiTestSuiteCase.suite_id == suite.id)
        .order_by(ApiTestSuiteCase.order_index.asc(), ApiTestSuiteCase.id.asc())
        .all()
    )
    if not links:
        return {"status": "error", "error_message": "API test suite has no test cases"}

    now = int(time.time())
    batch = ApiBatchRun(
        project_id=queue_item.project_id,
        suite_id=suite.id,
        environment_id=environment_id,
        triggered_by=None,
        status="running",
        total_cases=len(links),
        passed_cases=0,
        failed_cases=0,
        error_cases=0,
        started_at=now,
        created_at=now,
    )
    db.add(batch)
    db.flush()

    runtime_variables, variable_sources, secret_keys = resolve_runtime_variables_with_meta(
        db=db,
        project_id=queue_item.project_id,
        environment_id=environment_id,
    )

    for link in links:
        result = await _execute_api_case_with_retry(
            test_case=link.test_case,
            runtime_variables=runtime_variables,
            retry_count=retry_count,
            retry_on=retry_on,
        )
        test_run = _persist_test_run(
            db=db,
            case_id=link.test_case_id,
            result=result,
            runtime_variables=runtime_variables,
            variable_sources=variable_sources,
            secret_keys=secret_keys,
        )

        db.add(
            ApiBatchRunItem(
                batch_run_id=batch.id,
                test_case_id=link.test_case_id,
                test_run_id=test_run.id,
                order_index=link.order_index,
                status=result["status"],
                error_message=result.get("error_message"),
                created_at=int(time.time()),
            )
        )

        if result["status"] == "success":
            batch.passed_cases += 1
            extracted_variables = result.get("extracted_variables") or {}
            runtime_variables.update(extracted_variables)
            for extracted_key in extracted_variables:
                variable_sources[extracted_key] = "extracted"
                secret_keys.discard(extracted_key)
        elif result["status"] == "failed":
            batch.failed_cases += 1
        else:
            batch.error_cases += 1

    if batch.error_cases > 0:
        batch.status = "error"
    elif batch.failed_cases > 0:
        batch.status = "failed"
    else:
        batch.status = "success"
    batch.finished_at = int(time.time())

    db.commit()
    db.refresh(batch)
    return {
        "status": batch.status,
        "batch_run_id": batch.id,
        "target_type": "test_suite",
    }


async def _execute_api_case_with_retry(
    *,
    test_case: ApiTestCase,
    runtime_variables: dict[str, Any],
    retry_count: int,
    retry_on: set[str],
) -> dict[str, Any]:
    attempts = 0
    result: dict[str, Any] | None = None
    while attempts <= retry_count:
        execute_signature = inspect.signature(execute_test)
        if "runtime_variables" in execute_signature.parameters:
            result = await execute_test(test_case, runtime_variables=runtime_variables)
        else:
            result = await execute_test(test_case)
        if result.get("status") not in retry_on:
            break
        if attempts >= retry_count:
            break
        attempts += 1
    return result or {"status": "error", "error_message": "Execution returned empty result"}


async def _execute_web_test_case_queue_item(db: Session, *, queue_item: RunQueue) -> dict[str, Any]:
    test_case = (
        db.query(WebTestCase)
        .filter(WebTestCase.id == queue_item.target_id, WebTestCase.project_id == queue_item.project_id)
        .first()
    )
    if not test_case:
        return {"status": "error", "error_message": "Web test case not found in project"}

    now = int(time.time())
    run = WebTestRun(
        project_id=queue_item.project_id,
        web_test_case_id=test_case.id,
        triggered_by=None,
        status="running",
        started_at=now,
        created_at=now,
    )
    db.add(run)
    db.flush()

    artifact_dir_path = Path("artifacts") / "web-test-runs" / str(run.id)
    run.artifact_dir = str(artifact_dir_path)
    artifact_dir_path.mkdir(parents=True, exist_ok=True)
    db.flush()

    class _WebCaseExecutionAdapter(ExecutionAdapter):
        async def execute(self) -> dict[str, Any]:
            return await execute_web_test_case(test_case, artifact_dir=run.artifact_dir)

    _task, _job, result = await run_execution_task(
        db=db,
        project_id=queue_item.project_id,
        run_type="web",
        target_type="test_case",
        target_id=test_case.id,
        adapter=_WebCaseExecutionAdapter(),
        created_by=None,
        trigger_mode=queue_item.scheduled_by,
        context={"queue_item_id": queue_item.id, "artifact_dir": run.artifact_dir},
    )

    run.status = result.get("status", "error")
    run.error_message = result.get("error_message")
    run.duration_ms = result.get("duration_ms")
    run.step_logs_json = json.dumps(result.get("step_logs", []), ensure_ascii=False)
    run.artifacts_json = json.dumps(result.get("artifacts", []), ensure_ascii=False)
    run.finished_at = int(time.time())

    db.commit()
    db.refresh(run)
    return {
        "status": run.status,
        "run_id": run.id,
        "target_type": "test_case",
    }


def _read_int(raw: Any, default: int | None = None) -> int | None:
    if raw is None:
        return default
    try:
        return int(raw)
    except (TypeError, ValueError):
        return default


def _parse_retry_on(raw: Any) -> set[str]:
    allowed = {"failed", "error"}
    if isinstance(raw, list):
        normalized = {str(item).strip().lower() for item in raw}
    elif raw is None:
        normalized = {"error"}
    else:
        normalized = {str(raw).strip().lower()}

    picked = normalized & allowed
    return picked or {"error"}
