from typing import Optional
from database import TaskDTO, TaskRepository


class TaskNotFoundError(Exception):
    """Domain exception raised when a requested task is not found."""
    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f"Task with id {task_id} not found")


class InvalidTaskError(Exception):
    """Domain exception raised when task creation or validation fails."""
    pass


class TaskService:
    """Service layer containing business logic and coordinating with the repository."""

    def __init__(self, repository: Optional[TaskRepository] = None):
        self.repository = repository or TaskRepository()

    def get_all_tasks(
        self,
        search: Optional[str] = None,
        done: Optional[bool] = None,
    ) -> list[TaskDTO]:
        """Retrieve all tasks with optional search (LIKE) and completion status filters."""
        return self.repository.get_all(search=search, done=done)

    def get_stats(self) -> dict:
        """Retrieve database statistics (tables and row count breakdown)."""
        return self.repository.get_stats()


    def get_task_by_id(self, task_id: int) -> TaskDTO:
        """Retrieve a task by ID or raise TaskNotFoundError."""
        task = self.repository.get_by_id(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    def create_task(self, title: str) -> TaskDTO:
        """Validate input title and create a new task."""
        if not title or not title.strip():
            raise InvalidTaskError("Title is required and cannot be empty")
        return self.repository.create(title.strip())

    def replace_task(self, task_id: int, title: str, done: bool) -> TaskDTO:
        """Full replacement (PUT): Replaces the entire task state with the new title and done status."""
        self.get_task_by_id(task_id)  # Raises TaskNotFoundError if missing

        if not title or not title.strip():
            raise InvalidTaskError("Title is required and cannot be empty")

        updated = self.repository.update(task_id, title.strip(), done)
        if updated is None:
            raise TaskNotFoundError(task_id)

        return updated

    def patch_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        done: Optional[bool] = None,
    ) -> TaskDTO:
        """Partial update (PATCH): Updates only the fields provided, leaving unsupplied fields unchanged."""
        existing = self.get_task_by_id(task_id)  # Raises TaskNotFoundError if missing

        new_title = existing.title
        if title is not None:
            if not title.strip():
                raise InvalidTaskError("Title cannot be empty")
            new_title = title.strip()

        new_done = existing.done if done is None else done

        updated = self.repository.update(task_id, new_title, new_done)
        if updated is None:
            raise TaskNotFoundError(task_id)

        return updated


    def delete_task(self, task_id: int) -> None:
        """Delete a task by ID or raise TaskNotFoundError."""
        deleted = self.repository.delete(task_id)
        if not deleted:
            raise TaskNotFoundError(task_id)


