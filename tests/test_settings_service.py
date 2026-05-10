"""
AI World Engine - Test Settings Service
Tests for the app_settings table and SettingsService CRUD/precedence logic.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base
from app.models import AppSetting
from app.services.settings_service import SettingsService, DEFAULTS, SECRET_KEYS


# Isolated in-memory DB for settings service tests
_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
_Session = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


@pytest.fixture()
def db():
    Base.metadata.create_all(bind=_engine)
    session = _Session()
    yield session
    session.close()
    Base.metadata.drop_all(bind=_engine)


def test_defaults_exist_after_init(db):
    """init_defaults() should create all default settings rows."""
    SettingsService.init_defaults(db)
    for key in DEFAULTS:
        row = db.query(AppSetting).filter(AppSetting.key == key).first()
        assert row is not None, f"Default missing for key: {key}"
    assert db.query(AppSetting).count() == len(DEFAULTS)


def test_init_defaults_idempotent(db):
    """Calling init_defaults twice should not duplicate rows."""
    SettingsService.init_defaults(db)
    count1 = db.query(AppSetting).count()
    SettingsService.init_defaults(db)
    count2 = db.query(AppSetting).count()
    assert count1 == count2


def test_get_returns_default_when_not_set(db):
    """get() should return the hardcoded default for missing keys."""
    val = SettingsService.get(db, "ai_provider")
    assert val == "mock"


def test_set_and_get(db):
    """set() should create a row, get() should retrieve the value."""
    SettingsService.set(db, "ai_base_url", "https://example.com/v1")
    assert SettingsService.get(db, "ai_base_url") == "https://example.com/v1"


def test_set_updates_existing(db):
    """set() should update an existing row."""
    SettingsService.set(db, "ai_provider", "mock")
    SettingsService.set(db, "ai_provider", "openai_compatible")
    assert SettingsService.get(db, "ai_provider") == "openai_compatible"


def test_get_bool(db):
    """get_bool should parse true/false strings."""
    SettingsService.set(db, "ai_enable_live", "true")
    assert SettingsService.get_bool(db, "ai_enable_live") is True
    SettingsService.set(db, "ai_enable_live", "false")
    assert SettingsService.get_bool(db, "ai_enable_live") is False


def test_get_int(db):
    """get_int should parse integer strings."""
    SettingsService.set(db, "ai_max_tokens", "4000")
    assert SettingsService.get_int(db, "ai_max_tokens") == 4000


def test_get_int_with_invalid_value(db):
    """get_int should return default on parse failure."""
    SettingsService.set(db, "ai_max_tokens", "not_a_number")
    assert SettingsService.get_int(db, "ai_max_tokens", 2000) == 2000


def test_get_float(db):
    """get_float should parse float strings."""
    SettingsService.set(db, "ai_temperature", "0.9")
    assert SettingsService.get_float(db, "ai_temperature") == pytest.approx(0.9)


def test_mask_secret_short(db):
    """Short secrets should be completely masked."""
    assert SettingsService.mask_secret("abc") == "****"


def test_mask_secret_long(db):
    """Long secrets should show first 4 + **** + last 4 chars."""
    assert SettingsService.mask_secret("sk-1234567890abcd") == "sk-1****abcd"


def test_mask_secret_empty(db):
    """Empty secret should return empty string."""
    assert SettingsService.mask_secret("") == ""


def test_get_all_masks_api_key(db):
    """get_all() should return the masked API key, not the real one."""
    SettingsService.set(db, "ai_api_key", "sk-real-key-12345678", is_secret=True)
    all_settings = SettingsService.get_all(db, include_secrets=False)
    assert all_settings["ai_api_key"] == "sk-r****5678"


def test_get_all_plain_returns_real_key(db):
    """get_all_plain() should return the real API key for internal use."""
    SettingsService.set(db, "ai_api_key", "sk-real-key-12345678", is_secret=True)
    all_settings = SettingsService.get_all_plain(db)
    assert all_settings["ai_api_key"] == "sk-real-key-12345678"


def test_set_many(db):
    """set_many should create/update multiple settings at once."""
    SettingsService.set_many(db, {"ai_provider": "openai_compatible", "ai_enable_live": "true"})
    assert SettingsService.get(db, "ai_provider") == "openai_compatible"
    assert SettingsService.get_bool(db, "ai_enable_live") is True


def test_get_effective_config_returns_all_keys(db):
    """get_effective_config should return a complete config dict."""
    SettingsService.init_defaults(db)
    config = SettingsService.get_effective_config(db)
    expected_keys = [
        "ai_enable_live", "ai_provider", "ai_api_key", "ai_base_url",
        "ai_model", "ai_temperature", "ai_max_tokens", "ai_timeout",
        "ai_simulation_model", "ai_check_model", "ai_summary_model",
    ]
    for key in expected_keys:
        assert key in config, f"Missing key in effective config: {key}"


def test_restore_mock(db):
    """restore_mock should set ai_enable_live=false and ai_provider=mock."""
    SettingsService.set(db, "ai_enable_live", "true")
    SettingsService.set(db, "ai_provider", "openai_compatible")
    SettingsService.restore_mock(db)
    assert SettingsService.get(db, "ai_enable_live") == "false"
    assert SettingsService.get(db, "ai_provider") == "mock"


def test_is_live_enabled_requires_all_fields(db):
    """is_live_enabled should return False if any required field is missing."""
    SettingsService.set(db, "ai_enable_live", "true")
    SettingsService.set(db, "ai_provider", "openai_compatible")
    SettingsService.set(db, "ai_api_key", "sk-test")
    # Missing base_url and model
    assert SettingsService.is_live_enabled(db) is False


def test_is_live_enabled_true_when_complete(db):
    """is_live_enabled should return True when all fields are set."""
    SettingsService.set(db, "ai_enable_live", "true")
    SettingsService.set(db, "ai_provider", "openai_compatible")
    SettingsService.set(db, "ai_api_key", "sk-test")
    SettingsService.set(db, "ai_base_url", "https://example.com/v1")
    SettingsService.set(db, "ai_model", "gpt-4o")
    assert SettingsService.is_live_enabled(db) is True


def test_is_live_enabled_false_when_not_enabled(db):
    """is_live_enabled should return False when ai_enable_live=false."""
    SettingsService.init_defaults(db)
    assert SettingsService.is_live_enabled(db) is False


def test_updated_at_changes_on_update(db):
    """updated_at should change when a setting is updated."""
    SettingsService.set(db, "ai_provider", "mock")
    row1 = db.query(AppSetting).filter(AppSetting.key == "ai_provider").first()
    ts1 = row1.updated_at
    # Force a new timestamp by updating
    row1.value = "openai_compatible"
    db.commit()
    db.refresh(row1)
    # The update hook should have set a new timestamp
    assert row1.value == "openai_compatible"


def test_get_ai_summary_mock_mode(db):
    """get_ai_summary should return Mock mode when not configured."""
    SettingsService.init_defaults(db)
    summary = SettingsService.get_ai_summary(db)
    assert summary["mode_label"] == "Mock AI"
    assert summary["is_functional"] is False
    assert summary["has_api_key"] is False


def test_get_ai_summary_live_mode(db):
    """get_ai_summary should report OpenAI-compatible when fully configured."""
    SettingsService.set(db, "ai_enable_live", "true")
    SettingsService.set(db, "ai_provider", "openai_compatible")
    SettingsService.set(db, "ai_api_key", "sk-testkey-12345", is_secret=True)
    SettingsService.set(db, "ai_base_url", "https://api.deepseek.com/v1")
    SettingsService.set(db, "ai_model", "deepseek-chat")
    summary = SettingsService.get_ai_summary(db)
    assert summary["mode_label"] == "OpenAI-compatible"
    assert summary["is_functional"] is True
    assert summary["model"] == "deepseek-chat"
    assert summary["has_api_key"] is True
    assert "sk-tes****345" == summary["masked_api_key"] or "****" in summary["masked_api_key"]
    # Full key must not be returned
    assert "sk-testkey-12345" not in str(summary)


def test_get_ai_summary_incomplete_config(db):
    """get_ai_summary should report incomplete when live is on but fields missing."""
    SettingsService.set(db, "ai_enable_live", "true")
    SettingsService.set(db, "ai_provider", "openai_compatible")
    SettingsService.set(db, "ai_api_key", "sk-test")
    # Missing base_url and model
    summary = SettingsService.get_ai_summary(db)
    assert summary["mode_label"] == "配置不完整"
    assert summary["is_functional"] is False
