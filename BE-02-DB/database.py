import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "tasks.db"
SAMPLE_DATA_PATH = BASE_DIR / "sample_data.json"
MIGRATIONS_DIR = BASE_DIR / "migrations"


@dataclass
class TaskDTO:
    """Database Transfer Object representing a task record in SQLite."""
    id: int
    title: str
    done: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class TaskRepository:
    """Repository layer responsible for direct database interactions and versioned schema migrations."""

    def __init__(self, db_path: Path = DB_PATH, migrations_dir: Path = MIGRATIONS_DIR):
        self.db_path = db_path
        self.migrations_dir = migrations_dir

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def run_migrations(self) -> None:
        """
        Version-based database migration runner:
        1. Ensures `schema_migrations` tracking table exists.
        2. Scans `migrations/*.sql` files sorted by filename.
        3. Executes unapplied migration scripts in a transaction and records their version.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Step 1: Create tracking table for applied migrations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                filename TEXT NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

        # Step 2: Fetch already applied migration versions
        cursor.execute("SELECT version FROM schema_migrations")
        applied_versions = {row["version"] for row in cursor.fetchall()}

        # Step 3: Find and apply pending .sql migration files
        if self.migrations_dir.exists():
            migration_files = sorted(self.migrations_dir.glob("*.sql"))

            for file_path in migration_files:
                # Extract numeric version from prefix (e.g., '001' from '001_create_tasks_table.sql')
                version_str = file_path.name.split("_")[0]
                if version_str.isdigit():
                    version = int(version_str)
                    if version not in applied_versions:
                        with open(file_path, "r", encoding="utf-8") as f:
                            sql_script = f.read()

                        # Execute script and record version in a transaction
                        conn.executescript(sql_script)
                        cursor.execute(
                            "INSERT INTO schema_migrations (version, filename) VALUES (?, ?)",
                            (version, file_path.name)
                        )
                        conn.commit()

        conn.close()

    def init_db(self) -> None:
        """Run pending schema migrations and seed initial data if tasks table is empty."""
        # Step 1: Run versioned migrations
        self.run_migrations()

        # Step 2: Check if table needs seeding
        conn = self._get_connection()
        cursor = conn.cursor()

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
                "INSERT INTO tasks (title, done, created_at, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)",
                task_records
            )
            conn.commit()

        conn.close()


    def get_all(
        self,
        search: Optional[str] = None,
        done: Optional[bool] = None,
    ) -> list[TaskDTO]:
        """Fetch tasks with optional search and done filter."""
        conn = self._get_connection()
        cursor = conn.cursor()

        query = "SELECT id, title, done, created_at, updated_at FROM tasks"
        conditions = []
        params = []

        if search is not None and search.strip():
            conditions.append("title LIKE ?")
            params.append(f"%{search.strip()}%")

        if done is not None:
            conditions.append("done = ?")
            params.append(1 if done else 0)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        conn.close()

        keys = rows[0].keys() if rows else []

        return [
            TaskDTO(
                id=row["id"],
                title=row["title"],
                done=bool(row["done"]),
                created_at=row["created_at"] if "created_at" in keys else None,
                updated_at=row["updated_at"] if "updated_at" in keys else None,
            )
            for row in rows
        ]

    def get_by_id(self, task_id: int) -> Optional[TaskDTO]:
        """Fetch a single task record by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, done, created_at, updated_at FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()

        if row is None:
            return None

        keys = row.keys()

        return TaskDTO(
            id=row["id"],
            title=row["title"],
            done=bool(row["done"]),
            created_at=row["created_at"] if "created_at" in keys else None,
            updated_at=row["updated_at"] if "updated_at" in keys else None,
        )

    def create(self, title: str) -> TaskDTO:
        """Insert a new task into the database and return created TaskDTO."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, done, created_at, updated_at) VALUES (?, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)",
            (title,)
        )
        conn.commit()
        new_id = cursor.lastrowid


        cursor.execute("SELECT id, title, done, created_at, updated_at FROM tasks WHERE id = ?", (new_id,))
        row = cursor.fetchone()
        conn.close()

        keys = row.keys()

        return TaskDTO(
            id=row["id"],
            title=row["title"],
            done=bool(row["done"]),
            created_at=row["created_at"] if "created_at" in keys else None,
            updated_at=row["updated_at"] if "updated_at" in keys else None,
        )

    def update(self, task_id: int, title: str, done: bool) -> Optional[TaskDTO]:
        """Update task title/done and refresh updated_at timestamp."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE tasks
            SET title = ?, done = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (title, 1 if done else 0, task_id))
        conn.commit()

        if cursor.rowcount == 0:
            conn.close()
            return None

        cursor.execute("SELECT id, title, done, created_at, updated_at FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()

        keys = row.keys()

        return TaskDTO(
            id=row["id"],
            title=row["title"],
            done=bool(row["done"]),
            created_at=row["created_at"] if "created_at" in keys else None,
            updated_at=row["updated_at"] if "updated_at" in keys else None,
        )

    def delete(self, task_id: int) -> bool:
        """Delete a task record by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()

        return rows_affected > 0

    def get_stats(self) -> dict:
        """Query database table names, row counts, and status breakdown."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row["name"] for row in cursor.fetchall()]

        cursor.execute("SELECT COUNT(*) FROM tasks")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM tasks WHERE done = 1")
        done_count = cursor.fetchone()[0]

        open_count = total - done_count
        conn.close()

        return {
            "tables": tables,
            "total_tasks": total,
            "done_tasks": done_count,
            "open_tasks": open_count,
        }
