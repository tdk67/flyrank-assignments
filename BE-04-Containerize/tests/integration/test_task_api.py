import uuid

from tests.integration.sample_data import (
    ALAN_ID,
    GRACE_ID,
    TASK_DESIGN_API_ID,
    TASK_IMPLEMENT_SERVICE_ID,
    TASK_SHIP_RELEASE_ID,
    TASK_WRITE_TESTS_ID,
)


def test_list_tasks_returns_seeded_tasks(client, seeded_db):
    response = client.get("/tasks")

    assert response.status_code == 200
    assert len(response.json()) == 4


def test_list_tasks_filter_by_status(client, seeded_db):
    response = client.get("/tasks", params={"status": "DONE"})

    assert response.status_code == 200
    ids = {t["id"] for t in response.json()}
    assert ids == {str(TASK_SHIP_RELEASE_ID)}


def test_list_tasks_filter_by_assignee(client, seeded_db):
    response = client.get("/tasks", params={"assignee_user_id": str(ALAN_ID)})

    assert response.status_code == 200
    ids = {t["id"] for t in response.json()}
    assert ids == {str(TASK_WRITE_TESTS_ID)}


def test_get_task_includes_start_and_end_date(client, seeded_db):
    response = client.get(f"/task/{TASK_SHIP_RELEASE_ID}")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "DONE"
    assert body["assignee_user_id"] == str(GRACE_ID)
    assert body["start_date"] is not None
    assert body["end_date"] is not None


def test_get_task_not_found(client, seeded_db):
    response = client.get(f"/task/{uuid.uuid4()}")

    assert response.status_code == 404


def test_create_task_minimal_defaults(client):
    response = client.post(
        "/task",
        json={"name": "Prepare sprint backlog", "description": "Draft the backlog"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "PLANNED"
    assert body["assignee_user_id"] is None


def test_create_task_accepts_optional_metadata(client):
    response = client.post(
        "/task",
        json={
            "name": "Prepare sprint backlog",
            "description": "Draft the backlog",
            "estimated_duration_days": 5,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "PLANNED"
    assert body["assignee_user_id"] is None
    assert body["estimated_duration_days"] == 5
    assert body["start_date"] is None
    assert body["end_date"] is None


def test_create_task_rejects_lifecycle_fields(client):
    response = client.post(
        "/task",
        json={"name": "T", "status": "DONE", "assignee_user_id": str(uuid.uuid4())},
    )

    assert response.status_code == 422


def test_create_task_rejects_start_and_end_date(client):
    response = client.post(
        "/task",
        json={"name": "T", "start_date": "2026-08-01T09:00:00Z", "end_date": "2026-08-08T17:00:00Z"},
    )

    assert response.status_code == 422


def test_create_task_rejects_extra_field(client):
    response = client.post("/task", json={"name": "T", "priority": "high"})

    assert response.status_code == 422
    assert "priority" in response.json()["detail"]


def test_assign_planned_task_to_user(client, seeded_db):
    response = client.patch(
        f"/task/{TASK_DESIGN_API_ID}/assignee",
        json={"assignee_user_id": str(GRACE_ID)},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ASSIGNED"
    assert body["assignee_user_id"] == str(GRACE_ID)


def test_reassign_assigned_task_swaps_owner(client, seeded_db):
    response = client.patch(
        f"/task/{TASK_IMPLEMENT_SERVICE_ID}/assignee",
        json={"assignee_user_id": str(ALAN_ID)},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ASSIGNED"
    assert body["assignee_user_id"] == str(ALAN_ID)


def test_reassign_started_task_rejected(client, seeded_db):
    response = client.patch(
        f"/task/{TASK_WRITE_TESTS_ID}/assignee",
        json={"assignee_user_id": str(GRACE_ID)},
    )

    assert response.status_code == 409
    assert "Only a PLANNED or ASSIGNED task" in response.json()["detail"]


def test_assign_task_to_unknown_user_returns_404(client, seeded_db):
    response = client.patch(
        f"/task/{TASK_DESIGN_API_ID}/assignee",
        json={"assignee_user_id": str(uuid.uuid4())},
    )

    assert response.status_code == 404


def test_deassign_started_task_returns_to_planned(client, seeded_db):
    response = client.delete(f"/task/{TASK_WRITE_TESTS_ID}/assignee")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "PLANNED"
    assert body["assignee_user_id"] is None
    assert body["start_date"] is None
    assert body["end_date"] is None


def test_deassign_done_task_preserves_completion_record(client, seeded_db):
    response = client.delete(f"/task/{TASK_SHIP_RELEASE_ID}/assignee")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "DONE"
    assert body["assignee_user_id"] is None
    assert body["start_date"] is not None
    assert body["end_date"] is not None


def test_deassign_task_not_found(client, seeded_db):
    response = client.delete(f"/task/{uuid.uuid4()}/assignee")

    assert response.status_code == 404


def test_valid_status_transition(client, seeded_db):
    response = client.patch(f"/task/{TASK_WRITE_TESTS_ID}/status", json={"status": "DONE"})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "DONE"
    assert body["end_date"] is not None


def test_update_task_rejects_start_and_end_date(client, seeded_db):
    response = client.patch(
        f"/task/{TASK_DESIGN_API_ID}",
        json={"start_date": "2026-08-01T09:00:00Z", "end_date": "2026-08-08T17:00:00Z"},
    )

    assert response.status_code == 422


def test_invalid_status_transition_rejected(client, seeded_db):
    response = client.patch(f"/task/{TASK_DESIGN_API_ID}/status", json={"status": "STARTED"})

    assert response.status_code == 409
    assert "Invalid status transition" in response.json()["detail"]


def test_delete_task(client, seeded_db):
    response = client.delete(f"/task/{TASK_SHIP_RELEASE_ID}")

    assert response.status_code == 204
    assert client.get(f"/task/{TASK_SHIP_RELEASE_ID}").status_code == 404
