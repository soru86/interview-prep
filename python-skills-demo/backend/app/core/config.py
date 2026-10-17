"""Application-wide settings loaded from environment variables."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Central configuration sourced from .env / environment."""

    APP_NAME: str = "Python Skills Demo"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite:///./app.db"

    # JWT / Security
    SECRET_KEY: str = "aacc53ab58a94c41d6fe92d817bf86c34d0d47cfb801a61776441fbb88ff6d18"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    ALGORITHM: str = "HS256"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (read once per process)."""
    return Settings()
