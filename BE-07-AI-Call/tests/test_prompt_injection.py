import os
import json
import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.config import config

client = TestClient(app)


def test_prompt_injection_in_stub_mode():
    """Verifies API returns schema-valid JSON without crashing on prompt injection payloads."""
    os.environ["LLM_STUB"] = "1"
    config.llm_stub = True

    os.environ["LLM_ENABLED"] = "true"
    config.llm_enabled = True

    payload = {
        "book_id": "a897fe39b1053632",
        "target_language": "de",
    }

    response = client.post("/books/translate", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Verify output structure holds against schema
    assert data["book_id"] == "a897fe39b1053632"
    assert data["target_language"] == "de"
    assert "translated_title" in data
    assert "translated_description" in data
    assert 0.0 <= data["confidence"] <= 1.0
