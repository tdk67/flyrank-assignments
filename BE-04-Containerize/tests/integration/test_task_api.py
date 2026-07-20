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


def test_get_task_includes_lifecycle_timestamps(client, seeded_db):
    response = client.get(f"/task/{TASK_SHIP_RELEASE_ID}")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "DONE"
    assert body["assignee_user_id"] == str(GRACE_ID)
    assert body["assigned_at"] is not None
    assert body["started_at"] is not None
    assert body["finished_at"] is not None


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
    assert body["assigned_at"] is not None


def test_assign_already_assigned_task_rejected(client, seeded_db):
    response = client.patch(
        f"/task/{TASK_IMPLEMENT_SERVICE_ID}/assignee",
        json={"assignee_user_id": str(ALAN_ID)},
    )

    assert response.status_code == 409
    assert "Only a PLANNED task can be assigned" in response.json()["detail"]


def test_assign_task_to_unknown_user_returns_404(client, seeded_db):
    response = client.patch(
        f"/task/{TASK_DESIGN_API_ID}/assignee",
        json={"assignee_user_id": str(uuid.uuid4())},
    )

    assert response.status_code == 404


def test_valid_status_transition(client, seeded_db):
    response = client.patch(f"/task/{TASK_WRITE_TESTS_ID}/status", json={"status": "DONE"})

    assert response.status_code == 200
    assert response.json()["status"] == "DONE"


def test_invalid_status_transition_rejected(client, seeded_db):
    response = client.patch(f"/task/{TASK_DESIGN_API_ID}/status", json={"status": "STARTED"})

    assert response.status_code == 409
    assert "Invalid status transition" in response.json()["detail"]


def test_delete_task(client, seeded_db):
    response = client.delete(f"/task/{TASK_SHIP_RELEASE_ID}")

    assert response.status_code == 204
    assert client.get(f"/task/{TASK_SHIP_RELEASE_ID}").status_code == 404
