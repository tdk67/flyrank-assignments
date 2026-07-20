import uuid
from dataclasses import dataclass
from typing import Optional


@dataclass
class UserCreateDTO:
    first_name: str
    last_name: str
    email: Optional[str]
    telephone: Optional[str]


@dataclass
class UserReadDTO:
    id: uuid.UUID
    first_name: str
    last_name: str
    email: Optional[str]
    telephone: Optional[str]


@dataclass
class UserUpdateDTO:
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None
