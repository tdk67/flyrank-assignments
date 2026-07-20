from sqlalchemy.orm import Session

from repositories.task_repository import TaskRepository
from repositories.user_repository import UserRepository
from services.task_service import TaskService
from services.user_service import UserService
from services.user_task_service import UserTaskService


def get_user_service(db: Session) -> UserService:
    return UserService(UserRepository(db))


def get_task_service(db: Session) -> TaskService:
    return TaskService(TaskRepository(db))


def get_user_task_service(db: Session) -> UserTaskService:
    return UserTaskService(
        user_service=get_user_service(db),
        task_service=get_task_service(db),
    )
