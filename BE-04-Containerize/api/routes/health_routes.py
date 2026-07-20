from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db
from schemas import ErrorResponse

router = APIRouter(tags=["monitoring"])


@router.get(
    "/health",
    tags=["monitoring"],
    summary="Perform a system health check",
    responses={
        200: {"description": "System is healthy"},
        503: {"model": ErrorResponse, "description": "Database connection unhealthy"},
    },
)
def health_check(db: Session = Depends(get_db)):
    """Ping the database to verify it is healthy and responsive."""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}",
        )
