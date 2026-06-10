"""
Centralized configuration — loaded from environment variables / .env file.

Uses pydantic-settings BaseSettings for type-safe, validated configuration.
All values have sensible defaults matching the original app.py behavior.
"""

import os
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "gemma3:4b"
    AUDIO_DIR: str = "audio_outputs"
    UPLOAD_DIR: str = "uploads"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

    def ensure_directories(self) -> None:
        """Create required directories if they don't exist."""
        os.makedirs(self.AUDIO_DIR, exist_ok=True)
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (parsed once, reused everywhere)."""
    settings = Settings()
    settings.ensure_directories()
    return settings
