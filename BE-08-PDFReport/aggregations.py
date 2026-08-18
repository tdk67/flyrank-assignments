import sqlite3
from typing import Dict, Any, Optional
from db import get_db_connection
from config import config
import repository


def get_report_data(conn: sqlite3.Connection = None, limit: Optional[int] = None) -> Dict[str, Any]:
    """
    Executes high-performance SQL aggregation queries via the repository layer and returns report dictionary.
    """
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True

    effective_limit = limit if limit is not None else config.max_catalog_limit
    data = repository.fetch_report_aggregations(conn, limit=effective_limit)

    if should_close:
        conn.close()

    return data


if __name__ == "__main__":
    import json
    data = get_report_data()
    print("[OK] Report Data Aggregation Successful!")
    print(json.dumps(data["summary"], indent=2))
    print(f"Top 5 Count: {len(data['top_5_expensive'])}")
    print(f"All Books Rendered: {len(data['all_books'])} (Limit: {data['catalog_limit']}, Truncated: {data['is_truncated']})")
