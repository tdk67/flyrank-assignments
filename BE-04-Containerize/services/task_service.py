import uuid
from datetime import datetime, timezone

from dtos.task_dto import TaskCreateDTO, TaskReadDTO, TaskStatusUpdateDTO, TaskUpdateDTO
from models import Task
from repositories.task_repository_port import TaskRepositoryPort


class TaskService:
    VALID_STATUSES = {"PLANNED", "ASSIGNED", "STARTED", "DONE", "FAILED"}
    ALLOWED_TRANSITIONS = {
        "PLANNED": {"ASSIGNED"},
        "ASSIGNED": {"STARTED"},
        "STARTED": {"DONE", "FAILED"},
        "FAILED": {"STARTED"},
    }

    def __init__(self, task_repository: TaskRepositoryPort):
        self.task_repository = task_repository

    def create_task(self, payload: TaskCreateDTO) -> TaskReadDTO:
        if payload.status not in self.VALID_STATUSES:
            raise ValueError(f"Unsupported status '{payload.status}'. Allowed statuses: {sorted(self.VALID_STATUSES)}")

        task = Task(
            name=payload.name,
            description=payload.description,
            status=payload.status,
            estimated_duration_days=payload.estimated_duration_days,
            start_date=payload.start_date,
            end_date=payload.end_date,
            assignee_user_id=payload.assignee_user_id,
        )
        created = self.task_repository.create(task)
        return self._to_read_dto(created)

    def get_task_by_id(self, task_id: uuid.UUID) -> TaskReadDTO | None:
        task = self.task_repository.get_by_id(str(task_id))
        if task is None:
            return None
        return self._to_read_dto(task)

    def list_tasks(
        self,
        assignee_user_id: uuid.UUID | None = None,
        status: str | None = None,
        name: str | None = None,
    ) -> list[TaskReadDTO]:
        tasks = self.task_repository.list_tasks(
            assignee_user_id=str(assignee_user_id) if assignee_user_id is not None else None,
            status=status,
            name=name,
        )
        return [self._to_read_dto(task) for task in tasks]

    def update_task(self, task_id: uuid.UUID, payload: TaskUpdateDTO) -> TaskReadDTO | None:
        existing = self.task_repository.get_by_id(str(task_id))
        if existing is None:
            return None

        if payload.name is not None:
            existing.name = payload.name
        if payload.description is not None:
            existing.description = payload.description
        if payload.estimated_duration_days is not None:
            existing.estimated_duration_days = payload.estimated_duration_days
        if payload.start_date is not None:
            existing.start_date = payload.start_date
        if payload.end_date is not None:
            existing.end_date = payload.end_date

        updated = self.task_repository.update(existing)
        return self._to_read_dto(updated)

    def change_status(self, task_id: uuid.UUID, payload: TaskStatusUpdateDTO) -> TaskReadDTO | None:
        existing = self.task_repository.get_by_id(str(task_id))
        if existing is None:
            return None

        if payload.status not in self.VALID_STATUSES:
            raise ValueError(f"Unsupported status '{payload.status}'. Allowed statuses: {sorted(self.VALID_STATUSES)}")

        current_status = existing.status
        if payload.status not in self.ALLOWED_TRANSITIONS.get(current_status, set()):
            raise ValueError(
                f"Invalid status transition '{current_status}' -> '{payload.status}'. "
                "Allowed transitions: PLANNED -> ASSIGNED, ASSIGNED -> STARTED, STARTED -> DONE, STARTED -> FAILED, FAILED -> STARTED"
            )

        now = datetime.now(timezone.utc)
        existing.status = payload.status
        if payload.status == "ASSIGNED":
            existing.assigned_at = now
        elif payload.status == "STARTED":
            existing.started_at = now
        elif payload.status == "DONE":
            existing.finished_at = now
        elif payload.status == "FAILED":
            existing.failed_at = now

        updated = self.task_repository.update(existing)
        return self._to_read_dto(updated)

    def assign_task(self, task_id: uuid.UUID, assignee_user_id: uuid.UUID) -> TaskReadDTO | None:
        existing = self.task_repository.get_by_id(str(task_id))
        if existing is None:
            return None

        if existing.status != "PLANNED":
            raise ValueError("Only a PLANNED task can be assigned through the assignment API")

        existing.assignee_user_id = assignee_user_id
        existing.status = "ASSIGNED"
        existing.assigned_at = datetime.now(timezone.utc)
        updated = self.task_repository.update(existing)
        return self._to_read_dto(updated)

    def unassign_task(self, task_id: uuid.UUID) -> TaskReadDTO | None:
        existing = self.task_repository.get_by_id(str(task_id))
        if existing is None:
            return None

        existing.assignee_user_id = None
        existing.status = "PLANNED"
        existing.assigned_at = None
        existing.started_at = None
        existing.finished_at = None
        existing.failed_at = None
        updated = self.task_repository.update(existing)
        return self._to_read_dto(updated)

    def delete_task(self, task_id: uuid.UUID) -> bool:
        existing = self.task_repository.get_by_id(str(task_id))
        if existing is None:
            return False
        self.task_repository.delete(existing)
        return True

    @staticmethod
    def _to_read_dto(task: Task) -> TaskReadDTO:
        return TaskReadDTO(
            id=task.id,
            name=task.name,
            description=task.description,
            status=task.status,
            estimated_duration_days=task.estimated_duration_days,
            start_date=task.start_date,
            end_date=task.end_date,
            assigned_at=task.assigned_at,
            started_at=task.started_at,
            finished_at=task.finished_at,
            failed_at=task.failed_at,
            assignee_user_id=task.assignee_user_id,
        )
