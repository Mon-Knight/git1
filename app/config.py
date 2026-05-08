"""
AI World Engine - Configuration Management
Reads settings from environment variables with sensible defaults.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    # AI Configuration
    AI_API_KEY: str = os.getenv("AI_API_KEY", "")
    AI_BASE_URL: str = os.getenv("AI_BASE_URL", "https://api.openai.com/v1")
    AI_MODEL: str = os.getenv("AI_MODEL", "gpt-4o")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ai_world_engine.db")

    # Application
    APP_HOST: str = os.getenv("APP_HOST", "127.0.0.1")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
    APP_DEBUG: bool = os.getenv("APP_DEBUG", "false").lower() == "true"

    # Version
    VERSION: str = "0.1.0"

    @property
    def is_mock_ai(self) -> bool:
        """Return True if AI_API_KEY is not set (mock mode)."""
        return not self.AI_API_KEY


# Singleton instance
settings = Settings()
