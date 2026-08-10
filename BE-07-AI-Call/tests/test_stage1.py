import os
import pytest
from fastapi.testclient import TestClient

# Set LLM_STUB=1 before importing main app
os.environ["LLM_STUB"] = "1"

from src.main import app

client = TestClient(app)


def test_stage1_valid_stub_request():
    """Valid request in stub mode returns 200 and schema-valid response."""
    valid_payload = {
        "book_id": "a897fe39b1053632",
        "target_language": "de",
    }
    response = client.post("/books/translate", json=valid_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["book_id"] == "a897fe39b1053632"
    assert data["target_language"] == "de"
    assert "translated_title" in data
    assert "translated_description" in data
    assert data["confidence"] == 1.0


def test_stage1_missing_book_id():
    """Missing book ID returns 404 Not Found."""
    payload = {
        "book_id": "non_existent_book_id_9999",
        "target_language": "fr",
    }
    response = client.post("/books/translate", json=payload)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_stage1_invalid_target_language():
    """Unsupported target language returns 400 Bad Request naming offending field."""
    invalid_payload = {
        "book_id": "a897fe39b1053632",
        "target_language": "spanish_unsupported",  # valid is "de", "fr", "it", "en"
    }
    response = client.post("/books/translate", json=invalid_payload)
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert "target_language" in detail.lower()
