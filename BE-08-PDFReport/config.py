import json
from pathlib import Path
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parent
CONFIG_JSON_PATH = PROJECT_ROOT / "config.json"


class AppConfig(BaseModel):
    db_path: str = Field(..., description="Path to SQLite database file")
    reports_dir: str = Field(..., description="Directory for storing output PDF reports")
    templates_dir: str = Field(..., description="Directory containing HTML Jinja2 templates")

    def resolve(self, key: str) -> Path:
        """Generic path resolver: converts relative config paths to absolute Path objects."""
        p = Path(getattr(self, key))
        return p if p.is_absolute() else (PROJECT_ROOT / p).resolve()

    @classmethod
    def load(cls) -> "AppConfig":
        if not CONFIG_JSON_PATH.exists():
            raise FileNotFoundError(
                f"❌ Configuration Error: Mandatory configuration file '{CONFIG_JSON_PATH}' is missing!"
            )

        with open(CONFIG_JSON_PATH, "r", encoding="utf-8") as f:
            try:
                json_data = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"❌ Configuration Error: 'config.json' contains invalid JSON: {e}")

        config_obj = cls.model_validate(json_data)
        config_obj.resolve("reports_dir").mkdir(parents=True, exist_ok=True)
        return config_obj


config = AppConfig.load()
