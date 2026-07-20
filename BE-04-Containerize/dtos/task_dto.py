import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class TaskCreateDTO:
    name: str
    description: Optional[str]
    status: str = "PLANNED"
    estimated_duration_days: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    assignee_user_id: Optional[uuid.UUID] = None


@dataclass
class TaskUpdateDTO:
    name: Optional[str] = None
    description: Optional[str] = None
    estimated_duration_days: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


@dataclass
class TaskStatusUpdateDTO:
    status: str


@dataclass
class TaskReadDTO:
    id: uuid.UUID
    name: str
    description: Optional[str]
    status: str
    estimated_duration_days: Optional[int]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    assigned_at: Optional[datetime]
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    failed_at: Optional[datetime]
    assignee_user_id: Optional[uuid.UUID]
