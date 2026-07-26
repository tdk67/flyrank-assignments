from contextlib import asynccontextmanager
from fastapi import FastAPI

from database import TaskRepository
from schemas import StatsResponse
from service import TaskService
from task_routes import router as task_router


repository = TaskRepository()
service = TaskService(repository=repository)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs database initialization (table creation & JSON seeding if empty)
    repository.init_db()
    yield


app = FastAPI(
    title="Task API with SQLite (BE-02)",
    description="A modular FastAPI task service backed by a SQLite database.",
    version="1.0.0",
    lifespan=lifespan,
)

# Register domain router
app.include_router(task_router)


# ---------------------------------------------------------------------------
# Core & System Routes
# ---------------------------------------------------------------------------


@app.get("/")
def read_root():
    return {
        "name": "Task API with SQLite",
        "version": "1.0.0",
        "endpoints": ["/tasks", "/tasks/{id}", "/stats"]
    }


@app.get("/health")
def health_check():
    return {"status": "ok", "database": "tasks.db"}


@app.get("/stats", response_model=StatsResponse, tags=["system"], summary="Database statistics")
def get_stats():
    """Return SQLite database table names and row count breakdown."""
    stats = service.get_stats()
    return StatsResponse(
        tables=stats["tables"],
        total_tasks=stats["total_tasks"],
        done_tasks=stats["done_tasks"],
        open_tasks=stats["open_tasks"],
    )

