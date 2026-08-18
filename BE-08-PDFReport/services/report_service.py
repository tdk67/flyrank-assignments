"""
Report Service Layer.
Contains core business logic, workflow orchestration, file system management,
and coordination between the Repository Layer and PDF Generation Engine.
Includes concurrency locking (single-flight execution) to prevent race conditions
and decoupled in-memory / disk-file streaming.
"""
import asyncio
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
from fastapi import HTTPException
from fastapi.responses import FileResponse, StreamingResponse

from config import config
from db import get_db_connection
import repository
from pdf_generator import (
    render_html_template,
    generate_pdf_bytes,
    stream_bytes_chunks,
    stream_file_chunks
)
from schemas import ReportMetadataResponse, HealthResponse

# Global Asyncio Concurrency Lock: Prevents race conditions when multiple concurrent
# requests call report generation at the exact same time.
_generation_lock = asyncio.Lock()


def get_health_status() -> HealthResponse:
    """Retrieve system health and database book count."""
    conn = get_db_connection()
    try:
        count = repository.get_books_count(conn)
        return HealthResponse(
            status="ok",
            app="BE-08 PDF Report Generator",
            books_count=count
        )
    finally:
        conn.close()


def list_reports(limit: Optional[int] = None) -> List[ReportMetadataResponse]:
    """Retrieve list of generated report metadata records."""
    conn = get_db_connection()
    try:
        records = repository.list_reports_records(conn, limit=limit)
        return [
            ReportMetadataResponse(
                id=r["id"],
                report_date=r["report_date"],
                file=f"/reports/{r['id']}/file",
                created_at=str(r["created_at"]),
                idempotent=False
            )
            for r in records
        ]
    finally:
        conn.close()


async def get_or_create_report(force: bool = False) -> Tuple[Dict[str, Any], Optional[bytes], bool]:
    """
    Thread-safe & Task-safe report orchestration with Single-Flight Concurrency Lock.
    Prevents race conditions when multiple requests hit generation simultaneously.
    Returns (report_record_dict, pdf_bytes_in_memory, is_newly_created_boolean).
    """
    today_str = datetime.now().strftime("%Y-%m-%d")

    # Fast-path check without acquiring lock (if force=False)
    if not force:
        conn = get_db_connection()
        try:
            existing = repository.find_latest_report_by_date(conn, today_str)
            if existing and Path(existing["file_path"]).exists():
                return existing, None, False
        finally:
            conn.close()

    # Acquire concurrency lock for critical section (PDF generation & DB insert)
    async with _generation_lock:
        conn = get_db_connection()
        try:
            # Double-check inside lock: maybe another concurrent request finished while we waited!
            if not force:
                existing = repository.find_latest_report_by_date(conn, today_str)
                if existing and Path(existing["file_path"]).exists():
                    return existing, None, False

            # Generate fresh PDF in memory
            report_id = str(uuid.uuid4())[:8]
            data = repository.fetch_report_aggregations(conn, limit=config.max_catalog_limit)
            html = render_html_template(data)
            pdf_bytes = await generate_pdf_bytes(html)

            # Persist file to disk
            file_path = config.resolve("reports_dir") / f"{report_id}.pdf"
            file_path.write_bytes(pdf_bytes)

            created_at_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Persist metadata to database
            repository.insert_report_record(conn, report_id, today_str, str(file_path), created_at_str)

            new_record = {
                "id": report_id,
                "report_date": today_str,
                "file_path": str(file_path),
                "created_at": created_at_str
            }
            return new_record, pdf_bytes, True
        finally:
            conn.close()


async def generate_report_metadata(force: bool = False) -> Tuple[ReportMetadataResponse, bool]:
    """
    Service method for POST /reports.
    Orchestrates report retrieval/generation and formats the metadata response.
    Returns (ReportMetadataResponse, is_newly_created_boolean).
    """
    record, _, is_new = await get_or_create_report(force=force)
    response = ReportMetadataResponse(
        id=record["id"],
        report_date=record["report_date"],
        file=f"/reports/{record['id']}/file",
        created_at=str(record["created_at"]),
        idempotent=not is_new
    )
    return response, is_new


async def stream_pdf_report(force: bool = False) -> StreamingResponse:
    """
    Service method for GET /reports/stream ("Immediate PDF Streaming").
    Decouples memory streaming from disk storage:
      - If fresh: streams pdf_bytes directly from memory while file is persisted to disk.
      - If idempotent: streams existing PDF file directly from disk (0ms TTFB).
    """
    record, pdf_bytes, is_new = await get_or_create_report(force=force)

    if is_new and pdf_bytes:
        # Stream directly from memory buffer
        byte_stream = stream_bytes_chunks(pdf_bytes)
    else:
        # Stream pre-existing report file from disk
        file_path = Path(record["file_path"])
        byte_stream = stream_file_chunks(file_path)

    filename = f"book_analytics_report_{record['id']}.pdf"

    return StreamingResponse(
        byte_stream,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Report-Id": record["id"],
            "X-Report-Idempotent": "false" if is_new else "true"
        }
    )


def _fetch_existing_report_or_404(conn, report_id: str) -> Dict[str, Any]:
    """Helper to fetch a report record by ID or raise 404 HTTPException."""
    row = repository.find_report_by_id(conn, report_id)
    if not row:
        raise HTTPException(status_code=404, detail=f"Report '{report_id}' not found.")
    return row


def get_report_metadata_by_id(report_id: str) -> dict:
    """Retrieve metadata dict for a specific report ID."""
    conn = get_db_connection()
    try:
        row = _fetch_existing_report_or_404(conn, report_id)
        return {
            "id": row["id"],
            "report_date": row["report_date"],
            "file": f"/reports/{row['id']}/file",
            "created_at": str(row["created_at"])
        }
    finally:
        conn.close()


def get_report_file_response(report_id: str) -> FileResponse:
    """Serve stored PDF file for a given report ID."""
    conn = get_db_connection()
    try:
        row = _fetch_existing_report_or_404(conn, report_id)
        file_path = Path(row["file_path"])
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Report file on disk is missing.")

        return FileResponse(
            path=file_path,
            media_type="application/pdf",
            filename=f"book_analytics_report_{report_id}.pdf"
        )
    finally:
        conn.close()
