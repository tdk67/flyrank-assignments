import pytest
from aggregations import get_report_data
from pdf_generator import render_html_template


def test_render_html_template_success():
    """Verify render_html_template converts report dictionary into HTML string."""
    data = get_report_data()
    html = render_html_template(data)

    assert isinstance(html, str)
    assert len(html) > 500
    assert html.strip().startswith("<!DOCTYPE html>")


def test_fl05_identity_kit_elements():
    """Verify FL-05 brand tokens (colors, typography, monogram) are present in rendered HTML."""
    data = get_report_data()
    html = render_html_template(data)

    # Palette
    assert "#0284c7" in html  # Sky Blue Accent
    assert "#0f172a" in html  # Slate 900 Text

    # Typography
    assert "Inter" in html
    assert "JetBrains Mono" in html

    # TD Monogram logo badge
    assert "TD" in html
    assert "FlyRank Book Analytics &amp; Inventory Report" in html or "FlyRank Book Analytics" in html


def test_print_css_rules():
    """Verify print CSS rules for PDF page breaks are included."""
    data = get_report_data()
    html = render_html_template(data)

    assert "@page" in html
    assert "break-inside: avoid" in html
    assert "display: table-header-group" in html


def test_kpis_and_tables_rendered():
    """Verify data values are populated into HTML placeholders."""
    data = get_report_data()
    html = render_html_template(data)

    # Summary KPI total books
    assert str(data["summary"]["total_books"]) in html

    # Top 5 expensive book titles rendered
    for book in data["top_5_expensive"]:
        assert book["upc"] in html
