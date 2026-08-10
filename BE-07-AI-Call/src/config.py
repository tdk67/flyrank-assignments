import json
import os
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_JSON_PATH = PROJECT_ROOT / "config.json"


class AppConfig(BaseModel):
    # From config.json (Strictly required from config.json - ZERO hardcoded fallbacks!)
    timeout_seconds: float = Field(..., description="Overall wall-clock timeout cap for the translation request in seconds")
    max_network_retries: int = Field(..., description="Max backoff retries for 429/5xx errors")
    max_repair_retries: int = Field(..., description="Max repair retries for schema validation failures")
    prompt_version: str = Field(..., description="Current system prompt version")
    allowed_languages: list[str] = Field(..., description="Supported target language ISO codes")
    books_dataset_path: str = Field(..., description="Path to scraped books dataset")
    prompts_dir: str = Field(..., description="Directory containing prompt template files")
    logs_dir: str = Field(..., description="Directory containing log files")

    # From .env / Environment (Strictly required secrets)
    llm_base_url: str = Field(..., description="LLM Provider Base URL")
    llm_api_key: str = Field(..., description="LLM API Key")
    llm_model: str = Field(..., description="LLM Model Name")
    llm_stub: bool = Field(..., description="Stub Mode toggle flag")
    llm_enabled: bool = Field(..., description="Kill Switch toggle flag")

    @property
    def resolved_books_file_path(self) -> Path:
        """Resolves books dataset path relative to project root or environment override."""
        override = os.getenv("BOOKS_DATASET_PATH")
        path_str = override if override else self.books_dataset_path
        p = Path(path_str)
        return p if p.is_absolute() else (PROJECT_ROOT / p).resolve()

    @property
    def resolved_prompt_file_path(self) -> Path:
        """Resolves versioned prompt file path dynamically."""
        filename = f"book-translate-{self.prompt_version}.md"
        return (PROJECT_ROOT / self.prompts_dir / filename).resolve()

    @property
    def resolved_quarantine_log_path(self) -> Path:
        """Resolves quarantine log file path."""
        return (PROJECT_ROOT / self.logs_dir / "quarantine.jsonl").resolve()

    @property
    def resolved_cost_log_path(self) -> Path:
        """Resolves cost log file path."""
        return (PROJECT_ROOT / self.logs_dir / "costs.jsonl").resolve()

    @classmethod
    def load(cls) -> "AppConfig":
        """Loads configuration from config.json and .env. Fails fast if ANY setting is missing."""
        load_dotenv()

        if not CONFIG_JSON_PATH.exists():
            raise FileNotFoundError(
                f"❌ Configuration Error: Mandatory configuration file '{CONFIG_JSON_PATH}' is missing!"
            )

        with open(CONFIG_JSON_PATH, "r", encoding="utf-8") as f:
            try:
                json_data = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"❌ Configuration Error: 'config.json' contains invalid JSON: {e}")

        # Fetch environment variables
        stub_raw = os.getenv("LLM_STUB", "0").strip().lower()
        enabled_raw = os.getenv("LLM_ENABLED", "true").strip().lower()

        env_data = {
            "llm_base_url": os.getenv("LLM_BASE_URL", "").strip(),
            "llm_api_key": os.getenv("LLM_API_KEY", "").strip(),
            "llm_model": os.getenv("LLM_MODEL", "").strip(),
            "llm_stub": stub_raw in ("1", "true", "yes", "on"),
            "llm_enabled": enabled_raw in ("1", "true", "yes", "on"),
        }

        missing_secrets = [k.upper() for k, v in env_data.items() if k in ("llm_base_url", "llm_api_key", "llm_model") and not v]
        if missing_secrets:
            raise ValueError(
                f"❌ Configuration Error: Missing required environment variable(s) in .env: {', '.join(missing_secrets)}"
            )

        merged = {**json_data, **env_data}
        return cls.model_validate(merged)


# Global singleton instance
config = AppConfig.load()


def reload_config() -> AppConfig:
    """Reloads config from disk and environment for test isolation (C3 fix)."""
    global config
    config = AppConfig.load()
    return config
