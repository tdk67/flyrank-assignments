import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from dtos.user_dto import UserCreateDTO, UserUpdateDTO
from schemas import ErrorResponse, UserCreate, UserRecord, UserTaskUnassignResponse, UserUpdate
from services.service_factories import get_user_service, get_user_task_service

router = APIRouter(prefix="", tags=["users"])


@router.post(
    "/user",
    response_model=UserRecord,
    status_code=status.HTTP_201_CREATED,
    responses={422: {"model": ErrorResponse, "description": "Invalid request payload"}},
    summary="Create a new user",
)
def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> UserRecord:
    service = get_user_service(db)
    dto = UserCreateDTO(
        first_name=payload.name.first_name,
        last_name=payload.name.last_name,
        email=payload.email,
        telephone=payload.telephone,
    )
    created = service.create_user(dto)
    return UserRecord.model_validate(created)


@router.get(
    "/users",
    response_model=list[UserRecord],
    summary="List users with optional filters",
)
def list_users(
    email: str | None = Query(default=None, description="Filter users by email"),
    first_name: str | None = Query(default=None, description="Filter users by first name"),
    last_name: str | None = Query(default=None, description="Filter users by last name"),
    telephone: str | None = Query(default=None, description="Filter users by telephone number"),
    db: Session = Depends(get_db),
) -> list[UserRecord]:
    service = get_user_service(db)
    users = service.list_users(
        email=email,
        first_name=first_name,
        last_name=last_name,
        telephone=telephone,
    )
    return [UserRecord.model_validate(user) for user in users]


@router.get(
    "/user/{user_id}",
    response_model=UserRecord,
    responses={404: {"model": ErrorResponse, "description": "User not found"}},
    summary="Retrieve a user by id",
)
def get_user(user_id: uuid.UUID, db: Session = Depends(get_db)) -> UserRecord:
    service = get_user_service(db)
    user = service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id '{user_id}' not found",
        )
    return UserRecord.model_validate(user)


@router.patch(
    "/user/{user_id}",
    response_model=UserRecord,
    responses={404: {"model": ErrorResponse, "description": "User not found"}},
    summary="Partially update a user by id",
)
def update_user(user_id: uuid.UUID, payload: UserUpdate, db: Session = Depends(get_db)) -> UserRecord:
    service = get_user_service(db)
    dto = UserUpdateDTO(
        first_name=payload.name.first_name if payload.name is not None else None,
        last_name=payload.name.last_name if payload.name is not None else None,
        email=payload.email,
        telephone=payload.telephone,
    )
    user = service.update_user(user_id, dto)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id '{user_id}' not found",
        )
    return UserRecord.model_validate(user)


@router.post(
    "/users/{user_id}/tasks/unassign",
    response_model=UserTaskUnassignResponse,
    responses={404: {"model": ErrorResponse, "description": "User not found"}},
    summary="Unassign all tasks for a user and reset them to PLANNED",
)
def unassign_user_tasks(user_id: uuid.UUID, db: Session = Depends(get_db)) -> UserTaskUnassignResponse:
    coordinator = get_user_task_service(db)
    updated_count = coordinator.unassign_user_tasks(user_id)
    if updated_count is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id '{user_id}' not found",
        )
    return UserTaskUnassignResponse(unassigned_count=updated_count)


@router.delete(
    "/user/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse, "description": "User not found"}},
    summary="Delete a user by id",
)
def delete_user(user_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    user_service = get_user_service(db)
    coordinator = get_user_task_service(db)

    user = user_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id '{user_id}' not found",
        )

    if coordinator.has_assigned_tasks(user_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with id '{user_id}' still has assigned tasks and cannot be deleted until they are unassigned",
        )

    deleted = user_service.delete_user(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id '{user_id}' not found",
        )
    return None
