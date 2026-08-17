import json
import sqlite3
from datetime import datetime
from typing import Dict, Any
from db import get_db_connection

def get_report_data(conn: sqlite3.Connection = None) -> Dict[str, Any]:
    """Executes high-performance SQL aggregation queries and returns report dictionary."""
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
        
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

    summary = {
        "total_books": summary_row["total_books"],
        "avg_price": round(summary_row["avg_price"], 2),
        "total_stock": summary_row["total_stock"],
        "total_value": round(summary_row["total_value"], 2)
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

    # 5. All Books (for multi-page report demonstration & page-break testing)
    all_rows = cursor.execute("""
        SELECT upc, title, category, price_incl_tax, rating, stock_quantity
        FROM books
        ORDER BY title ASC;
    """).fetchall()

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

    if should_close:
        conn.close()

    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "summary": summary,
        "rating_breakdown": rating_breakdown,
        "category_breakdown": category_breakdown,
        "top_5_expensive": top_5_expensive,
        "all_books": all_books
    }

if __name__ == "__main__":
    data = get_report_data()
    print("[OK] Report Data Aggregation Successful!")
    print(json.dumps(data["summary"], indent=2))
    print(f"Top 5 Count: {len(data['top_5_expensive'])}")
    print(f"All Books Count: {len(data['all_books'])}")
