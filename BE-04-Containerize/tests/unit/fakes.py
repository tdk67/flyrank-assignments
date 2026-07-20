"""In-memory fakes for the repository ports, used to unit test the service layer without a database."""

import uuid

from models import Task, User
from repositories.task_repository_port import TaskRepositoryPort
from repositories.user_repository_port import UserRepositoryPort


class FakeUserRepository(UserRepositoryPort):
    def __init__(self):
        self._store: dict[str, User] = {}

    def create(self, user: User) -> User:
        if user.id is None:
            user.id = uuid.uuid4()
        self._store[str(user.id)] = user
        return user

    def get_by_id(self, user_id: str) -> User | None:
        return self._store.get(str(user_id))

    def list_users(
        self,
        email: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        telephone: str | None = None,
    ) -> list[User]:
        results = list(self._store.values())
        if email is not None:
            results = [u for u in results if u.email == email]
        if first_name is not None:
            results = [u for u in results if u.first_name == first_name]
        if last_name is not None:
            results = [u for u in results if u.last_name == last_name]
        if telephone is not None:
            results = [u for u in results if u.telephone == telephone]
        return results

    def update(self, user: User) -> User:
        self._store[str(user.id)] = user
        return user

    def delete(self, user: User) -> None:
        self._store.pop(str(user.id), None)


class FakeTaskRepository(TaskRepositoryPort):
    def __init__(self):
        self._store: dict[str, Task] = {}

    def create(self, task: Task) -> Task:
        if task.id is None:
            task.id = uuid.uuid4()
        self._store[str(task.id)] = task
        return task

    def get_by_id(self, task_id: str) -> Task | None:
        return self._store.get(str(task_id))

    def list_tasks(
        self,
        assignee_user_id: str | None = None,
        status: str | None = None,
        name: str | None = None,
    ) -> list[Task]:
        results = list(self._store.values())
        if assignee_user_id is not None:
            results = [t for t in results if t.assignee_user_id is not None and str(t.assignee_user_id) == str(assignee_user_id)]
        if status is not None:
            results = [t for t in results if t.status == status]
        if name is not None:
            results = [t for t in results if t.name == name]
        return results

    def update(self, task: Task) -> Task:
        self._store[str(task.id)] = task
        return task

    def delete(self, task: Task) -> None:
        self._store.pop(str(task.id), None)
