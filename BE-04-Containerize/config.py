from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_user: str = "postgres"
    postgres_password: str = "postgrespassword"
    postgres_db: str = "user_db"
    postgres_host: str = "db"
    postgres_port: int = 5432

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        user = quote_plus(self.postgres_user)
        password = quote_plus(self.postgres_password)
        return f"postgresql://{user}:{password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"


settings = Settings()
