"""
BE-08 PDF Report Generator Application Entry Point.
Clean, layered FastAPI application including routers for Health and Reports.
Contains ZERO SQL statements or database logic.
"""
import sys
import asyncio
from fastapi import FastAPI
from routers import health, reports

# Ensure Windows Proactor Event Loop Policy for Playwright Subprocess Transport
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

app = FastAPI(
    title="BE-08 PDF Report Generator API",
    description="Executive Analytics & PDF Report Generator with Immediate Streaming",
    version="1.0.0"
)

# Register Layered Routers
app.include_router(health.router)
app.include_router(reports.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
