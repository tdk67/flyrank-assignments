from contextlib import asynccontextmanager
from fastapi import FastAPI

from database import TaskRepository
from task_routes import router as task_router

repository = TaskRepository()


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
# Core / Health Routes
# ---------------------------------------------------------------------------


@app.get("/")
def read_root():
    return {
        "name": "Task API with SQLite",
        "version": "1.0.0",
        "endpoints": ["/tasks", "/tasks/{id}"]
    }


@app.get("/health")
def health_check():
    return {"status": "ok", "database": "tasks.db"}
