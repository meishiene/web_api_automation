import json

from app.models.run_queue import RunQueue
from app.models.worker_heartbeat import WorkerHeartbeat
from app.models import test_run as test_run_model


def _create_project(client, headers, name: str = "P-queue-worker") -> int:
    resp = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": name, "description": "desc"},
    )
    assert resp.status_code == 200
    return resp.json()["id"]


def _create_schedule_task(client, headers, project_id: int, name: str, target_id: int) -> int:
    resp = client.post(
        "/api/schedule-tasks",
        headers=headers,
        json={
            "project_id": project_id,
            "name": name,
            "cron_expr": "*/5 * * * *",
            "timezone": "UTC",
            "enabled": True,
            "target_type": "test_case",
            "target_id": target_id,
            "payload": {"run_type": "api", "priority": 2},
        },
    )
    assert resp.status_code == 200
    return resp.json()["id"]


def _trigger_task(client, headers, task_id: int) -> int:
    resp = client.post(f"/api/schedule-tasks/{task_id}/trigger", headers=headers)
    assert resp.status_code == 200
    return resp.json()["queue_item_id"]


def test_queue_claim_complete_and_worker_heartbeat(client, create_user_and_login, auth_headers, db_session):
    token = create_user_and_login("owner_queue_worker", "pwd")
    headers = auth_headers(token)
    project_id = _create_project(client, headers, name="P-queue-worker-main")
    task_id = _create_schedule_task(client, headers, project_id, "queue-main", 101)
    queue_item_id = _trigger_task(client, headers, task_id)

    heartbeat_resp = client.post(
        "/api/run-queue/worker/heartbeat",
        headers=headers,
        json={
            "project_id": project_id,
            "worker_id": "worker-a",
            "run_type": "api",
            "status": "online",
        },
    )
    assert heartbeat_resp.status_code == 200
    heartbeat = heartbeat_resp.json()
    assert heartbeat["project_id"] == project_id
    assert heartbeat["worker_id"] == "worker-a"
    assert heartbeat["status"] == "online"

    claim_resp = client.post(
        "/api/run-queue/claim",
        headers=headers,
        json={"project_id": project_id, "worker_id": "worker-a", "run_type": "api"},
    )
    assert claim_resp.status_code == 200
    claim = claim_resp.json()
    assert claim["claimed"] is True
    assert claim["queue_item"]["id"] == queue_item_id
    assert claim["queue_item"]["status"] == "running"
    assert claim["queue_item"]["worker_id"] == "worker-a"

    complete_resp = client.post(
        f"/api/run-queue/{queue_item_id}/complete",
        headers=headers,
        json={"worker_id": "worker-a", "status": "success", "result": {"message": "placeholder done"}},
    )
    assert complete_resp.status_code == 200
    complete = complete_resp.json()
    assert complete["queue_item_id"] == queue_item_id
    assert complete["status"] == "success"

    queue_item = db_session.query(RunQueue).filter(RunQueue.id == queue_item_id).first()
    assert queue_item is not None
    assert queue_item.status == "success"
    assert queue_item.worker_id == "worker-a"
    assert queue_item.started_at is not None
    assert queue_item.finished_at is not None

    hb_record = (
        db_session.query(WorkerHeartbeat)
        .filter(WorkerHeartbeat.project_id == project_id, WorkerHeartbeat.worker_id == "worker-a")
        .first()
    )
    assert hb_record is not None

    queue_list_resp = client.get(f"/api/run-queue/project/{project_id}", headers=headers)
    assert queue_list_resp.status_code == 200
    queue_list = queue_list_resp.json()
    assert queue_list["total"] == 1
    assert queue_list["items"][0]["id"] == queue_item_id

    queue_detail_resp = client.get(f"/api/run-queue/{queue_item_id}", headers=headers)
    assert queue_detail_resp.status_code == 200
    assert queue_detail_resp.json()["status"] == "success"

    heartbeat_list_resp = client.get(f"/api/run-queue/worker/heartbeats/project/{project_id}", headers=headers)
    assert heartbeat_list_resp.status_code == 200
    heartbeat_list = heartbeat_list_resp.json()
    assert heartbeat_list["total"] == 1
    assert heartbeat_list["items"][0]["worker_id"] == "worker-a"


