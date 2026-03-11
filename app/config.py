"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings sourced from .env file."""

    # Database
    database_url: str = "postgresql+asyncpg://autoapply:autoapply@localhost:5433/autoapply"

    # Google Gemini
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.1-flash-lite"

    # Server
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # CORS
    cors_origins: list[str] = ["*"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
