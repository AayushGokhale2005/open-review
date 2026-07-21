"""Application settings and paths."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from platformdirs import user_data_dir
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def default_data_dir() -> Path:
    return Path(user_data_dir("OpenReview", "OpenReview"))


def default_repos_dir() -> Path:
    return Path.home() / "AIReviewer" / "repos"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="OPENREVIEW_",
        env_file=".env",
        extra="ignore",
    )

    app_name: str = "Open Review"
    app_version: str = "0.1.0"
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 8741

    data_dir: Path = Field(default_factory=default_data_dir)
    repos_dir: Path = Field(default_factory=default_repos_dir)

    # OAuth — register localhost apps with GitHub/GitLab for production use
    github_client_id: str = ""
    github_client_secret: str = ""
    gitlab_client_id: str = ""
    gitlab_client_secret: str = ""
    oauth_redirect_uri: str = "http://127.0.0.1:8741/auth/callback"

    # AI defaults
    default_ai_provider: str = "ollama"
    ollama_base_url: str = "http://127.0.0.1:11434"
    lmstudio_base_url: str = "http://127.0.0.1:1234/v1"
    vllm_base_url: str = "http://127.0.0.1:8000/v1"

    # Security
    token_encryption_key: str = "dev-only-change-me-in-production!!"

    # Telemetry (always off by default)
    telemetry_enabled: bool = False

    @property
    def database_url(self) -> str:
        db_path = self.data_dir / "openreview.db"
        return f"sqlite+aiosqlite:///{db_path}"

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.repos_dir.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_dirs()
    return settings