def _create_test_case(client, headers, project_id: int, name: str = "Queue API Case", url: str = "https://example.com"):
    resp = client.post(
        f"/api/test-cases/project/{project_id}",
        headers=headers,
        json={
            "name": name,
            "method": "GET",
            "url": url,
            "expected_status": 200,
        },
    )
    assert resp.status_code == 200
    return resp.json()["id"]


def test_worker_execute_once_consumes_queue_item_with_real_execution(
    client,
    monkeypatch,
    create_user_and_login,
    auth_headers,
    db_session,
):
    token = create_user_and_login("owner_queue_execute_once", "pwd")
    headers = auth_headers(token)
    project_id = _create_project(client, headers, name="P-queue-execute-once")
    case_id = _create_test_case(client, headers, project_id, name="Queue Execute Once Case")
    task_id = _create_schedule_task(client, headers, project_id, "queue-execute-once", case_id)
    queue_item_id = _trigger_task(client, headers, task_id)

    async def fake_execute_test(_test_case, runtime_variables=None):
        return {
            "status": "success",
            "actual_status": 200,
            "actual_body": "{\"ok\": true}",
            "error_message": None,
            "duration_ms": 8,
            "extracted_variables": {},
        }

    monkeypatch.setattr("app.services.queue_worker_runtime.execute_test", fake_execute_test)

    execute_resp = client.post(
        "/api/run-queue/worker/execute-once",
        headers=headers,
        json={
            "project_id": project_id,
            "worker_id": "worker-b",
            "run_type": "api",
        },
    )
    assert execute_resp.status_code == 200
    execute = execute_resp.json()
    assert execute["executed"] is True
    assert execute["queue_item_id"] == queue_item_id
    assert execute["status"] == "success"

    queue_item = db_session.query(RunQueue).filter(RunQueue.id == queue_item_id).first()
    assert queue_item is not None
    assert queue_item.status == "success"
    assert queue_item.worker_id == "worker-b"
    assert queue_item.finished_at is not None
    payload = json.loads(queue_item.payload or "{}")
    assert payload.get("result", {}).get("run_id") is not None
    assert payload.get("result", {}).get("target_type") == "test_case"

    test_runs = db_session.query(test_run_model.TestRun).filter(test_run_model.TestRun.test_case_id == case_id).all()
    assert len(test_runs) == 1
    assert test_runs[0].status == "success"


def test_non_owner_cannot_claim_or_heartbeat(client, create_user_and_login, auth_headers):
    owner_token = create_user_and_login("owner_queue_forbid", "pwd")
    attacker_token = create_user_and_login("attacker_queue_forbid", "pwd")
    owner_headers = auth_headers(owner_token)
    attacker_headers = auth_headers(attacker_token)

    project_id = _create_project(client, owner_headers, name="P-queue-forbid")
    task_id = _create_schedule_task(client, owner_headers, project_id, "queue-forbid", 808)
    _trigger_task(client, owner_headers, task_id)

    attacker_claim = client.post(
        "/api/run-queue/claim",
        headers=attacker_headers,
        json={"project_id": project_id, "worker_id": "worker-z"},
    )
    assert attacker_claim.status_code == 403
    assert attacker_claim.json()["error"]["code"] == "FORBIDDEN"

    attacker_heartbeat = client.post(
        "/api/run-queue/worker/heartbeat",
        headers=attacker_headers,
        json={
            "project_id": project_id,
            "worker_id": "worker-z",
            "status": "online",
        },
    )
    assert attacker_heartbeat.status_code == 403
    assert attacker_heartbeat.json()["error"]["code"] == "FORBIDDEN"

    attacker_queue_list = client.get(f"/api/run-queue/project/{project_id}", headers=attacker_headers)
    assert attacker_queue_list.status_code == 403
    assert attacker_queue_list.json()["error"]["code"] == "FORBIDDEN"
