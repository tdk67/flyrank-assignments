from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status

from database import TaskRepository
from schemas import TaskResponse
from service import TaskNotFoundError, TaskService

# Initialize global repository and service instances
repository = TaskRepository()
service = TaskService(repository=repository)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs database initialization (table creation & JSON seeding if empty)
    repository.init_db()
    yield


app = FastAPI(
    title="Task API with SQLite (BE-02)",
    description="A layered FastAPI task service backed by a SQLite database.",
    version="1.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Routes
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


@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def get_tasks():
    """Fetch all tasks via the Service layer."""
    tasks = service.get_all_tasks()
    return [
        TaskResponse(id=t.id, title=t.title, done=t.done)
        for t in tasks
    ]


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def get_task(task_id: int):
    """Fetch a single task by ID via the Service layer."""
    try:
        t = service.get_task_by_id(task_id)
        return TaskResponse(id=t.id, title=t.title, done=t.done)
    except TaskNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
