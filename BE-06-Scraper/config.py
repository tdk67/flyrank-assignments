import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    DATABASE_URL: str = "sqlite:///./flyrank_scraper.db"
    USER_AGENT: str = "FlyrankBot/1.0 (+https://github.com/flyrank/flyrank-assignments; bot@flyrank.ai)"
    DEFAULT_RATE_LIMIT_DELAY: float = 0.5
    MAX_RETRIES: int = 3


settings = Settings()
