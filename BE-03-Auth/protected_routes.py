from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase_client import supabase

# ---------------------------------------------------------------------------
# Protected router — routes mounted under /protected prefix
# HTTPBearer adds the 'Authorize 🔓' lock button in Swagger UI and tells
# Swagger UI to include the 'Authorization: Bearer <token>' header on requests.
# ---------------------------------------------------------------------------
router = APIRouter(prefix="/protected", tags=["Protected"])
security = HTTPBearer(auto_error=False)


@router.get("/profile", status_code=200)
def get_profile(credentials: HTTPAuthorizationCredentials | None = Depends(security)):
    """Stage 3: Real JWT token verification with Supabase.

    Calls `supabase.auth.get_user(token)` to verify the JWT signature and expiry.
    Returns 401 if missing, expired, or tampered.
    Returns user details (id, email, created_at) on success.
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
        # Supabase raises an error if the JWT signature is invalid, tampered, or expired
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

    return {
        "message": "Token verified successfully",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "created_at": str(user.created_at),
        },
    }
