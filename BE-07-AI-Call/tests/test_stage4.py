import os
import json
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from src.main import app
from src.config import config

client = TestClient(app)


def test_stage4_kill_switch():
    """Setting LLM_ENABLED=false returns 503 Service Unavailable instantly."""
    config.llm_enabled = False

    payload = {
        "book_id": "a897fe39b1053632",
        "target_language": "de",
    }
    response = client.post("/books/translate", json=payload)
    assert response.status_code == 503
    assert "disabled" in response.json()["detail"].lower()

    config.llm_enabled = True


def test_stage4_cost_logging_real_llm_path():
    """H2 Fix: Verifies cost logging entry is written to logs/costs.jsonl on live/mocked translation call."""
    config.llm_stub = False
    config.llm_enabled = True

    mock_completion = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = json.dumps({
        "book_id": "a897fe39b1053632",
        "target_language": "fr",
        "translated_title": "Un Licht dans le Dachboden",
        "translated_description": "Une description de test.",
        "confidence": 0.95,
    })
    mock_completion.choices = [mock_choice]
    mock_completion.usage = MagicMock(prompt_tokens=100, completion_tokens=40)

    with patch("src.llm.translator.get_client") as mock_get_client:
        mock_openai = MagicMock()
        mock_openai.chat.completions.create.return_value = mock_completion
        mock_get_client.return_value = mock_openai

        payload = {
            "book_id": "a897fe39b1053632",
            "target_language": "fr",
        }
        response = client.post("/books/translate", json=payload)
        assert response.status_code == 200

        # Assert cost log file exists and contains a valid log entry
        cost_log_path = config.resolved_cost_log_path
        assert cost_log_path.exists()
        with open(cost_log_path, "r", encoding="utf-8") as f:
            lines = [json.loads(line) for line in f if line.strip()]
            assert len(lines) > 0
            latest = lines[-1]
            assert "prompt_version" in latest
            assert "total_tokens" in latest
            assert "duration_ms" in latest
            assert "success" in latest
