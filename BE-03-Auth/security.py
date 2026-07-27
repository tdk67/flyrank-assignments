from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from schemas import UserProfile
from supabase_client import supabase

# ---------------------------------------------------------------------------
# Reusable Security Scheme for Swagger UI (HTTPBearer)
# ---------------------------------------------------------------------------
security = HTTPBearer(auto_error=False)


# ---------------------------------------------------------------------------
# Security Guard Dependency: get_current_user
# Can be injected into ANY route function: `current_user: UserProfile = Depends(get_current_user)`
# ---------------------------------------------------------------------------
def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> UserProfile:
    """Verifies the incoming JWT bearer token with Supabase Auth.

    Returns a strongly-typed `UserProfile` object if valid.
    Raises HTTPException(401) if missing, invalid, or expired.
    """
    if not credentials or not credentials.credentials.strip():
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header",
        )

    token = credentials.credentials

    try:
        user_response = supabase.auth.get_user(token)
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )

    if user_response is None or user_response.user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )

    user = user_response.user

    return UserProfile(
        id=str(user.id),
        email=user.email,
        created_at=str(user.created_at),
        token=token,
    )
