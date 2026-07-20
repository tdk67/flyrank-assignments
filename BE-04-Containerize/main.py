from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from api.routes.health_routes import router as health_router
from api.routes.task_routes import router as task_router
from api.routes.user_routes import router as user_router

app = FastAPI(
    title="Flyrank BE-04 Containerized User Service",
    description="A containerized FastAPI backend backed by PostgreSQL database.",
    version="1.0.0",
)


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


app.include_router(health_router)
app.include_router(user_router)
app.include_router(task_router)
