"""
BE-08 PDF Report Generator Application Entry Point.
Clean, layered FastAPI application including routers for Health and Reports.
Contains ZERO SQL statements or database logic.
"""
import sys
import asyncio
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from routers import health, reports

# Ensure Windows Proactor Event Loop Policy for Playwright Subprocess Transport
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

app = FastAPI(
    title="BE-08 PDF Report Generator API",
    description="Executive Analytics & PDF Report Generator with Immediate Streaming",
    version="1.0.0"
)

# Enable CORS for browser access from any origin or file:// protocol
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Report-Id", "X-Report-Idempotent", "Content-Disposition"]
)

# Register Layered Routers
app.include_router(health.router)
app.include_router(reports.router)


@app.get("/demo", include_in_schema=False)
def serve_demo_page():
    """Serves the lightweight HTML live streaming monitor dashboard."""
    demo_path = Path(__file__).parent / "static" / "demo.html"
    return FileResponse(demo_path)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
