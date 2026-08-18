import pytest
from fastapi.testclient import TestClient
from main import app
from setup_db import run_db_setup

# Ensure DB setup is run before tests
run_db_setup()
client = TestClient(app)


def test_health_endpoint():
    """Verify health endpoint returns 200 OK and books_count."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["books_count"] > 0


def test_demo_page_endpoint():
    """Verify GET /demo serves static/demo.html lightweight streaming monitor."""
    res = client.get("/demo")
    assert res.status_code == 200
    assert "FlyRank PDF Report Streaming Monitor" in res.text


def test_list_reports_endpoint():
    """Verify GET /reports returns list of generated report metadata with optional limit."""
    # Generate at least 1 report
    client.post("/reports?force=true")

    # 1. GET /reports without limit
    res_all = client.get("/reports")
    assert res_all.status_code == 200
    reports_all = res_all.json()
    assert isinstance(reports_all, list)
    assert len(reports_all) >= 1

    # 2. GET /reports with limit=1
    res_lim = client.get("/reports?limit=1")
    assert res_lim.status_code == 200
    reports_lim = res_lim.json()
    assert isinstance(reports_lim, list)
    assert len(reports_lim) == 1


def test_generate_and_idempotency_flow():
    """Verify POST /reports generates a file, and subsequent calls return idempotent response."""
    res1 = client.post("/reports?force=true")
    assert res1.status_code == 201
    data1 = res1.json()
    assert "id" in data1
    assert data1["file"] == f"/reports/{data1['id']}/file"
    assert data1["idempotent"] is False

    report_id = data1["id"]

    res2 = client.post("/reports")
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["id"] == report_id
    assert data2["idempotent"] is True


def test_get_metadata_and_download_file():
    """Verify metadata lookup and PDF file downloading endpoints."""
    res = client.post("/reports?force=true")
    assert res.status_code == 201
    report_id = res.json()["id"]

    meta_res = client.get(f"/reports/{report_id}")
    assert meta_res.status_code == 200
    meta = meta_res.json()
    assert meta["id"] == report_id

    file_res = client.get(f"/reports/{report_id}/file")
    assert file_res.status_code == 200
    assert file_res.headers["content-type"] == "application/pdf"
    assert file_res.content.startswith(b"%PDF-1.")


def test_immediate_pdf_streaming_with_idempotency():
    """Verify POST /reports/stream creates DB record, supports force, and streams chunks instantly."""
    # 1. Fresh streaming call with force=true -> generates PDF, saves DB row, streams chunks
    res1 = client.post("/reports/stream?force=true")
    assert res1.status_code == 200
    assert res1.headers["content-type"] == "application/pdf"
    assert res1.headers["X-Report-Idempotent"] == "false"
    report_id = res1.headers["X-Report-Id"]
    assert len(res1.content) > 10000

    # Verify report was saved in DB
    meta_res = client.get(f"/reports/{report_id}")
    assert meta_res.status_code == 200

    # 2. Second streaming call without force -> streams existing PDF file from disk (sub-1ms TTFB!)
    res2 = client.post("/reports/stream")
    assert res2.status_code == 200
    assert res2.headers["X-Report-Idempotent"] == "true"
    assert res2.headers["X-Report-Id"] == report_id
    assert res2.content == res1.content


def test_unknown_report_404():
    """Verify 404 Not Found for non-existent report IDs."""
    res_meta = client.get("/reports/unknown_id_999")
    assert res_meta.status_code == 404

    res_file = client.get("/reports/unknown_id_999/file")
    assert res_file.status_code == 404
