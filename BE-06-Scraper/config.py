import os
from urllib.parse import quote_plus
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "flyrank_scraper"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    USER_AGENT: str = "FlyrankBot/1.0 (+https://github.com/flyrank/flyrank-assignments; bot@flyrank.ai)"
    DEFAULT_RATE_LIMIT_DELAY: float = 0.5
    MAX_RETRIES: int = 3
    DEFAULT_OUTPUT_FORMAT: str = "jsonl"

    @property
    def database_url(self) -> str:
        escaped_user = quote_plus(self.POSTGRES_USER)
        escaped_password = quote_plus(self.POSTGRES_PASSWORD)
        return (
            f"postgresql://{escaped_user}:{escaped_password}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
