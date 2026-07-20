import uuid

import pytest

from dtos.task_dto import TaskCreateDTO, TaskStatusUpdateDTO, TaskUpdateDTO
from services.task_service import TaskService
from tests.unit.fakes import FakeTaskRepository


@pytest.fixture()
def service() -> TaskService:
    return TaskService(FakeTaskRepository())


def make_task(service: TaskService, name: str = "Task", description: str | None = None):
    return service.create_task(TaskCreateDTO(name=name, description=description))


def force_status(service: TaskService, task_id, status: str) -> None:
    """Directly mutate a task's stored status, bypassing the state machine, to set up a scenario."""
    existing = service.task_repository.get_by_id(str(task_id))
    existing.status = status
    service.task_repository.update(existing)


def test_create_task_defaults_to_planned(service):
    task = make_task(service)

    assert task.status == "PLANNED"
    assert task.assignee_user_id is None


def test_create_task_rejects_unsupported_status(service):
    with pytest.raises(ValueError, match="Unsupported status"):
        service.create_task(TaskCreateDTO(name="T", description=None, status="BOGUS"))


def test_update_task_changes_only_provided_fields(service):
    task = make_task(service, description="original")

    updated = service.update_task(task.id, TaskUpdateDTO(estimated_duration_days=3))

    assert updated is not None
    assert updated.estimated_duration_days == 3
    assert updated.description == "original"


def test_update_task_missing_returns_none(service):
    assert service.update_task(uuid.uuid4(), TaskUpdateDTO(estimated_duration_days=1)) is None


def test_valid_status_transition_sets_timestamp(service):
    task = make_task(service)

    updated = service.change_status(task.id, TaskStatusUpdateDTO(status="ASSIGNED"))

    assert updated.status == "ASSIGNED"
    assert updated.assigned_at is not None


def test_invalid_status_transition_raises(service):
    task = make_task(service)
    force_status(service, task.id, "DONE")

    with pytest.raises(ValueError, match="Invalid status transition"):
        service.change_status(task.id, TaskStatusUpdateDTO(status="STARTED"))


def test_change_status_rejects_unsupported_status(service):
    task = make_task(service)

    with pytest.raises(ValueError, match="Unsupported status"):
        service.change_status(task.id, TaskStatusUpdateDTO(status="BOGUS"))


def test_change_status_missing_task_returns_none(service):
    assert service.change_status(uuid.uuid4(), TaskStatusUpdateDTO(status="ASSIGNED")) is None


def test_assign_task_transitions_to_assigned(service):
    task = make_task(service)
    user_id = uuid.uuid4()

    updated = service.assign_task(task.id, user_id)

    assert updated.status == "ASSIGNED"
    assert updated.assignee_user_id == user_id
    assert updated.assigned_at is not None


def test_assign_task_requires_planned_status(service):
    task = make_task(service)
    force_status(service, task.id, "STARTED")

    with pytest.raises(ValueError, match="Only a PLANNED task can be assigned"):
        service.assign_task(task.id, uuid.uuid4())


def test_unassign_task_resets_lifecycle_fields(service):
    task = make_task(service)
    service.assign_task(task.id, uuid.uuid4())

    updated = service.unassign_task(task.id)

    assert updated.status == "PLANNED"
    assert updated.assignee_user_id is None
    assert updated.assigned_at is None


def test_delete_task_removes_record(service):
    task = make_task(service)

    assert service.delete_task(task.id) is True
    assert service.get_task_by_id(task.id) is None


def test_delete_task_missing_returns_false(service):
    assert service.delete_task(uuid.uuid4()) is False
