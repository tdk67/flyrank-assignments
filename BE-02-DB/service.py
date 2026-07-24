from typing import Optional
from database import TaskDTO, TaskRepository


class TaskNotFoundError(Exception):
    """Domain exception raised when a requested task is not found."""
    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f"Task with id {task_id} not found")


class TaskService:
    """Service layer containing business logic and coordinating with the repository."""

    def __init__(self, repository: Optional[TaskRepository] = None):
        self.repository = repository or TaskRepository()

    def get_all_tasks(self) -> list[TaskDTO]:
        """Retrieve all tasks."""
        return self.repository.get_all()

    def get_task_by_id(self, task_id: int) -> TaskDTO:
        """Retrieve a task by ID or raise TaskNotFoundError."""
        task = self.repository.get_by_id(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task
