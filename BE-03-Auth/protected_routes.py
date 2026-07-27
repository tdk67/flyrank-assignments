from fastapi import APIRouter, Depends
from schemas import UserProfile
from security import get_current_user

# ---------------------------------------------------------------------------
# Protected router — routes mounted under /protected prefix
# All endpoints use the reusable `get_current_user` dependency from deps.py
# ---------------------------------------------------------------------------
router = APIRouter(prefix="/protected", tags=["Protected"])


@router.get("/profile", status_code=200)
def get_profile(current_user: UserProfile = Depends(get_current_user)):
    """Protected profile endpoint — uses strongly-typed UserProfile dependency."""
    return {
        "message": "Profile details retrieved successfully",
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "created_at": current_user.created_at,
        },
    }


@router.get("/dashboard", status_code=200)
def get_dashboard(current_user: UserProfile = Depends(get_current_user)):
    """Protected dashboard endpoint — uses the exact same dependency with zero duplicate auth code!"""
    return {
        "message": f"Welcome to your dashboard, {current_user.email}!",
        "stats": {
            "tasks_completed": 12,
            "account_status": "Active",
            "user_id": current_user.id,
        },
    }
