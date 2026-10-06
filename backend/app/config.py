from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=REPO_ROOT / ".env", extra="ignore")

    data_dir: Path = REPO_ROOT / "data"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"
    cors_origins: list[str] = ["http://localhost:5173"]


settings = Settings()
