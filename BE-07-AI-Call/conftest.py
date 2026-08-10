import os
import pytest
from src.config import reload_config
from src.llm.translator import reset_client


@pytest.fixture(autouse=True)
def reset_config_and_client():
    """Autouse fixture to reset config singleton and OpenAI client before/after each test (C3 Fix)."""
    # Teardown / Reset before test
    reload_config()
    reset_client()

    yield

    # Teardown / Reset after test
    reload_config()
    reset_client()
