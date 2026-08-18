import asyncio
import pytest
from pathlib import Path
from aggregations import get_report_data
from pdf_generator import render_html_template, generate_pdf_bytes
from config import config


def test_generate_pdf_bytes():
    """Verify Playwright Chromium converts HTML to valid binary PDF bytes."""
    async def _test():
        data = get_report_data()
        html = render_html_template(data)
        pdf_bytes = await generate_pdf_bytes(html)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 10000
        # PDF magic byte signature header
        assert pdf_bytes.startswith(b"%PDF-1.")

    asyncio.run(_test())


def test_pdf_file_creation():
    """Verify generated PDF can be written to disk in reports directory."""
    async def _test():
        data = get_report_data()
        html = render_html_template(data)
        pdf_bytes = await generate_pdf_bytes(html)

        reports_dir = config.resolve("reports_dir")
        test_pdf_path = reports_dir / "test.pdf"
        test_pdf_path.write_bytes(pdf_bytes)

        assert test_pdf_path.exists()
        assert test_pdf_path.is_file()
        assert test_pdf_path.stat().st_size > 10000

    asyncio.run(_test())
