import uuid

from dtos.task_dto import TaskReadDTO
from services.task_service import TaskService
from services.user_service import UserService


class UserTaskService:
    def __init__(self, user_service: UserService, task_service: TaskService):
        self.user_service = user_service
        self.task_service = task_service

    def assign_user_to_task(self, task_id: uuid.UUID, assignee_user_id: uuid.UUID) -> TaskReadDTO | None:
        user = self.user_service.get_user_by_id(assignee_user_id)
        if user is None:
            return None

        return self.task_service.assign_task(task_id, assignee_user_id)

    def has_assigned_tasks(self, user_id: uuid.UUID) -> bool:
        tasks = self.task_service.list_tasks(assignee_user_id=user_id)
        return len(tasks) > 0

    def unassign_user_tasks(self, user_id: uuid.UUID) -> int | None:
        user = self.user_service.get_user_by_id(user_id)
        if user is None:
            return None

        tasks = self.task_service.list_tasks(assignee_user_id=user_id)
        updated_count = 0

        for task in tasks:
            task = self.task_service.unassign_task(task.id)
            if task is not None:
                updated_count += 1

        return updated_count
