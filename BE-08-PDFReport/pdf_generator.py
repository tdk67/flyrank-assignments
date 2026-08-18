import sys
import asyncio
from pathlib import Path
from typing import AsyncGenerator
from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright
from config import config

# Set up Jinja2 environment loader
jinja_env = Environment(loader=FileSystemLoader(str(config.resolve("templates_dir"))))


def render_html_template(data: dict, template_name: str = "report_template.html") -> str:
    """Renders data into the decoupled HTML template."""
    template = jinja_env.get_template(template_name)
    return template.render(**data)


FOOTER_TEMPLATE = """
<div style="font-family: 'Inter', system-ui, -apple-system, sans-serif; font-size: 8.5px; color: #64748b; width: 100%; padding: 0 14mm; display: flex; justify-content: space-between; box-sizing: border-box;">
    <span>FlyRank Backend Track • Assignment A8 PDF Generator</span>
    <span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span>
</div>
"""


async def _raw_playwright_pdf_render(html_content: str) -> bytes:
    """Internal raw Playwright Chromium PDF generator."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        # Set HTML content and wait until network is idle (fonts loaded)
        await page.set_content(html_content, wait_until="networkidle")

        pdf_bytes = await page.pdf(
            format="A4",
            print_background=True,
            display_header_footer=True,
            header_template="<div style='font-size: 8px;'></div>",
            footer_template=FOOTER_TEMPLATE,
            margin={"top": "16mm", "bottom": "16mm", "left": "14mm", "right": "14mm"}
        )
        await browser.close()
        return pdf_bytes



def _sync_render_with_proactor(html_content: str) -> bytes:
    """
    Sync worker function executing Playwright inside a dedicated ProactorEventLoop thread.
    Guarantees Windows subprocess transport support regardless of main Uvicorn event loop type.
    """
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    return asyncio.run(_raw_playwright_pdf_render(html_content))


async def generate_pdf_bytes(html_content: str) -> bytes:
    """
    Uses Playwright Chromium to convert HTML string to PDF bytes in memory.
    Offloads execution to an isolated thread with WindowsProactorEventLoopPolicy to prevent
    NotImplementedError when running inside Uvicorn or non-Proactor event loops.
    """
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _sync_render_with_proactor, html_content)


async def stream_bytes_chunks(pdf_bytes: bytes, chunk_size: int = 8192) -> AsyncGenerator[bytes, None]:
    """
    Async generator for streaming PDF bytes directly from memory.
    Decouples in-memory streaming from disk write operations.
    """
    for i in range(0, len(pdf_bytes), chunk_size):
        yield pdf_bytes[i:i + chunk_size]
        await asyncio.sleep(0)  # yield control to event loop


async def stream_file_chunks(file_path: Path, chunk_size: int = 8192) -> AsyncGenerator[bytes, None]:
    """
    Async generator for streaming pre-generated PDF file bytes directly from disk.
    Provides sub-millisecond instant download start for idempotent requests.
    """
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            yield chunk
            await asyncio.sleep(0)


if __name__ == "__main__":
    from aggregations import get_report_data

    async def test_run():
        print("[1/3] Fetching aggregation data...")
        data = get_report_data()

        print("[2/3] Rendering HTML template...")
        html = render_html_template(data)

        print("[3/3] Generating PDF bytes via Playwright Chromium...")
        pdf_bytes = await generate_pdf_bytes(html)

        out_path = config.resolve("reports_dir") / "test.pdf"
        out_path.write_bytes(pdf_bytes)
        print(f"[OK] Generated PDF report successfully!")
        print(f"     File Path: {out_path}")
        print(f"     File Size: {len(pdf_bytes):,} bytes")

    asyncio.run(test_run())
