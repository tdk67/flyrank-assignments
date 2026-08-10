import os
import pytest
from fastapi.testclient import TestClient

# Disable stub mode for live model testing
os.environ["LLM_STUB"] = "0"
os.environ["LLM_ENABLED"] = "true"

from src.main import app

client = TestClient(app)


def test_stage2_3_live_translation_de():
    """Tests real LLM translation of a book into German (de)."""
    payload = {
        "book_id": "a897fe39b1053632",  # A Light in the Attic
        "target_language": "de",
    }
    response = client.post("/books/translate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["book_id"] == "a897fe39b1053632"
    assert data["target_language"] == "de"
    assert isinstance(data["translated_title"], str)
    assert isinstance(data["translated_description"], str)
    assert 0.0 <= data["confidence"] <= 1.0
    print("\n[SUCCESS] Live Model Output (German):", data)
