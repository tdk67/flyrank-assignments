import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class Name(BaseModel):
    model_config = ConfigDict(extra="forbid")

    first_name: str = Field(..., min_length=1, description="First name", examples=["Jane"])
    last_name: str = Field(..., min_length=1, description="Last name", examples=["Doe"])


class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Name = Field(..., description="User's first and last name (mandatory)")
    email: Optional[EmailStr] = Field(None, description="Email address (optional)")
    telephone: Optional[str] = Field(None, description="Telephone number (optional)")


class UserRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Server-generated unique user id")
    name: Name = Field(..., description="User's first and last name (mandatory)")
    email: Optional[EmailStr] = Field(None, description="Email address (optional)")
    telephone: Optional[str] = Field(None, description="Telephone number (optional)")

    @model_validator(mode="before")
    @classmethod
    def construct_name(cls, data: Any) -> Any:
        """Translate flat database structure (first_name/last_name) to nested Pydantic structure (name)."""
        # If input is a dictionary
        if isinstance(data, dict):
            if "name" not in data and "first_name" in data and "last_name" in data:
                data = dict(data)
                data["name"] = {
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                }
            return data

        # If input is a database model (ORM object)
        if hasattr(data, "first_name") and hasattr(data, "last_name"):
            return {
                "id": getattr(data, "id"),
                "name": {
                    "first_name": getattr(data, "first_name"),
                    "last_name": getattr(data, "last_name"),
                },
                "email": getattr(data, "email", None),
                "telephone": getattr(data, "telephone", None),
            }

        return data


class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Optional[Name] = Field(None, description="User's first and last name")
    email: Optional[EmailStr] = Field(None, description="Email address (optional)")
    telephone: Optional[str] = Field(None, description="Telephone number (optional)")


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        ...,
        min_length=1,
        description="Task name",
        examples=["Prepare sprint backlog"],
    )
    description: Optional[str] = Field(
        None,
        description="Task description",
        examples=["Draft the backlog for the next sprint"],
    )


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Optional[str] = Field(None, description="Task name")
    description: Optional[str] = Field(None, description="Task description")
    estimated_duration_days: Optional[int] = Field(None, description="Estimated duration in days")
    start_date: Optional[datetime] = Field(None, description="Task start timestamp")
    end_date: Optional[datetime] = Field(None, description="Task end timestamp")


class TaskStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = Field(
        ...,
        description="New task status",
        examples=["STARTED"],
    )


class TaskAssigneeUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    assignee_user_id: uuid.UUID = Field(
        ...,
        description="Assigned user id",
        examples=["c3b9a7a9-91c6-43b6-9812-a16fbd4c6a6f"],
    )


class UserTaskUnassignResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    unassigned_count: int = Field(
        ...,
        description="Number of assigned tasks reset to PLANNED",
        examples=[2],
    )


class TaskRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Server-generated unique task id")
    name: str = Field(..., description="Task name")
    description: Optional[str] = Field(None, description="Task description")
    status: str = Field(..., description="Task status")
    estimated_duration_days: Optional[int] = Field(None, description="Estimated duration in days")
    start_date: Optional[datetime] = Field(None, description="Task start timestamp")
    end_date: Optional[datetime] = Field(None, description="Task end timestamp")
    assigned_at: Optional[datetime] = Field(None, description="Timestamp when the task was assigned")
    started_at: Optional[datetime] = Field(None, description="Timestamp when the task started")
    finished_at: Optional[datetime] = Field(None, description="Timestamp when the task finished")
    failed_at: Optional[datetime] = Field(None, description="Timestamp when the task failed")
    assignee_user_id: Optional[uuid.UUID] = Field(None, description="Assigned user id")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "00000000-0000-0000-0000-000000000000",
                "name": "Prepare sprint backlog",
                "description": "Draft the backlog for the next sprint",
                "status": "PLANNED",
                "estimated_duration_days": None,
                "start_date": None,
                "end_date": None,
                "assigned_at": None,
                "started_at": None,
                "finished_at": None,
                "failed_at": None,
                "assignee_user_id": None,
            }
        },
    )


class ErrorResponse(BaseModel):
    detail: str
