from app.models.run_queue import RunQueue


def test_schedule_task_crud_and_trigger_creates_queue_item(client, create_user_and_login, auth_headers, db_session):
    token = create_user_and_login("owner_schedule", "pwd")
    headers = auth_headers(token)

    project_resp = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P-schedule", "description": "desc"},
    )
    assert project_resp.status_code == 200
    project_id = project_resp.json()["id"]

    create_resp = client.post(
        "/api/schedule-tasks",
        headers=headers,
        json={
            "project_id": project_id,
            "name": "daily-api-smoke",
            "cron_expr": "0 9 * * *",
            "timezone": "Asia/Shanghai",
            "enabled": True,
            "target_type": "test_case",
            "target_id": 101,
            "payload": {"run_type": "api", "priority": 3, "environment_id": 1},
        },
    )
    assert create_resp.status_code == 200
    task = create_resp.json()
    assert task["project_id"] == project_id
    assert task["enabled"] is True
    task_id = task["id"]

    list_resp = client.get(f"/api/schedule-tasks/project/{project_id}", headers=headers)
    assert list_resp.status_code == 200
    listed = list_resp.json()
    assert listed["total"] == 1
    assert listed["items"][0]["id"] == task_id

    update_resp = client.put(
        f"/api/schedule-tasks/{task_id}",
        headers=headers,
        json={
            "name": "daily-api-smoke-updated",
            "cron_expr": "*/15 * * * *",
            "timezone": "UTC",
            "enabled": True,
            "target_type": "test_case",
            "target_id": 202,
            "payload": {"run_type": "web", "priority": 4},
        },
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["name"] == "daily-api-smoke-updated"
    assert updated["target_id"] == 202
    assert updated["payload"]["run_type"] == "web"

    trigger_resp = client.post(f"/api/schedule-tasks/{task_id}/trigger", headers=headers)
    assert trigger_resp.status_code == 200
    trigger = trigger_resp.json()
    assert trigger["schedule_task_id"] == task_id
    assert trigger["status"] == "queued"

    queue_item = db_session.query(RunQueue).filter(RunQueue.id == trigger["queue_item_id"]).first()
    assert queue_item is not None
    assert queue_item.project_id == project_id
    assert queue_item.run_type == "web"
    assert queue_item.target_type == "test_case"
    assert queue_item.target_id == 202
    assert queue_item.status == "queued"
    assert queue_item.scheduled_by == "scheduler"

    delete_resp = client.delete(f"/api/schedule-tasks/{task_id}", headers=headers)
    assert delete_resp.status_code == 200
    assert delete_resp.json()["message"] == "Schedule task deleted"

    list_after_delete = client.get(f"/api/schedule-tasks/project/{project_id}", headers=headers)
    assert list_after_delete.status_code == 200
    assert list_after_delete.json()["total"] == 0


def test_non_owner_cannot_manage_schedule_task(client, create_user_and_login, auth_headers):
    owner_token = create_user_and_login("owner_schedule_forbid", "pwd")
    attacker_token = create_user_and_login("attacker_schedule_forbid", "pwd")

    project_resp = client.post(
        "/api/projects/",
        headers=auth_headers(owner_token),
        json={"name": "P-schedule-forbid", "description": "desc"},
    )
    assert project_resp.status_code == 200
    project_id = project_resp.json()["id"]

    create_resp = client.post(
        "/api/schedule-tasks",
        headers=auth_headers(owner_token),
        json={
            "project_id": project_id,
            "name": "forbid-task",
            "cron_expr": "0 * * * *",
            "timezone": "UTC",
            "enabled": True,
            "target_type": "test_case",
            "target_id": 1,
            "payload": {"run_type": "api"},
        },
    )
    assert create_resp.status_code == 200
    task_id = create_resp.json()["id"]

    attacker_list = client.get(f"/api/schedule-tasks/project/{project_id}", headers=auth_headers(attacker_token))
    assert attacker_list.status_code == 403
    assert attacker_list.json()["error"]["code"] == "FORBIDDEN"

    attacker_trigger = client.post(f"/api/schedule-tasks/{task_id}/trigger", headers=auth_headers(attacker_token))
    assert attacker_trigger.status_code == 403
    assert attacker_trigger.json()["error"]["code"] == "FORBIDDEN"


def test_trigger_disabled_schedule_task_returns_validation_error(client, create_user_and_login, auth_headers):
    token = create_user_and_login("owner_schedule_disabled", "pwd")
    headers = auth_headers(token)

    project_resp = client.post(
        "/api/projects/",
        headers=headers,
        json={"name": "P-schedule-disabled", "description": "desc"},
    )
    assert project_resp.status_code == 200
    project_id = project_resp.json()["id"]

    create_resp = client.post(
        "/api/schedule-tasks",
        headers=headers,
        json={
            "project_id": project_id,
            "name": "disabled-task",
            "cron_expr": "0 * * * *",
            "timezone": "UTC",
            "enabled": False,
            "target_type": "test_case",
            "target_id": 1,
            "payload": {"run_type": "api"},
        },
    )
    assert create_resp.status_code == 200
    task_id = create_resp.json()["id"]

    trigger_resp = client.post(f"/api/schedule-tasks/{task_id}/trigger", headers=headers)
    assert trigger_resp.status_code == 400
    assert trigger_resp.json()["error"]["code"] == "VALIDATION_ERROR"
