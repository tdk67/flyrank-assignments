import sqlite3
import logging
from pathlib import Path
from config import config

logger = logging.getLogger("be08.db")


def get_db_connection(db_path: Path = None) -> sqlite3.Connection:
    """
    Returns a SQLite connection with dict-like row access.
    Fails fast with human-readable error messages if DB file or required tables do not exist.
    No automatic schema mutations are performed here.
    """
    target_path = db_path or config.resolve("db_path")

    if not target_path.exists():
        raise FileNotFoundError(
            f"❌ Database Error: Database file does not exist at '{target_path}'. "
            f"Please verify 'db_path' in 'config.json'."
        )

    conn = sqlite3.connect(target_path)
    conn.row_factory = sqlite3.Row

    # Verify 'books' table existence
    cursor = conn.cursor()
    books_check = cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='books';"
    ).fetchone()

    if not books_check:
        conn.close()
        raise RuntimeError(
            f"❌ Database Error: Mandatory table 'books' is missing from database '{target_path}'. "
            f"Please run 'python setup_db.py' or ensure BE-06 scraper DB is available."
        )

    return conn


def verify_database(db_path: Path = None) -> int:
    """Verifies DB connection and returns total book count."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    count = cursor.execute("SELECT COUNT(*) as cnt FROM books").fetchone()["cnt"]
    conn.close()
    return count


if __name__ == "__main__":
    count = verify_database()
    print("[OK] Database Verification Successful!")
    print(f"     Database Path: {config.resolve('db_path')}")
    print(f"     Books Count:   {count}")
