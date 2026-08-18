"""
Health Check Router.
Handles HTTP GET /health requests.
"""
from fastapi import APIRouter
from schemas import HealthResponse
from services import report_service

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health_check():
    """Minimal health check endpoint to verify server setup and DB connectivity."""
    return report_service.get_health_status()
