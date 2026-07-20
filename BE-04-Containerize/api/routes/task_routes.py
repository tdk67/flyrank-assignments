import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from dtos.task_dto import TaskCreateDTO, TaskStatusUpdateDTO, TaskUpdateDTO
from schemas import ErrorResponse, TaskAssigneeUpdate, TaskCreate, TaskRecord, TaskStatusUpdate, TaskUpdate
from services.service_factories import get_task_service, get_user_task_service

router = APIRouter(prefix="", tags=["tasks"])


@router.post(
    "/task",
    response_model=TaskRecord,
    status_code=status.HTTP_201_CREATED,
    responses={422: {"model": ErrorResponse, "description": "Invalid request payload"}},
    summary="Create a new task",
)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)) -> TaskRecord:
    service = get_task_service(db)
    task = service.create_task(
        TaskCreateDTO(
            name=payload.name,
            description=payload.description,
            estimated_duration_days=payload.estimated_duration_days,
        )
    )
    return TaskRecord.model_validate(task)


@router.get(
    "/tasks",
    response_model=list[TaskRecord],
    summary="List tasks with optional filters",
)
def list_tasks(
    assignee_user_id: uuid.UUID | None = Query(default=None, description="Filter tasks by assignee user id"),
    status: str | None = Query(default=None, description="Filter tasks by status"),
    name: str | None = Query(default=None, description="Filter tasks by name"),
    db: Session = Depends(get_db),
) -> list[TaskRecord]:
    service = get_task_service(db)
    tasks = service.list_tasks(
        assignee_user_id=assignee_user_id,
        status=status,
        name=name,
    )
    return [TaskRecord.model_validate(task) for task in tasks]


@router.get(
    "/task/{task_id}",
    response_model=TaskRecord,
    responses={404: {"model": ErrorResponse, "description": "Task not found"}},
    summary="Retrieve a task by id",
)
def get_task(task_id: uuid.UUID, db: Session = Depends(get_db)) -> TaskRecord:
    service = get_task_service(db)
    task = service.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id '{task_id}' not found",
        )
    return TaskRecord.model_validate(task)


@router.patch(
    "/task/{task_id}",
    response_model=TaskRecord,
    responses={404: {"model": ErrorResponse, "description": "Task not found"}},
    summary="Partially update a task by id",
)
def update_task(task_id: uuid.UUID, payload: TaskUpdate, db: Session = Depends(get_db)) -> TaskRecord:
    service = get_task_service(db)
    dto = TaskUpdateDTO(
        name=payload.name,
        description=payload.description,
        estimated_duration_days=payload.estimated_duration_days,
    )
    task = service.update_task(task_id, dto)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id '{task_id}' not found",
        )
    return TaskRecord.model_validate(task)


@router.patch(
    "/task/{task_id}/status",
    response_model=TaskRecord,
    responses={404: {"model": ErrorResponse, "description": "Task not found"}},
    summary="Change task status through the lifecycle state machine",
)
def change_status(task_id: uuid.UUID, payload: TaskStatusUpdate, db: Session = Depends(get_db)) -> TaskRecord:
    service = get_task_service(db)
    try:
        task = service.change_status(task_id, TaskStatusUpdateDTO(status=payload.status))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id '{task_id}' not found",
        )

    return TaskRecord.model_validate(task)


@router.patch(
    "/task/{task_id}/assignee",
    response_model=TaskRecord,
    responses={
        404: {"model": ErrorResponse, "description": "Task not found or assignee user does not exist"},
        409: {"model": ErrorResponse, "description": "Task status does not allow (re)assignment"},
    },
    summary="Assign or reassign a task to a user",
)
def assign_task(task_id: uuid.UUID, payload: TaskAssigneeUpdate, db: Session = Depends(get_db)) -> TaskRecord:
    coordinator = get_user_task_service(db)

    try:
        task = coordinator.assign_user_to_task(task_id, payload.assignee_user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id '{task_id}' not found or assignee user '{payload.assignee_user_id}' does not exist",
        )
    return TaskRecord.model_validate(task)


@router.delete(
    "/task/{task_id}/assignee",
    response_model=TaskRecord,
    responses={404: {"model": ErrorResponse, "description": "Task not found"}},
    summary="Deassign a task, returning it to PLANNED",
)
def deassign_task(task_id: uuid.UUID, db: Session = Depends(get_db)) -> TaskRecord:
    service = get_task_service(db)
    task = service.unassign_task(task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id '{task_id}' not found",
        )
    return TaskRecord.model_validate(task)


@router.delete(
    "/task/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse, "description": "Task not found"}},
    summary="Delete a task by id",
)
def delete_task(task_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    service = get_task_service(db)
    deleted = service.delete_task(task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id '{task_id}' not found",
        )
    return None
