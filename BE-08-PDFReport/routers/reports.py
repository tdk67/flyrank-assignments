"""
Reports API Router.
Handles HTTP request parsing, status codes, and delegates business logic to the Report Service.
Contains NO SQL queries or database manipulation.
"""
from typing import List, Optional
from fastapi import APIRouter, Query, Response, status
from fastapi.responses import FileResponse, StreamingResponse
from schemas import ReportMetadataResponse
from services import report_service

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("", response_model=List[ReportMetadataResponse])
def list_reports(limit: Optional[int] = Query(None, ge=1, description="Optional limit to show N most recent reports")):
    """List generated reports metadata ordered by created_at DESC, with optional limit filter."""
    return report_service.list_reports(limit=limit)


@router.post("", response_model=ReportMetadataResponse, status_code=status.HTTP_201_CREATED)
async def generate_report(
    response: Response,
    force: bool = Query(False, description="Set force=true to bypass idempotency check")
):
    """
    Generate & store PDF report on disk with idempotency check.
    If a report was generated today and force=False, returns existing report link with 200 OK.
    Otherwise, generates a new report with 201 Created.
    """
    metadata, is_new = await report_service.generate_report_metadata(force=force)
    if not is_new:
        response.status_code = status.HTTP_200_OK
    else:
        response.status_code = status.HTTP_201_CREATED
    return metadata


@router.post(
    "/stream",
    response_class=StreamingResponse,
    responses={
        200: {
            "content": {
                "application/pdf": {
                    "schema": {
                        "type": "string",
                        "format": "binary"
                    }
                }
            },
            "description": "Binary PDF report stream. Swagger UI presents a direct Download file button."
        }
    }
)
async def stream_report_pdf(force: bool = Query(False, description="Set force=true to bypass idempotency check")):
    """
    Immediate PDF Streaming Endpoint ("The Performance Trick").
    Combines report generation & DB bookkeeping with instant file/byte streaming.
    If a report was generated today and force=False, streams existing PDF from disk instantly (0ms TTFB!).
    """
    return await report_service.stream_pdf_report(force=force)


@router.get("/{report_id}")
def get_report_metadata(report_id: str):
    """Retrieve metadata record for a generated report by ID."""
    return report_service.get_report_metadata_by_id(report_id)


@router.get(
    "/{report_id}/file",
    response_class=FileResponse,
    responses={
        200: {
            "content": {
                "application/pdf": {
                    "schema": {
                        "type": "string",
                        "format": "binary"
                    }
                }
            },
            "description": "Binary PDF report file."
        }
    }
)
def download_report_file(report_id: str):
    """Download stored PDF report file from disk."""
    return report_service.get_report_file_response(report_id)
