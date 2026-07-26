from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status

from database import TaskRepository
from schemas import TaskCreate, TaskReplace, TaskResponse, TaskUpdate
from service import InvalidTaskError, TaskNotFoundError, TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])

# Initialize repository and service for task routes
repository = TaskRepository()
service = TaskService(repository=repository)


def _to_task_response(t) -> TaskResponse:
    return TaskResponse(
        id=t.id,
        title=t.title,
        done=t.done,
        created_at=t.created_at,
        updated_at=t.updated_at,
    )


@router.get("", response_model=list[TaskResponse], summary="List all tasks with optional search/filtering")
def get_tasks(
    search: Optional[str] = Query(None, description="Search term to filter task titles (LIKE %search%)"),
    done: Optional[bool] = Query(None, description="Filter by task completion status (true/false)"),
):
    """Fetch all tasks via the Service layer with optional search and completion filters."""
    tasks = service.get_all_tasks(search=search, done=done)
    return [_to_task_response(t) for t in tasks]


@router.get("/{task_id}", response_model=TaskResponse, summary="Get task by ID")
def get_task(task_id: int):
    """Fetch a single task by ID via the Service layer."""
    try:
        t = service.get_task_by_id(task_id)
        return _to_task_response(t)
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
        return _to_task_response(t)
    except InvalidTaskError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.put("/{task_id}", response_model=TaskResponse, summary="Replace task by ID (Full Replacement)")
def update_task(task_id: int, payload: TaskReplace):
    """Replace an existing task's entire state (both title and done are required)."""
    try:
        t = service.replace_task(task_id, payload.title, payload.done)
        return _to_task_response(t)
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
    """Partially update an existing task's title and/or done status (all fields optional)."""
    try:
        t = service.patch_task(task_id, payload.title, payload.done)
        return _to_task_response(t)
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
