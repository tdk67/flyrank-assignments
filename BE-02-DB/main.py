import sqlite3
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI

# Database file location (saved directly in the BE-02-DB directory)
DB_PATH = Path(__file__).parent / "tasks.db"


def init_db():
    """
    Initialize SQLite database:
    1. Connect to tasks.db (creates the file if it doesn't exist).
    2. Create the `tasks` table if it doesn't already exist.
    3. Seed 3 initial tasks ONLY if the table is empty (COUNT == 0).
    """
    conn = sqlite3.connect(DB_PATH)
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
        # Using parameterized query (?, ?) to safely insert multiple rows
        cursor.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            sample_tasks
        )
        conn.commit()

    conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs when the FastAPI app starts up
    init_db()
    yield
    # Runs when the FastAPI app shuts down (if needed)


app = FastAPI(
    title="Task API with SQLite (BE-02)",
    description="A FastAPI task service backed by a SQLite database.",
    version="1.0.0",
    lifespan=lifespan,
)


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
