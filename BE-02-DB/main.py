import sqlite3
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

# Database file location (saved directly in the BE-02-DB directory)
DB_PATH = Path(__file__).parent / "tasks.db"


def get_db_connection() -> sqlite3.Connection:
    """Helper function to create a database connection with sqlite3.Row row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Initialize SQLite database:
    1. Connect to tasks.db (creates the file if it doesn't exist).
    2. Create the `tasks` table if it doesn't already exist.
    3. Seed 3 initial tasks ONLY if the table is empty (COUNT == 0).
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Step 1: Create the table schema
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0
        )
    """)

    # Step 2: Check if table is empty
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]

    # Step 3: Seed initial data if count is 0
    if count == 0:
        sample_tasks = [
            ("Buy milk", 0),
            ("Clean apartment", 0),
            ("Learn SQLite", 1),
        ]
        cursor.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            sample_tasks
        )
        conn.commit()

    conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Task API with SQLite (BE-02)",
    description="A FastAPI task service backed by a SQLite database.",
    version="1.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------


class TaskResponse(BaseModel):
    id: int
    title: str
    done: bool


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
    """Fetch all tasks from the SQLite database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks")
    rows = cursor.fetchall()
    conn.close()

    return [
        TaskResponse(id=row["id"], title=row["title"], done=bool(row["done"]))
        for row in rows
    ]


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def get_task(task_id: int):
    """Fetch a single task by ID using a parameterized SQL query."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Parameterized query: (task_id,) passed separately to prevent SQL injection
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    return TaskResponse(id=row["id"], title=row["title"], done=bool(row["done"]))
