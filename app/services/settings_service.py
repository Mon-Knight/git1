"""
AI World Engine - Settings Service
Manages application settings stored in the app_settings table.
Configuration priority: DB > .env > defaults.
"""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models import AppSetting
from app.config import settings as env_settings


# Default values for all AI-related settings
DEFAULTS: Dict[str, str] = {
    "ai_provider": "mock",
    "ai_api_key": "",
    "ai_base_url": "",
    "ai_model": "",
    "ai_temperature": "0.7",
    "ai_max_tokens": "2000",
    "ai_timeout": "60",
    "ai_enable_live": "false",
    "ai_simulation_model": "",
    "ai_check_model": "",
    "ai_summary_model": "",
}

# Keys that store sensitive values
SECRET_KEYS = {"ai_api_key"}


class SettingsService:
    """Service for reading and writing application settings."""

    @staticmethod
    def init_defaults(db: Session) -> None:
        """Insert default settings into the database if they don't exist."""
        for key, default_value in DEFAULTS.items():
            existing = db.query(AppSetting).filter(AppSetting.key == key).first()
            if not existing:
                is_secret = key in SECRET_KEYS
                value = default_value
                # Seed from .env if available
                if key == "ai_base_url" and env_settings.AI_BASE_URL:
                    value = env_settings.AI_BASE_URL
                elif key == "ai_api_key" and env_settings.AI_API_KEY:
                    value = env_settings.AI_API_KEY
                elif key == "ai_model" and env_settings.AI_MODEL:
                    value = env_settings.AI_MODEL
                setting = AppSetting(
                    key=key,
                    value=value,
                    is_secret=is_secret,
                )
                db.add(setting)
        db.commit()

    @staticmethod
    def get(db: Session, key: str) -> str:
        """Get a setting value. Returns default if not in DB."""
        row = db.query(AppSetting).filter(AppSetting.key == key).first()
        if row and row.value is not None and row.value != "":
            return row.value
        return DEFAULTS.get(key, "")

    @staticmethod
    def get_bool(db: Session, key: str) -> bool:
        """Get a boolean setting value."""
        val = SettingsService.get(db, key)
        return val.lower() in ("true", "1", "yes")

    @staticmethod
    def get_int(db: Session, key: str, default: int = 0) -> int:
        """Get an integer setting value."""
        val = SettingsService.get(db, key)
        try:
            return int(val)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def get_float(db: Session, key: str, default: float = 0.0) -> float:
        """Get a float setting value."""
        val = SettingsService.get(db, key)
        try:
            return float(val)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def set(db: Session, key: str, value: str, is_secret: bool = False) -> AppSetting:
        """Create or update a setting."""
        row = db.query(AppSetting).filter(AppSetting.key == key).first()
        if row:
            row.value = value
            if is_secret:
                row.is_secret = True
        else:
            row = AppSetting(key=key, value=value, is_secret=is_secret)
            db.add(row)
        db.commit()
        db.refresh(row)
        return row

    @staticmethod
    def set_many(db: Session, settings: Dict[str, Any]) -> None:
        """Create or update multiple settings at once."""
        for key, value in settings.items():
            is_secret = key in SECRET_KEYS
            SettingsService.set(db, key, str(value), is_secret=is_secret)

    @staticmethod
    def get_all(db: Session, include_secrets: bool = False) -> Dict[str, str]:
        """Get all settings as a dict."""
        rows = db.query(AppSetting).all()
        result = {}
        for row in rows:
            if row.is_secret and not include_secrets:
                result[row.key] = SettingsService.mask_secret(row.value or "")
            else:
                result[row.key] = row.value or ""
        # Fill in any missing defaults
        for key, default_val in DEFAULTS.items():
            if key not in result:
                result[key] = default_val if key not in SECRET_KEYS else ""
        return result

    @staticmethod
    def get_all_plain(db: Session) -> Dict[str, str]:
        """Get all settings with secret values included (for internal use only)."""
        return SettingsService.get_all(db, include_secrets=True)

    @staticmethod
    def mask_secret(value: str) -> str:
        """Mask a secret value for display."""
        if not value:
            return ""
        if len(value) <= 8:
            return "****"
        return f"{value[:4]}****{value[-4:]}"

    @staticmethod
    def is_live_enabled(db: Session) -> bool:
        """Check if live AI is enabled and properly configured."""
        enable_live = SettingsService.get_bool(db, "ai_enable_live")
        if not enable_live:
            return False
        provider = SettingsService.get(db, "ai_provider")
        if provider == "mock":
            return False
        if provider == "openai_compatible":
            api_key = SettingsService.get(db, "ai_api_key")
            base_url = SettingsService.get(db, "ai_base_url")
            model = SettingsService.get(db, "ai_model")
            return bool(api_key and base_url and model)
        return False

    @staticmethod
    def get_effective_config(db: Session) -> Dict[str, Any]:
        """Get the effective AI configuration for the model router."""
        return {
            "ai_enable_live": SettingsService.get_bool(db, "ai_enable_live"),
            "ai_provider": SettingsService.get(db, "ai_provider"),
            "ai_api_key": SettingsService.get(db, "ai_api_key"),
            "ai_base_url": SettingsService.get(db, "ai_base_url"),
            "ai_model": SettingsService.get(db, "ai_model"),
            "ai_temperature": SettingsService.get_float(db, "ai_temperature", 0.7),
            "ai_max_tokens": SettingsService.get_int(db, "ai_max_tokens", 2000),
            "ai_timeout": SettingsService.get_int(db, "ai_timeout", 60),
            "ai_simulation_model": SettingsService.get(db, "ai_simulation_model"),
            "ai_check_model": SettingsService.get(db, "ai_check_model"),
            "ai_summary_model": SettingsService.get(db, "ai_summary_model"),
        }

    @staticmethod
    def restore_mock(db: Session) -> None:
        """Restore to mock AI mode."""
        SettingsService.set(db, "ai_enable_live", "false")
        SettingsService.set(db, "ai_provider", "mock")

    @staticmethod
    def get_ai_summary(db: Session) -> Dict[str, Any]:
        """
        Get a safe summary of AI configuration for display on pages.
        Never returns the full API key.
        """
        provider = SettingsService.get(db, "ai_provider")
        enable_live = SettingsService.get_bool(db, "ai_enable_live")
        base_url = SettingsService.get(db, "ai_base_url")
        model = SettingsService.get(db, "ai_model")
        api_key = SettingsService.get(db, "ai_api_key")

        # Determine if live is actually functional
        is_functional = False
        if enable_live and provider == "openai_compatible":
            is_functional = bool(api_key and base_url and model)
        if enable_live and provider != "openai_compatible" and provider != "mock":
            is_functional = bool(api_key and base_url and model)

        if is_functional:
            mode_label = "OpenAI-compatible"
        elif enable_live and provider == "openai_compatible" and not is_functional:
            mode_label = "配置不完整"
        else:
            mode_label = "Mock AI"

        has_key = bool(api_key)
        masked_key = SettingsService.mask_secret(api_key) if api_key else ""

        return {
            "provider": provider,
            "enable_live": enable_live,
            "base_url": base_url or "",
            "model": model or "",
            "has_api_key": has_key,
            "masked_api_key": masked_key,
            "is_functional": is_functional,
            "mode_label": mode_label,
        }
