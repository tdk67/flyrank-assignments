"""
Database Repository Layer.
Contains ALL SQL statements and raw database query operations.
This isolates persistence logic completely from business services and HTTP routers.
"""
import sqlite3
from datetime import datetime
from typing import Dict, Any, List, Optional


def get_books_count(conn: sqlite3.Connection) -> int:
    """Query total number of records in books table."""
    cursor = conn.cursor()
    row = cursor.execute("SELECT COUNT(*) as cnt FROM books;").fetchone()
    return row["cnt"] if row else 0


def fetch_report_aggregations(conn: sqlite3.Connection, limit: int) -> Dict[str, Any]:
    """Execute high-performance SQL aggregation queries for the executive report."""
    cursor = conn.cursor()

    # 1. Summary KPIs
    summary_row = cursor.execute("""
        SELECT 
            COUNT(*) as total_books,
            COALESCE(AVG(price_incl_tax), 0.0) as avg_price,
            COALESCE(SUM(stock_quantity), 0) as total_stock,
            COALESCE(SUM(price_incl_tax * stock_quantity), 0.0) as total_value
        FROM books;
    """).fetchone()

    total_books = summary_row["total_books"] if summary_row else 0
    summary = {
        "total_books": total_books,
        "avg_price": round(summary_row["avg_price"], 2) if summary_row else 0.0,
        "total_stock": summary_row["total_stock"] if summary_row else 0,
        "total_value": round(summary_row["total_value"], 2) if summary_row else 0.0
    }

    # 2. Rating Breakdown
    rating_rows = cursor.execute("""
        SELECT 
            rating, 
            COUNT(*) as book_count, 
            COALESCE(AVG(price_incl_tax), 0.0) as avg_price
        FROM books
        GROUP BY rating
        ORDER BY rating DESC;
    """).fetchall()

    rating_breakdown = [
        {
            "rating": r["rating"],
            "count": r["book_count"],
            "avg_price": round(r["avg_price"], 2)
        }
        for r in rating_rows
    ]

    # 3. Category Breakdown
    category_rows = cursor.execute("""
        SELECT 
            category, 
            COUNT(*) as book_count, 
            COALESCE(SUM(stock_quantity), 0) as total_stock,
            COALESCE(AVG(price_incl_tax), 0.0) as avg_price
        FROM books
        GROUP BY category
        ORDER BY book_count DESC;
    """).fetchall()

    category_breakdown = [
        {
            "category": c["category"],
            "count": c["book_count"],
            "total_stock": c["total_stock"],
            "avg_price": round(c["avg_price"], 2)
        }
        for c in category_rows
    ]

    # 4. Top 5 Most Expensive Books
    top_5_rows = cursor.execute("""
        SELECT upc, title, category, price_incl_tax, rating, stock_quantity
        FROM books
        ORDER BY price_incl_tax DESC
        LIMIT 5;
    """).fetchall()

    top_5_expensive = [
        {
            "upc": row["upc"],
            "title": row["title"],
            "category": row["category"],
            "price": round(row["price_incl_tax"], 2),
            "rating": row["rating"],
            "stock": row["stock_quantity"]
        }
        for row in top_5_rows
    ]

    # 5. Catalog Books Query (Capped by limit)
    all_rows = cursor.execute("""
        SELECT upc, title, category, price_incl_tax, rating, stock_quantity
        FROM books
        ORDER BY title ASC
        LIMIT ?;
    """, (limit,)).fetchall()

    all_books = [
        {
            "upc": row["upc"],
            "title": row["title"],
            "category": row["category"],
            "price": round(row["price_incl_tax"], 2),
            "rating": row["rating"],
            "stock": row["stock_quantity"]
        }
        for row in all_rows
    ]

    is_truncated = total_books > len(all_books)

    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "summary": summary,
        "rating_breakdown": rating_breakdown,
        "category_breakdown": category_breakdown,
        "top_5_expensive": top_5_expensive,
        "all_books": all_books,
        "catalog_limit": limit,
        "is_truncated": is_truncated
    }


def find_latest_report_by_date(conn: sqlite3.Connection, report_date: str) -> Optional[Dict[str, Any]]:
    """Retrieve the most recent report record generated on a given date."""
    cursor = conn.cursor()
    row = cursor.execute(
        "SELECT id, report_date, file_path, created_at FROM reports WHERE report_date = ? ORDER BY created_at DESC LIMIT 1;",
        (report_date,)
    ).fetchone()
    return dict(row) if row else None


def insert_report_record(conn: sqlite3.Connection, report_id: str, report_date: str, file_path: str, created_at: str):
    """Insert a new report metadata tracking record."""
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO reports (id, report_date, file_path, created_at) VALUES (?, ?, ?, ?);",
        (report_id, report_date, file_path, created_at)
    )
    conn.commit()


def find_report_by_id(conn: sqlite3.Connection, report_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a report metadata record by unique ID."""
    cursor = conn.cursor()
    row = cursor.execute(
        "SELECT id, report_date, file_path, created_at FROM reports WHERE id = ?;",
        (report_id,)
    ).fetchone()
    return dict(row) if row else None


def list_reports_records(conn: sqlite3.Connection, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Retrieve list of report records ordered by creation date descending, with optional limit."""
    cursor = conn.cursor()
    if limit is not None:
        rows = cursor.execute(
            "SELECT id, report_date, file_path, created_at FROM reports ORDER BY created_at DESC LIMIT ?;",
            (limit,)
        ).fetchall()
    else:
        rows = cursor.execute(
            "SELECT id, report_date, file_path, created_at FROM reports ORDER BY created_at DESC;"
        ).fetchall()
    return [dict(row) for row in rows]


def delete_report_by_id(conn: sqlite3.Connection, report_id: str) -> Optional[str]:
    """Delete a report record by ID and return its file_path if deleted, or None if not found."""
    cursor = conn.cursor()
    row = cursor.execute("SELECT file_path FROM reports WHERE id = ?;", (report_id,)).fetchone()
    if not row:
        return None
    file_path = row["file_path"]
    cursor.execute("DELETE FROM reports WHERE id = ?;", (report_id,))
    conn.commit()
    return file_path


def delete_all_reports(conn: sqlite3.Connection) -> List[str]:
    """Delete all report records from the database and return list of file_paths to remove."""
    cursor = conn.cursor()
    rows = cursor.execute("SELECT file_path FROM reports;").fetchall()
    file_paths = [r["file_path"] for r in rows]
    cursor.execute("DELETE FROM reports;")
    conn.commit()
    return file_paths
