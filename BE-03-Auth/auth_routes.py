import re
from fastapi import APIRouter, Depends, HTTPException
from schemas import AuthCredentials
from security import UserProfile, get_current_user
from supabase_client import supabase

# ---------------------------------------------------------------------------
# Router — all routes here will be mounted under the /auth prefix in main.py
# ---------------------------------------------------------------------------
router = APIRouter(prefix="/auth", tags=["Auth"])


# ---------------------------------------------------------------------------
# Password strength rules (enforced on signup only).
# Each lookahead asserts the presence of one required character class:
#   (?=.*[a-z])  — at least one lowercase letter
#   (?=.*[A-Z])  — at least one uppercase letter
#   (?=.*\d)     — at least one digit
#   (?=.*[...])  — at least one special character
#   .{8,}        — minimum 8 characters total
# ---------------------------------------------------------------------------
PASSWORD_REGEX = re.compile(
    r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};:\'"\\|,.<>\/?]).{8,}$'
)
PASSWORD_RULES_MSG = (
    "Password must be at least 8 characters and include: "
    "one uppercase letter (A-Z), one lowercase letter (a-z), "
    "one digit (0-9), and one special character (!@#$%^&* …)"
)


# ---------------------------------------------------------------------------
# POST /auth/signup
# What happens:
#   1. Validate that email and password are not blank strings
#   2. Call Supabase sign_up() — Supabase stores the user and hashes the password
#   3. Return 201 Created with the new user object
# ---------------------------------------------------------------------------
@router.post("/signup", status_code=201)
def signup(credentials: AuthCredentials):
    # --- Field presence checks (Pydantic catches missing keys; we catch blank strings) ---
    if not credentials.email.strip():
        raise HTTPException(status_code=400, detail="Email is required")
    if not credentials.password.strip():
        raise HTTPException(status_code=400, detail="Password is required")

    # --- Password strength check (signup only) ---
    if not PASSWORD_REGEX.match(credentials.password):
        raise HTTPException(status_code=400, detail=PASSWORD_RULES_MSG)

    try:
        response = supabase.auth.sign_up({
            "email": credentials.email,
            "password": credentials.password,
        })
    except Exception as e:
        # Supabase raises AuthApiError for things like invalid email format,
        # password too short (if Supabase has its own min-length set), etc.
        # Forward the message as a 400 so the client sees a readable error.
        raise HTTPException(status_code=400, detail=str(e))

    # If Supabase returns without error but user is None (edge case), surface it.
    if response.user is None:
        raise HTTPException(status_code=400, detail="Signup failed. Email may already be registered.")

    return {
        "message": "User created successfully",
        "user": {
            "id": str(response.user.id),
            "email": response.user.email,
            "created_at": str(response.user.created_at),
        }
    }


# ---------------------------------------------------------------------------
# POST /auth/login
# What happens:
#   1. Validate non-empty fields
#   2. Call Supabase sign_in_with_password() — Supabase checks the credentials
#   3. Return 200 with the access_token (JWT) and refresh_token
#      The client will use access_token on every subsequent protected request
# ---------------------------------------------------------------------------
@router.post("/login", status_code=200)
def login(credentials: AuthCredentials):
    # At login we only guard against blank strings — strength rules are for signup.
    if not credentials.email.strip():
        raise HTTPException(status_code=400, detail="Email is required")
    if not credentials.password.strip():
        raise HTTPException(status_code=400, detail="Password is required")

    try:
        response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password,
        })
    except Exception:
        # Supabase raises an exception on invalid credentials
        raise HTTPException(status_code=401, detail="Invalid login credentials")

    if response.session is None:
        raise HTTPException(status_code=401, detail="Invalid login credentials")

    return {
        "message": "Login successful",
        "access_token": response.session.access_token,   # <-- this is the JWT
        "refresh_token": response.session.refresh_token,
        "token_type": "bearer",
    }


# ---------------------------------------------------------------------------
# POST /auth/logout
# What happens:
#   1. Requires a valid JWT token via get_current_user dependency
#   2. Calls Supabase sign_out() to end the session
#   3. Returns 204 No Content (empty body)
# ---------------------------------------------------------------------------
@router.post("/logout", status_code=204)
def logout(current_user: UserProfile = Depends(get_current_user)):
    try:
        supabase.auth.sign_out(current_user.token)
    except Exception:
        # Even if Supabase sign_out raises, the client discards its token locally
        pass
    return None
