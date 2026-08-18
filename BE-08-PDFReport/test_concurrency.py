import asyncio
import pytest
from datetime import datetime
from db import get_db_connection
from services import report_service
from setup_db import run_db_setup

run_db_setup()


def test_concurrent_report_requests_single_flight():
    """
    Verify that 5 concurrent requests arriving at the exact same time when no report exists for today
    acquire the concurrency lock, preventing duplicate PDF generation and race conditions.
    """
    async def _run_concurrent_requests():
        # Clear any report records generated today to test a fresh concurrent generation
        today_str = datetime.now().strftime("%Y-%m-%d")
        conn = get_db_connection()
        conn.execute("DELETE FROM reports WHERE report_date = ?;", (today_str,))
        conn.commit()
        conn.close()

        # Fire 5 concurrent report generation calls simultaneously
        tasks = [
            report_service.generate_report_metadata(force=False)
            for _ in range(5)
        ]
        results = await asyncio.gather(*tasks)

        # All 5 calls should succeed
        assert len(results) == 5

        # Inspect the report IDs returned across all 5 concurrent calls
        report_ids = [res[0].id for res in results]
        is_new_flags = [res[1] for res in results]

        # Exactly 1 call should have generated a new report (is_new=True),
        # while the remaining 4 concurrent calls waited on lock and returned the same report ID (is_new=False)!
        assert len(set(report_ids)) == 1, "All concurrent requests must resolve to the same report ID"
        assert is_new_flags.count(True) == 1, "Exactly one request should execute generation"
        assert is_new_flags.count(False) == 4, "The remaining requests should serve the idempotent result"

    asyncio.run(_run_concurrent_requests())
