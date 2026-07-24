import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "tasks.db"
SAMPLE_DATA_PATH = BASE_DIR / "sample_data.json"


@dataclass
class TaskDTO:
    """Database Transfer Object representing a task record in SQLite."""
    id: int
    title: str
    done: bool


class TaskRepository:
    """Repository layer responsible for all direct database interactions."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        """Create tasks table if not exists and seed initial data from sample_data.json if empty."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0
            )
        """)

        cursor.execute("SELECT COUNT(*) FROM tasks")
        count = cursor.fetchone()[0]

        if count == 0 and SAMPLE_DATA_PATH.exists():
            with open(SAMPLE_DATA_PATH, "r", encoding="utf-8") as f:
                sample_tasks = json.load(f)

            task_records = [
                (task["title"], 1 if task.get("done", False) else 0)
                for task in sample_tasks
            ]

            cursor.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                task_records
            )
            conn.commit()

        conn.close()

    def get_all(self) -> list[TaskDTO]:
        """Fetch all task records from the database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, done FROM tasks")
        rows = cursor.fetchall()
        conn.close()

        return [
            TaskDTO(id=row["id"], title=row["title"], done=bool(row["done"]))
            for row in rows
        ]

    def get_by_id(self, task_id: int) -> Optional[TaskDTO]:
        """Fetch a single task record by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()

        if row is None:
            return None

        return TaskDTO(id=row["id"], title=row["title"], done=bool(row["done"]))
