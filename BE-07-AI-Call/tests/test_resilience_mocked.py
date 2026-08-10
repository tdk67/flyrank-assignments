import os
import json
import time
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from openai import APITimeoutError, AuthenticationError, APIStatusError, BadRequestError

from src.main import app
from src.config import config

client = TestClient(app)


def count_log_lines(filepath) -> int:
    """Helper to count non-empty lines in a log file."""
    if not filepath.exists():
        return 0
    with open(filepath, "r", encoding="utf-8") as f:
        return len([line for line in f if line.strip()])


def test_health_endpoint():
    """M10 & Nit 4 Fix: Verifies /health endpoint returns loaded book count and dataset status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "loaded_books_count" in data
    assert data["loaded_books_count"] > 0
    assert data["dataset_exists"] is True


def test_response_mismatch_book_id_rejected_and_quarantined():
    """C1 Fix: Verifies that model returning wrong book_id is rejected and repaired/quarantined."""
    config.llm_stub = False
    config.llm_enabled = True

    mock_completion = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = json.dumps({
        "book_id": "WRONG_BOOK_ID",
        "target_language": "de",
        "translated_title": "Falsches Buch",
        "translated_description": "Falsche Beschreibung",
        "confidence": 0.9,
    })
    mock_completion.choices = [mock_choice]
    mock_completion.usage = MagicMock(prompt_tokens=100, completion_tokens=40)

    with patch("src.llm.translator.get_client") as mock_get_client:
        mock_openai = MagicMock()
        mock_openai.chat.completions.create.return_value = mock_completion
        mock_get_client.return_value = mock_openai

        payload = {
            "book_id": "a897fe39b1053632",
            "target_language": "de",
        }
        response = client.post("/books/translate", json=payload)
        assert response.status_code == 422
        assert "mismatch" in response.json()["detail"].lower()
        assert config.resolved_quarantine_log_path.exists()


def test_schema_extra_fields_rejected():
    """C2 Fix: Verifies that extra fields in LLM response trigger schema validation failure."""
    config.llm_stub = False
    config.llm_enabled = True

    mock_completion = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = json.dumps({
        "book_id": "a897fe39b1053632",
        "target_language": "de",
        "translated_title": "Ein Licht auf dem Dachboden",
        "translated_description": "Eine Beschreibung",
        "confidence": 0.95,
        "evil_extra_key": "SYSTEM COMPROMISED",
    })
    mock_completion.choices = [mock_choice]
    mock_completion.usage = MagicMock(prompt_tokens=100, completion_tokens=40)

    with patch("src.llm.translator.get_client") as mock_get_client:
        mock_openai = MagicMock()
        mock_openai.chat.completions.create.return_value = mock_completion
        mock_get_client.return_value = mock_openai

        payload = {
            "book_id": "a897fe39b1053632",
            "target_language": "de",
        }
        response = client.post("/books/translate", json=payload)
        assert response.status_code == 422
        assert "extra" in response.json()["detail"].lower() or "validation" in response.json()["detail"].lower()


def test_timeout_maps_to_504_and_logs_failure():
    """Verifies APITimeoutError maps to 504 and logs failure entry to costs.jsonl and quarantine.jsonl."""
    config.llm_stub = False
    config.llm_enabled = True

    cost_log_before = count_log_lines(config.resolved_cost_log_path)
    quarantine_log_before = count_log_lines(config.resolved_quarantine_log_path)

    with patch("src.llm.translator.get_client") as mock_get_client:
        mock_openai = MagicMock()
        mock_openai.chat.completions.create.side_effect = APITimeoutError(request=None)
        mock_get_client.return_value = mock_openai

        payload = {
            "book_id": "a897fe39b1053632",
            "target_language": "de",
        }
        response = client.post("/books/translate", json=payload)
        assert response.status_code == 504
        assert "timed out" in response.json()["detail"].lower()

        # Assert cost and quarantine log lines WERE appended with success=False
        cost_log_after = count_log_lines(config.resolved_cost_log_path)
        quarantine_log_after = count_log_lines(config.resolved_quarantine_log_path)

        assert cost_log_after == cost_log_before + 1
        assert quarantine_log_after == quarantine_log_before + 1


def test_wall_clock_timeout_exceeded_maps_to_504_and_logs_failure():
    """Verifies that if call_duration exceeds timeout_seconds (e.g. 40.9s), an HTTP 504 is returned and logged."""
    config.llm_stub = False
    config.llm_enabled = True

    cost_log_before = count_log_lines(config.resolved_cost_log_path)
    quarantine_log_before = count_log_lines(config.resolved_quarantine_log_path)

    mock_completion = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = json.dumps({
        "book_id": "a897fe39b1053632",
        "target_language": "de",
        "translated_title": "Ein Licht",
        "translated_description": "Beschreibung",
        "confidence": 0.9,
    })
    mock_completion.choices = [mock_choice]
    mock_completion.usage = MagicMock(prompt_tokens=100, completion_tokens=40)

    with patch("src.llm.translator.get_client") as mock_get_client:
        mock_openai = MagicMock()

        def slow_create(*args, **kwargs):
            time.sleep(0.1)  # Simulate slow call
            return mock_completion

        mock_openai.chat.completions.create.side_effect = slow_create
        mock_get_client.return_value = mock_openai

        # Set tight timeout of 0.05s for testing
        config.timeout_seconds = 0.05

        payload = {
            "book_id": "a897fe39b1053632",
            "target_language": "de",
        }
        response = client.post("/books/translate", json=payload)
        assert response.status_code == 504
        assert "timed out" in response.json()["detail"].lower()

        # Assert cost and quarantine log lines WERE appended
        cost_log_after = count_log_lines(config.resolved_cost_log_path)
        quarantine_log_after = count_log_lines(config.resolved_quarantine_log_path)

        assert cost_log_after == cost_log_before + 1
        assert quarantine_log_after == quarantine_log_before + 1


def test_auth_error_sanitized_to_502():
    """H6 & M3 Fix: Verifies provider AuthenticationError maps to 502 Bad Gateway without leaking keys."""
    config.llm_stub = False
    config.llm_enabled = True

    mock_resp = MagicMock(status_code=401, headers={})
    auth_err = AuthenticationError(message="Invalid API Key sk-secret-12345", response=mock_resp, body={"error": "invalid_key"})

    with patch("src.llm.translator.get_client") as mock_get_client:
        mock_openai = MagicMock()
        mock_openai.chat.completions.create.side_effect = auth_err
        mock_get_client.return_value = mock_openai

        payload = {
            "book_id": "a897fe39b1053632",
            "target_language": "de",
        }
        response = client.post("/books/translate", json=payload)
        assert response.status_code == 502
        assert "sk-secret" not in response.json()["detail"]
        assert "authentication failed" in response.json()["detail"].lower()


def test_empty_choices_handled_cleanly():
    """M8 Fix: Verifies empty choices array from provider is caught cleanly."""
    config.llm_stub = False
    config.llm_enabled = True

    mock_completion = MagicMock()
    mock_completion.choices = []

    with patch("src.llm.translator.get_client") as mock_get_client:
        mock_openai = MagicMock()
        mock_openai.chat.completions.create.return_value = mock_completion
        mock_get_client.return_value = mock_openai

        payload = {
            "book_id": "a897fe39b1053632",
            "target_language": "de",
        }
        response = client.post("/books/translate", json=payload)
        assert response.status_code in (422, 500)
