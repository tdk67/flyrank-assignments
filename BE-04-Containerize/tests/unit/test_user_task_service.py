import uuid

import pytest

from dtos.task_dto import TaskCreateDTO
from dtos.user_dto import UserCreateDTO
from services.task_service import TaskService
from services.user_service import UserService
from services.user_task_service import UserTaskService
from tests.unit.fakes import FakeTaskRepository, FakeUserRepository


@pytest.fixture()
def services():
    user_service = UserService(FakeUserRepository())
    task_service = TaskService(FakeTaskRepository())
    coordinator = UserTaskService(user_service=user_service, task_service=task_service)
    return coordinator, user_service, task_service


def make_user(user_service: UserService):
    return user_service.create_user(UserCreateDTO(first_name="Jane", last_name="Doe", email=None, telephone=None))


def make_task(task_service: TaskService, name: str = "Task"):
    return task_service.create_task(TaskCreateDTO(name=name, description=None))


def test_assign_user_to_task_success(services):
    coordinator, user_service, task_service = services
    user = make_user(user_service)
    task = make_task(task_service)

    updated = coordinator.assign_user_to_task(task.id, user.id)

    assert updated is not None
    assert updated.status == "ASSIGNED"
    assert updated.assignee_user_id == user.id


def test_assign_user_to_task_unknown_user_returns_none(services):
    coordinator, _, task_service = services
    task = make_task(task_service)

    assert coordinator.assign_user_to_task(task.id, uuid.uuid4()) is None


def test_has_assigned_tasks_reflects_current_assignment(services):
    coordinator, user_service, task_service = services
    user = make_user(user_service)
    task = make_task(task_service)

    assert coordinator.has_assigned_tasks(user.id) is False

    coordinator.assign_user_to_task(task.id, user.id)

    assert coordinator.has_assigned_tasks(user.id) is True


def test_unassign_user_tasks_resets_all_and_returns_count(services):
    coordinator, user_service, task_service = services
    user = make_user(user_service)
    first_task = make_task(task_service, name="First")
    second_task = make_task(task_service, name="Second")
    coordinator.assign_user_to_task(first_task.id, user.id)
    coordinator.assign_user_to_task(second_task.id, user.id)

    updated_count = coordinator.unassign_user_tasks(user.id)

    assert updated_count == 2
    assert coordinator.has_assigned_tasks(user.id) is False


def test_unassign_user_tasks_unknown_user_returns_none(services):
    coordinator, _, _ = services

    assert coordinator.unassign_user_tasks(uuid.uuid4()) is None
