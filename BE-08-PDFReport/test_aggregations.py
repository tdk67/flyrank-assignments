import pytest
from aggregations import get_report_data
from db import get_db_connection


def test_report_data_structure():
    """Verify get_report_data returns the complete expected schema structure."""
    data = get_report_data()

    assert "generated_at" in data
    assert "summary" in data
    assert "rating_breakdown" in data
    assert "category_breakdown" in data
    assert "top_5_expensive" in data
    assert "all_books" in data


def test_summary_kpi_math():
    """Verify summary KPIs contain non-null positive numbers."""
    data = get_report_data()
    summary = data["summary"]

    assert summary["total_books"] > 0
    assert summary["avg_price"] > 0.0
    assert summary["total_stock"] > 0
    assert summary["total_value"] > 0.0


def test_top_5_expensive_sorting():
    """Verify top_5_expensive contains at most 5 books sorted descending by price."""
    data = get_report_data()
    top_5 = data["top_5_expensive"]

    assert 0 < len(top_5) <= 5

    # Verify descending sort order
    prices = [item["price"] for item in top_5]
    assert prices == sorted(prices, reverse=True)


def test_rating_and_category_breakdowns():
    """Verify rating and category breakdown structures and counts."""
    data = get_report_data()
    rating_bd = data["rating_breakdown"]
    category_bd = data["category_breakdown"]

    assert len(rating_bd) > 0
    for r in rating_bd:
        assert 1 <= r["rating"] <= 5
        assert r["count"] > 0
        assert r["avg_price"] >= 0.0

    assert len(category_bd) > 0
    for c in category_bd:
        assert len(c["category"]) > 0
        assert c["count"] > 0
        assert c["total_stock"] >= 0
