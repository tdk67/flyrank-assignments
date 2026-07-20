import uuid
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


class ErrorResponse(BaseModel):
    detail: str
