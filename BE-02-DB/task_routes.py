from fastapi import APIRouter, HTTPException, status

from database import TaskRepository
from schemas import TaskCreate, TaskResponse, TaskUpdate
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


@router.put("/{task_id}", response_model=TaskResponse, summary="Update task by ID (Full/Partial)")
def update_task(task_id: int, payload: TaskUpdate):
    """Update title and/or done status of an existing task."""
    try:
        t = service.update_task(task_id, payload.title, payload.done)
        return TaskResponse(id=t.id, title=t.title, done=t.done)
    except TaskNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except InvalidTaskError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.patch("/{task_id}", response_model=TaskResponse, summary="Partially update task by ID")
def patch_task(task_id: int, payload: TaskUpdate):
    """Partially update an existing task's title and/or done status."""
    try:
        t = service.update_task(task_id, payload.title, payload.done)
        return TaskResponse(id=t.id, title=t.title, done=t.done)
    except TaskNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except InvalidTaskError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )



@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task by ID",
)
def delete_task(task_id: int):
    """Delete a task by ID from SQLite."""
    try:
        service.delete_task(task_id)
    except TaskNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

