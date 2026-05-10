"""
AI World Engine - Test Desktop AI Settings
Tests for AI configuration persistence in desktop mode, API key masking,
mock mode, and config survival after restart.
"""

import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import AppSetting
from app.services.settings_service import SettingsService


_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
_Session = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


@pytest.fixture()
def db():
    Base.metadata.create_all(bind=_engine)
    session = _Session()
    yield session
    session.close()
    Base.metadata.drop_all(bind=_engine)


def test_desktop_config_saves_mock_mode(db):
    """After saving Mock mode config, it should be retrievable."""
    SettingsService.init_defaults(db)
    SettingsService.set(db, "ai_enable_live", "false")
    SettingsService.set(db, "ai_provider", "mock")
    assert SettingsService.get(db, "ai_enable_live") == "false"
    assert SettingsService.get(db, "ai_provider") == "mock"


def test_desktop_config_saves_openai_compatible(db):
    """OpenAI-compatible config should save and persist."""
    SettingsService.init_defaults(db)
    SettingsService.set(db, "ai_enable_live", "true")
    SettingsService.set(db, "ai_provider", "openai_compatible")
    SettingsService.set(db, "ai_api_key", "sk-desktop-test-key-12345", is_secret=True)
    SettingsService.set(db, "ai_base_url", "https://api.deepseek.com/v1")
    SettingsService.set(db, "ai_model", "deepseek-chat")

    assert SettingsService.get(db, "ai_enable_live") == "true"
    assert SettingsService.get(db, "ai_provider") == "openai_compatible"
    assert SettingsService.get(db, "ai_base_url") == "https://api.deepseek.com/v1"
    assert SettingsService.get(db, "ai_model") == "deepseek-chat"


def test_desktop_api_key_masked_in_get_all(db):
    """get_all() should mask the API key for display."""
    SettingsService.set(db, "ai_api_key", "sk-desktop-mask-test-12345", is_secret=True)
    all_settings = SettingsService.get_all(db, include_secrets=False)
    masked = all_settings.get("ai_api_key", "")
    assert "sk-desktop-mask-test-12345" not in masked
    assert "****" in masked


def test_desktop_api_key_readable_in_plain(db):
    """get_all_plain() should return the real API key (for internal use)."""
    SettingsService.set(db, "ai_api_key", "sk-desktop-internal-use-12345", is_secret=True)
    all_plain = SettingsService.get_all_plain(db)
    assert all_plain["ai_api_key"] == "sk-desktop-internal-use-12345"


def test_desktop_config_survives_simulated_restart(db):
    """
    Config should persist across 'restarts'.
    Simulate by reusing same DB session (representing the persistent SQLite file).
    """
    SettingsService.init_defaults(db)
    SettingsService.set(db, "ai_enable_live", "true")
    SettingsService.set(db, "ai_provider", "openai_compatible")
    SettingsService.set(db, "ai_api_key", "sk-persist-key-abc", is_secret=True)
    SettingsService.set(db, "ai_base_url", "https://token-plan-cn.xiaomimimo.com/v1")
    SettingsService.set(db, "ai_model", "mimo-large")
    SettingsService.set(db, "ai_simulation_model", "mimo-sim")
    SettingsService.set(db, "ai_temperature", "0.8")

    # Simulate restart: read from same session
    config = SettingsService.get_effective_config(db)
    assert config["ai_enable_live"] is True
    assert config["ai_provider"] == "openai_compatible"
    assert config["ai_api_key"] == "sk-persist-key-abc"
    assert config["ai_base_url"] == "https://token-plan-cn.xiaomimimo.com/v1"
    assert config["ai_model"] == "mimo-large"
    assert config["ai_simulation_model"] == "mimo-sim"
    assert config["ai_temperature"] == pytest.approx(0.8)


def test_desktop_is_live_enabled_positive(db):
    """Should return True when live is fully configured."""
    SettingsService.set(db, "ai_enable_live", "true")
    SettingsService.set(db, "ai_provider", "openai_compatible")
    SettingsService.set(db, "ai_api_key", "sk-key")
    SettingsService.set(db, "ai_base_url", "https://api.test.com/v1")
    SettingsService.set(db, "ai_model", "test-model")
    assert SettingsService.is_live_enabled(db) is True


def test_desktop_is_live_enabled_negative(db):
    """Should return False when enable_live is false."""
    SettingsService.init_defaults(db)
    assert SettingsService.is_live_enabled(db) is False


def test_desktop_mask_secret_short():
    """Short secrets should be completely masked."""
    assert SettingsService.mask_secret("abc") == "****"


def test_desktop_mask_secret_long():
    """Long secrets should show first 4 + **** + last 4."""
    assert SettingsService.mask_secret("sk-1234567890abcd") == "sk-1****abcd"


def test_desktop_mask_secret_exact_8():
    """Exact 8 chars should be completely masked."""
    assert SettingsService.mask_secret("12345678") == "****"


def test_desktop_mask_secret_9_chars():
    """9 chars should use first4+last4 with ****."""
    assert SettingsService.mask_secret("123456789") == "1234****6789"


def test_desktop_restore_mock(db):
    """restore_mock() should disable live mode."""
    SettingsService.set(db, "ai_enable_live", "true")
    SettingsService.set(db, "ai_provider", "openai_compatible")
    SettingsService.restore_mock(db)
    assert SettingsService.get(db, "ai_enable_live") == "false"
    assert SettingsService.get(db, "ai_provider") == "mock"
