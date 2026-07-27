from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Signup & Login Request Schema
# Pydantic validates field existence automatically when JSON is parsed.
# ---------------------------------------------------------------------------
class AuthCredentials(BaseModel):
    email: str
    password: str


# ---------------------------------------------------------------------------
# Strongly-Typed Authenticated User DTO
# Provides clean dot-notation (user.email), type checking, and IDE autocomplete.
# ---------------------------------------------------------------------------
class UserProfile(BaseModel):
    id: str
    email: str
    created_at: str
    token: str
