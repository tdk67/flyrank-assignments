from fastapi import APIRouter, HTTPException, status

from database import TaskRepository
from schemas import TaskCreate, TaskResponse
from service import InvalidTaskError, TaskNotFoundError, TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])

# Initialize repository and service for task routes
repository = TaskRepository()
service = TaskService(repository=repository)


@router.get("", response_model=list[TaskResponse], summary="List all tasks")
def get_tasks():
    """Fetch all tasks via the Service layer."""
    tasks = service.get_all_tasks()
    return [
        TaskResponse(id=t.id, title=t.title, done=t.done)
        for t in tasks
    ]


@router.get("/{task_id}", response_model=TaskResponse, summary="Get task by ID")
def get_task(task_id: int):
    """Fetch a single task by ID via the Service layer."""
    try:
        t = service.get_task_by_id(task_id)
        return TaskResponse(id=t.id, title=t.title, done=t.done)
    except TaskNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
)
def create_task(payload: TaskCreate):
    """Create a new task in SQLite with default done=False."""
    try:
        t = service.create_task(payload.title)
        return TaskResponse(id=t.id, title=t.title, done=t.done)
    except InvalidTaskError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
