"""
AI World Engine - Configuration Management
Reads settings from environment variables with sensible defaults.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def resource_path(relative_path: str) -> str:
    """
    Get the absolute path to a resource file.
    Works both in normal Python mode and PyInstaller bundled mode.
    """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(os.path.dirname(__file__))
        base_path = os.path.dirname(base_path)

    return os.path.join(base_path, relative_path)


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
    VERSION: str = "2.1.0"

    @property
    def is_mock_ai(self) -> bool:
        """Return True if AI_API_KEY is not set (mock mode)."""
        return not self.AI_API_KEY

    @staticmethod
    def get_desktop_db_path() -> str:
        """
        Get database path for desktop mode.
        Uses Windows AppData/Local/AIWorldEngine/ai_world_engine.db.
        """
        if sys.platform == "win32":
            appdata = os.getenv("LOCALAPPDATA")
            if appdata:
                db_dir = os.path.join(appdata, "AIWorldEngine")
                os.makedirs(db_dir, exist_ok=True)
                db_path = os.path.join(db_dir, "ai_world_engine.db")
                return f"sqlite:///{db_path}"
        return "sqlite:///./ai_world_engine.db"


# Singleton instance
settings = Settings()
