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
        task = Task(
            name=payload.name,
            description=payload.description,
            status="PLANNED",
            estimated_duration_days=payload.estimated_duration_days,
            assignee_user_id=None,
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
        if payload.status == "STARTED":
            # Covers both the first ASSIGNED -> STARTED transition and a FAILED -> STARTED
            # retry, where end_date must be cleared since the task is active again.
            existing.start_date = now
            existing.end_date = None
        elif payload.status in ("DONE", "FAILED"):
            existing.end_date = now

        updated = self.task_repository.update(existing)
        return self._to_read_dto(updated)

    REASSIGNABLE_STATUSES = {"PLANNED", "ASSIGNED"}

    def assign_task(self, task_id: uuid.UUID, assignee_user_id: uuid.UUID) -> TaskReadDTO | None:
        existing = self.task_repository.get_by_id(str(task_id))
        if existing is None:
            return None

        if existing.status not in self.REASSIGNABLE_STATUSES:
            raise ValueError(
                "Only a PLANNED or ASSIGNED task can be (re)assigned through the assignment API; "
                "unassign a STARTED/FAILED task first"
            )

        existing.assignee_user_id = assignee_user_id
        existing.status = "ASSIGNED"
        updated = self.task_repository.update(existing)
        return self._to_read_dto(updated)

    def unassign_task(self, task_id: uuid.UUID) -> TaskReadDTO | None:
        existing = self.task_repository.get_by_id(str(task_id))
        if existing is None:
            return None

        existing.assignee_user_id = None
        if existing.status != "DONE":
            # DONE is a terminal, historical record: detach the owner but keep the
            # completion status and end_date rather than discarding it.
            existing.status = "PLANNED"
            existing.start_date = None
            existing.end_date = None
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
            assignee_user_id=task.assignee_user_id,
        )
