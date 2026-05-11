"""
AI World Engine - Application Settings Service
Lightweight key-value settings stored in SQLite app_settings table.
Used for UI preferences, desktop window size, export defaults, etc.
Does NOT store API keys (those remain in the existing AI settings system).
"""

import os
import sys
import json
from pathlib import Path
from sqlalchemy.orm import Session
from app.models import AppSetting


class AppSettingsService:
    """Service for managing application-level settings (non-AI)."""

    # Default values for all known settings
    DEFAULTS = {
        "ui_sidebar_default_expanded": "true",
        "ui_compact_mode": "false",
        "desktop_default_width": "1280",
        "desktop_default_height": "820",
        "export_default_dir": "",
        "diagnostics_show_debug_info": "false",
    }

    # Valid ranges for numeric settings
    VALIDATORS = {
        "desktop_default_width": (1024, 2560),
        "desktop_default_height": (700, 1600),
    }

    @staticmethod
    def get(db: Session, key: str, default: str = "") -> str:
        """Get a setting value, falling back to DEFAULTS then the given default."""
        # Check DEFAULTS first
        fallback = AppSettingsService.DEFAULTS.get(key, default)

        row = db.query(AppSetting).filter_by(key=key).first()
        if row:
            return row.value
        return fallback

    @staticmethod
    def set(db: Session, key: str, value: str) -> None:
        """Set a setting value. Validates if applicable."""
        # Validate range
        if key in AppSettingsService.VALIDATORS:
            try:
                num = int(value)
                lo, hi = AppSettingsService.VALIDATORS[key]
                if num < lo or num > hi:
                    raise ValueError(f"{key} must be between {lo} and {hi}")
            except (TypeError, ValueError) as e:
                raise ValueError(f"Invalid value for {key}: {e}")

        row = db.query(AppSetting).filter_by(key=key).first()
        if row:
            row.value = value
        else:
            row = AppSetting(key=key, value=value)
            db.add(row)
        db.commit()

    @staticmethod
    def get_all(db: Session) -> dict:
        """Get all current settings as a dict with defaults filled."""
        result = dict(AppSettingsService.DEFAULTS)
        rows = db.query(AppSetting).all()
        for row in rows:
            result[row.key] = row.value
        return result

    @staticmethod
    def is_desktop_mode() -> bool:
        """Check if running in desktop/EXE mode."""
        try:
            sys._MEIPASS
            return True
        except AttributeError:
            return os.environ.get("AIWE_DESKTOP_MODE", "").lower() == "true"

    @staticmethod
    def get_window_size() -> tuple:
        """Get the configured default window size. Returns (width, height)."""
        width, height = 1280, 820
        if AppSettingsService.is_desktop_mode() or os.environ.get("AIWE_DESKTOP_MODE", "").lower() == "true":
            log_dir = os.environ.get("AIWE_LOG_DIR", "")
            if not log_dir:
                if os.name == "nt":
                    log_dir = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "AIWorldEngine", "logs")
                else:
                    log_dir = os.path.join(os.path.expanduser("~"), ".AIWorldEngine", "logs")
            settings_file = os.path.join(os.path.dirname(log_dir), "app_settings.json")
        else:
            settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "app_settings.json")

        try:
            if os.path.exists(settings_file):
                with open(settings_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                w = int(data.get("desktop_default_width", 1280))
                h = int(data.get("desktop_default_height", 820))
                w = max(1024, min(2560, w))
                h = max(700, min(1600, h))
                return (w, h)
        except (json.JSONDecodeError, ValueError, OSError):
            pass
        return (width, height)

    @staticmethod
    def save_window_size(width: int, height: int):
        """Save window size to the JSON settings file for desktop launcher to read."""
        if AppSettingsService.is_desktop_mode():
            log_dir = os.environ.get("AIWE_LOG_DIR", "")
            if not log_dir:
                if os.name == "nt":
                    log_dir = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "AIWorldEngine", "logs")
                else:
                    log_dir = os.path.join(os.path.expanduser("~"), ".AIWorldEngine", "logs")
            settings_file = os.path.join(os.path.dirname(log_dir), "app_settings.json")
        else:
            settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "app_settings.json")

        os.makedirs(os.path.dirname(settings_file), exist_ok=True)
        try:
            data = {}
            if os.path.exists(settings_file):
                with open(settings_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            data["desktop_default_width"] = str(width)
            data["desktop_default_height"] = str(height)
            with open(settings_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except (OSError, json.JSONDecodeError):
            pass
