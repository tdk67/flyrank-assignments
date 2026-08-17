import sqlite3
import pytest
from pathlib import Path
from config import config, AppConfig
from db import get_db_connection, verify_database
from setup_db import run_db_setup


def test_config_loading():
    """Verify config loads dynamically from config.json without hardcoded values."""
    assert isinstance(config.db_path, str) and len(config.db_path) > 0
    assert config.resolve("db_path").is_absolute()
    assert config.resolve("reports_dir").is_absolute()
    assert config.resolve("templates_dir").is_absolute()


def test_missing_db_file_raises_readable_error(tmp_path):
    """Verify human-readable FileNotFoundError when DB file does not exist."""
    fake_db = tmp_path / "non_existent.db"
    with pytest.raises(FileNotFoundError) as exc_info:
        get_db_connection(db_path=fake_db)
    assert "❌ Database Error: Database file does not exist" in str(exc_info.value)


def test_missing_books_table_raises_readable_error(tmp_path):
    """Verify human-readable RuntimeError when 'books' table is missing."""
    empty_db = tmp_path / "empty.db"
    # Create empty sqlite file without tables
    conn = sqlite3.connect(empty_db)
    conn.close()

    with pytest.raises(RuntimeError) as exc_info:
        get_db_connection(db_path=empty_db)
    assert "❌ Database Error: Mandatory table 'books' is missing" in str(exc_info.value)


def test_setup_db_and_verification():
    """Verify setup_db script creates reports table and indexes on existing DB."""
    run_db_setup()
    count = verify_database()
    assert count > 0

    # Verify tables and indexes exist
    conn = get_db_connection()
    cursor = conn.cursor()

    tables = [row["name"] for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
    assert "books" in tables
    assert "reports" in tables

    indexes = [row["name"] for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='index';").fetchall()]
    assert "idx_books_category" in indexes
    assert "idx_books_rating" in indexes
    assert "idx_books_price" in indexes
    conn.close()
