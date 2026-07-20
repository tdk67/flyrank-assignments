import uuid

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import ErrorResponse, UserCreate, UserRecord

app = FastAPI(
    title="Flyrank BE-04 Containerized User Service",
    description="A containerized FastAPI backend backed by PostgreSQL database.",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Turn Pydantic's validation errors into a short, readable message."""
    messages = []
    for error in exc.errors():
        location = ".".join(str(part) for part in error["loc"] if part != "body")
        messages.append(f"{location}: {error['msg']}" if location else error["msg"])
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "; ".join(messages)},
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get(
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


@app.post(
    "/user",
    response_model=UserRecord,
    status_code=status.HTTP_201_CREATED,
    responses={422: {"model": ErrorResponse, "description": "Invalid request payload"}},
    tags=["users"],
    summary="Create a new user",
)
def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    """Create a user in the database from the payload and return the record."""
    db_user = User(
        first_name=payload.name.first_name,
        last_name=payload.name.last_name,
        email=payload.email,
        telephone=payload.telephone,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get(
    "/user/{user_id}",
    response_model=UserRecord,
    responses={404: {"model": ErrorResponse, "description": "User not found"}},
    tags=["users"],
    summary="Retrieve a user by id",
)
def get_user(user_id: uuid.UUID, db: Session = Depends(get_db)) -> User:
    """Return the user matching `user_id` from the database, or a 404 error if not found."""
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id '{user_id}' not found",
        )
    return db_user
