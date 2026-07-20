from sqlalchemy.orm import Session

from models import Task
from repositories.task_repository_port import TaskRepositoryPort


class TaskRepository(TaskRepositoryPort):
    def __init__(self, session: Session):
        self.session = session

    def create(self, task: Task) -> Task:
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def get_by_id(self, task_id: str) -> Task | None:
        return self.session.query(Task).filter(Task.id == task_id).first()

    def list_tasks(
        self,
        assignee_user_id: str | None = None,
        status: str | None = None,
        name: str | None = None,
    ) -> list[Task]:
        query = self.session.query(Task)

        if assignee_user_id is not None:
            query = query.filter(Task.assignee_user_id == assignee_user_id)
        if status is not None:
            query = query.filter(Task.status == status)
        if name is not None:
            query = query.filter(Task.name == name)

        return query.all()

    def update(self, task: Task) -> Task:
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def delete(self, task: Task) -> None:
        self.session.delete(task)
        self.session.commit()
