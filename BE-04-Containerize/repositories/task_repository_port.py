from abc import ABC, abstractmethod

from models import Task


class TaskRepositoryPort(ABC):
    @abstractmethod
    def create(self, task: Task) -> Task:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, task_id: str) -> Task | None:
        raise NotImplementedError

    @abstractmethod
    def list_tasks(
        self,
        assignee_user_id: str | None = None,
        status: str | None = None,
        name: str | None = None,
    ) -> list[Task]:
        raise NotImplementedError

    @abstractmethod
    def update(self, task: Task) -> Task:
        raise NotImplementedError

    @abstractmethod
    def delete(self, task: Task) -> None:
        raise NotImplementedError
