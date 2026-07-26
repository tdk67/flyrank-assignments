from typing import Optional
from pydantic import BaseModel, Field


class TaskResponse(BaseModel):
    """API model returned in HTTP responses."""
    id: int = Field(..., description="Unique task identifier")
    title: str = Field(..., description="Task title/description")
    done: bool = Field(..., description="Task completion status")
    created_at: Optional[str] = Field(None, description="Task creation timestamp")
    updated_at: Optional[str] = Field(None, description="Task last update timestamp")



class TaskCreate(BaseModel):
    """API model accepted when creating a new task."""
    title: str = Field(..., min_length=1, description="Task title (required, non-empty)")


class TaskReplace(BaseModel):
    """API model accepted by PUT /tasks/{id} for full resource replacement (both title & done required)."""
    title: str = Field(..., min_length=1, description="Full replacement task title")
    done: bool = Field(..., description="Full replacement completion status")


class TaskUpdate(BaseModel):
    """API model accepted by PATCH /tasks/{id} for partial updates (all fields optional)."""
    title: Optional[str] = Field(None, min_length=1, description="Updated task title")
    done: Optional[bool] = Field(None, description="Updated completion status")



class StatsResponse(BaseModel):
    """API model returned by GET /stats endpoint."""
    tables: list[str] = Field(..., description="List of user tables in SQLite database")
    total_tasks: int = Field(..., description="Total row count in tasks table")
    done_tasks: int = Field(..., description="Count of completed tasks")
    open_tasks: int = Field(..., description="Count of open tasks")

