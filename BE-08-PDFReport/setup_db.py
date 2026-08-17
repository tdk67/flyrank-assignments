"""
Standalone Database Setup & Maintenance Script.
Runs once outside of the main application to create the reports metadata tracking table
and performance indexes on the books table.
"""
import sqlite3
import sys
from pathlib import Path
from config import config


def run_db_setup(db_path: Path = None):
    target_path = db_path or config.resolve("db_path")

    if not target_path.exists():
        print(f"❌ Error: Database file does not exist at '{target_path}'!")
        print("   Please ensure BE-06-Scraper has generated 'flyrank_scraper.db'.")
        sys.exit(1)

    conn = sqlite3.connect(target_path)
    cursor = conn.cursor()

    # 1. Verify 'books' table exists
    books_check = cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='books';"
    ).fetchone()

    if not books_check:
        print(f"❌ Error: Mandatory table 'books' is missing from database '{target_path}'!")
        conn.close()
        sys.exit(1)

    # 2. Create 'reports' tracking table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id TEXT PRIMARY KEY,
            report_date TEXT NOT NULL,
            file_path TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 3. Add Performance Indexes for scaling queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_books_category ON books(category);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_books_rating ON books(rating);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_books_price ON books(price_incl_tax DESC);")

    conn.commit()

    # Fetch count
    books_count = cursor.execute("SELECT COUNT(*) FROM books;").fetchone()[0]
    conn.close()

    print("[OK] Database Setup Completed Successfully!")
    print(f"     Database File: {target_path}")
    print(f"     Books Count:   {books_count} rows")
    print("     Tables:        books, reports")
    print("     Indexes:       idx_books_category, idx_books_rating, idx_books_price")


if __name__ == "__main__":
    run_db_setup()
