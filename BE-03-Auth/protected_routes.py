from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# ---------------------------------------------------------------------------
# Protected router — routes mounted under /protected prefix
# HTTPBearer adds the 'Authorize 🔓' lock button in Swagger UI and tells
# Swagger UI to include the 'Authorization: Bearer <token>' header on requests.
# ---------------------------------------------------------------------------
router = APIRouter(prefix="/protected", tags=["Protected"])
security = HTTPBearer(auto_error=False)


@router.get("/profile", status_code=200)
def get_profile(credentials: HTTPAuthorizationCredentials | None = Depends(security)):
    """Stage 2: Checks if Authorization header is present.

    Does not verify JWT validity yet (that's Stage 3).
    """
    if not credentials or not credentials.credentials.strip():
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header",
        )

    token = credentials.credentials
    return {
        "message": "Access granted (unverified token structure check)",
        "token_snippet": f"{token[:10]}...",
    }
