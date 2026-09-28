from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / ".env", extra="ignore")
    demo_mode: bool = True
    database_url: str = f"sqlite:///{ROOT / 'backend/inventcheck.sqlite3'}"
    cache_seconds: int = Field(default=300, ge=0, le=3600)
    request_timeout: float = Field(default=5, gt=0, le=30)
    frontend_origin: str = "http://127.0.0.1:5173"
