"""
Flyrank assignment BE-01 - minimal FastAPI user service.

Exposes two endpoints backed by an in-memory store:
    POST /user           - create a user
    GET  /user/{user_id} - fetch a user by id
"""

import uuid
from typing import Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, EmailStr, Field

app = FastAPI(
    title="Flyrank BE-01 User Service",
    description="A minimal FastAPI backend that creates and retrieves users, "
    "keeping all data in memory. Flyrank assignment BE-01.",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class Name(BaseModel):
    """A user's name. Both parts are required when a name is supplied."""

    model_config = ConfigDict(extra="forbid")

    first_name: str = Field(..., min_length=1, description="First name", examples=["Jane"])
    last_name: str = Field(..., min_length=1, description="Last name", examples=["Doe"])


class UserCreate(BaseModel):
    """Payload accepted by POST /user. Only `name` is mandatory."""

    model_config = ConfigDict(extra="forbid")

    name: Name = Field(..., description="User's first and last name (mandatory)")
    email: Optional[EmailStr] = Field(None, description="Email address (optional)")
    telephone: Optional[str] = Field(None, description="Telephone number (optional)")


class UserRecord(UserCreate):
    """A stored user, as returned by both endpoints."""

    id: uuid.UUID = Field(..., description="Server-generated unique user id")


class ErrorResponse(BaseModel):
    detail: str


# ---------------------------------------------------------------------------
# In-memory storage
# ---------------------------------------------------------------------------

users: dict[uuid.UUID, UserRecord] = {}


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Turn Pydantic's validation errors into a short, readable message."""
    messages = []
    for error in exc.errors():
        location = ".".join(str(part) for part in error["loc"] if part != "body")
        messages.append(f"{location}: {error['msg']}" if location else error["msg"])
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "; ".join(messages)},
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.post(
    "/user",
    response_model=UserRecord,
    status_code=status.HTTP_201_CREATED,
    responses={422: {"model": ErrorResponse, "description": "Invalid request payload"}},
    tags=["users"],
    summary="Create a new user",
)
def create_user(payload: UserCreate) -> UserRecord:
    """Create a user from the given payload and return the stored record, including its new id."""
    user_id = uuid.uuid4()
    record = UserRecord(id=user_id, **payload.model_dump())
    users[user_id] = record
    return record


@app.get(
    "/user/{user_id}",
    response_model=UserRecord,
    responses={404: {"model": ErrorResponse, "description": "User not found"}},
    tags=["users"],
    summary="Retrieve a user by id",
)
def get_user(user_id: uuid.UUID) -> UserRecord:
    """Return the user matching `user_id`, or a 404 error if it does not exist."""
    record = users.get(user_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id '{user_id}' not found",
        )
    return record
