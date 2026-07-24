from typing import Optional
from pydantic import BaseModel, Field


class TaskResponse(BaseModel):
    """API model returned in HTTP responses."""
    id: int = Field(..., description="Unique task identifier")
    title: str = Field(..., description="Task title/description")
    done: bool = Field(..., description="Task completion status")


class TaskCreate(BaseModel):
    """API model accepted when creating a new task."""
    title: str = Field(..., min_length=1, description="Task title (required, non-empty)")


class TaskUpdate(BaseModel):
    """API model accepted when updating an existing task."""
    title: Optional[str] = Field(None, min_length=1, description="Updated task title")
    done: Optional[bool] = Field(None, description="Updated completion status")
