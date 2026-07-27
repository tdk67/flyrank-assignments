from fastapi import APIRouter

# ---------------------------------------------------------------------------
# Public router — routes mounted under /public prefix (no authentication needed)
# ---------------------------------------------------------------------------
router = APIRouter(prefix="/public", tags=["Public"])


@router.get("/info", status_code=200)
def public_info():
    return {
        "message": "Welcome to the public endpoint! No authentication required.",
        "status": "online",
    }
