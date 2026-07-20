import uuid

from tests.integration.sample_data import ADA_ID, ALAN_ID, GRACE_ID, TASK_SHIP_RELEASE_ID


def test_list_users_returns_seeded_users(client, seeded_db):
    response = client.get("/users")

    assert response.status_code == 200
    ids = {user["id"] for user in response.json()}
    assert ids == {str(ADA_ID), str(ALAN_ID), str(GRACE_ID)}


def test_get_user_by_id(client, seeded_db):
    response = client.get(f"/user/{ADA_ID}")

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == {"first_name": "Ada", "last_name": "Lovelace"}
    assert body["email"] == "ada@example.com"


def test_get_user_not_found(client, seeded_db):
    response = client.get(f"/user/{uuid.uuid4()}")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_list_users_filters_by_first_name(client, seeded_db):
    response = client.get("/users", params={"first_name": "Alan"})

    assert response.status_code == 200
    assert [u["id"] for u in response.json()] == [str(ALAN_ID)]


def test_create_user_minimal(client):
    response = client.post("/user", json={"name": {"first_name": "New", "last_name": "Person"}})

    assert response.status_code == 201
    body = response.json()
    assert body["email"] is None
    assert body["telephone"] is None
    assert uuid.UUID(body["id"])


def test_create_user_rejects_extra_field(client):
    response = client.post(
        "/user",
        json={"name": {"first_name": "Jane", "last_name": "Doe"}, "age": 30},
    )

    assert response.status_code == 422
    assert "age" in response.json()["detail"]


def test_update_user_changes_only_provided_fields(client, seeded_db):
    response = client.patch(f"/user/{ALAN_ID}", json={"email": "alan.turing@example.com"})

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "alan.turing@example.com"
    assert body["name"] == {"first_name": "Alan", "last_name": "Turing"}


def test_delete_user_blocked_while_assigned(client, seeded_db):
    response = client.delete(f"/user/{ADA_ID}")

    assert response.status_code == 409
    assert "still has assigned tasks" in response.json()["detail"]


def test_unassign_then_delete_user_succeeds(client, seeded_db):
    unassign_response = client.post(f"/users/{ADA_ID}/tasks/unassign")
    assert unassign_response.status_code == 200
    assert unassign_response.json()["unassigned_count"] == 1

    delete_response = client.delete(f"/user/{ADA_ID}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/user/{ADA_ID}")
    assert get_response.status_code == 404


def test_delete_user_with_only_done_task_succeeds(client, seeded_db):
    """Grace only owns a DONE task; that's a historical record, not an active assignment,
    so it must not block deletion (the FK is ON DELETE SET NULL)."""
    delete_response = client.delete(f"/user/{GRACE_ID}")
    assert delete_response.status_code == 204

    task_response = client.get(f"/task/{TASK_SHIP_RELEASE_ID}")
    assert task_response.status_code == 200
    body = task_response.json()
    assert body["status"] == "DONE"
    assert body["assignee_user_id"] is None
