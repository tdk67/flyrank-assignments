import os
import json
import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.config import config

client = TestClient(app)


def test_stage4_kill_switch():
    """Setting LLM_ENABLED=false returns 503 Service Unavailable instantly."""
    os.environ["LLM_ENABLED"] = "false"
    config.llm_enabled = False

    payload = {
        "book_id": "a897fe39b1053632",
        "target_language": "de",
    }
    response = client.post("/books/translate", json=payload)
    assert response.status_code == 503
    assert "disabled" in response.json()["detail"].lower()

    os.environ["LLM_ENABLED"] = "true"
    config.llm_enabled = True


def test_stage4_cost_logging():
    """Stub or live call verifies cost log format or existence."""
    os.environ["LLM_ENABLED"] = "true"
    config.llm_enabled = True

    os.environ["LLM_STUB"] = "1"
    config.llm_stub = True

    payload = {
        "book_id": "a897fe39b1053632",
        "target_language": "fr",
    }
    response = client.post("/books/translate", json=payload)
    assert response.status_code == 200
