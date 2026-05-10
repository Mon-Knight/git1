"""
AI World Engine - Test Model Router
Tests for the ModelRouter routing logic and per-task model resolution.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base
from app.models import AppSetting
from app.services.settings_service import SettingsService
from app.services.ai.model_router import ModelRouter
from app.services.ai.mock_client import MockAIClient
from app.services.ai.openai_compatible_client import OpenAICompatibleClient


_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
_Session = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


@pytest.fixture()
def db():
    Base.metadata.create_all(bind=_engine)
    session = _Session()
    yield session
    session.close()
    Base.metadata.drop_all(bind=_engine)


def _setup_live_config(db, api_key="sk-test", base_url="https://api.example.com/v1", model="gpt-4o"):
    """Helper to configure live AI in the database."""
    SettingsService.set(db, "ai_enable_live", "true")
    SettingsService.set(db, "ai_provider", "openai_compatible")
    SettingsService.set(db, "ai_api_key", api_key)
    SettingsService.set(db, "ai_base_url", base_url)
    SettingsService.set(db, "ai_model", model)


def test_live_disabled_returns_mock(db):
    """When ai_enable_live=false, router should return MockAIClient."""
    SettingsService.init_defaults(db)
    client = ModelRouter.get_client(db, "simulation")
    assert isinstance(client, MockAIClient)


def test_provider_mock_returns_mock(db):
    """When provider=mock, router should return MockAIClient even if live is enabled."""
    SettingsService.set(db, "ai_enable_live", "true")
    SettingsService.set(db, "ai_provider", "mock")
    client = ModelRouter.get_client(db, "simulation")
    assert isinstance(client, MockAIClient)


def test_complete_config_returns_openai_client(db):
    """When live config is complete, router should return OpenAICompatibleClient."""
    _setup_live_config(db)
    client = ModelRouter.get_client(db, "simulation")
    assert isinstance(client, OpenAICompatibleClient)
    assert client.provider == "openai_compatible"


def test_incomplete_config_fallback_to_mock(db):
    """When live config is incomplete, router should fall back to MockAIClient."""
    SettingsService.set(db, "ai_enable_live", "true")
    SettingsService.set(db, "ai_provider", "openai_compatible")
    SettingsService.set(db, "ai_api_key", "sk-test")
    # Missing base_url and model
    client = ModelRouter.get_client(db, "simulation")
    assert isinstance(client, MockAIClient)


def test_simulation_uses_simulation_model(db):
    """Simulation task should use ai_simulation_model if set."""
    _setup_live_config(db)
    SettingsService.set(db, "ai_simulation_model", "custom-sim-model")
    client = ModelRouter.get_client(db, "simulation")
    assert client.model_name == "custom-sim-model"


def test_conflict_check_uses_check_model(db):
    """Conflict check task should use ai_check_model if set."""
    _setup_live_config(db)
    SettingsService.set(db, "ai_check_model", "custom-check-model")
    client = ModelRouter.get_client(db, "conflict_check")
    assert client.model_name == "custom-check-model"


def test_behavior_check_uses_check_model(db):
    """Behavior check task should use ai_check_model if set."""
    _setup_live_config(db)
    SettingsService.set(db, "ai_check_model", "check-special")
    client = ModelRouter.get_client(db, "behavior_check")
    assert client.model_name == "check-special"


def test_summary_uses_summary_model(db):
    """Summary task should use ai_summary_model if set."""
    _setup_live_config(db)
    SettingsService.set(db, "ai_summary_model", "summary-model")
    client = ModelRouter.get_client(db, "summary")
    assert client.model_name == "summary-model"


def test_task_model_fallback_to_default(db):
    """When task-specific model is empty, should fall back to ai_model."""
    _setup_live_config(db, model="default-model")
    # ai_simulation_model is empty by default
    client = ModelRouter.get_client(db, "simulation")
    assert client.model_name == "default-model"


def test_connection_test_uses_default_model(db):
    """Connection test should use the default model."""
    _setup_live_config(db, model="main-model")
    client = ModelRouter.get_client(db, "connection_test")
    assert client.model_name == "main-model"


def test_config_hint_mock_mode(db):
    """config_hint should describe mock mode clearly."""
    SettingsService.init_defaults(db)
    hint = ModelRouter.config_hint(db)
    assert "Mock" in hint


def test_config_hint_incomplete_config(db):
    """config_hint should list missing fields when config is incomplete."""
    SettingsService.set(db, "ai_enable_live", "true")
    SettingsService.set(db, "ai_provider", "openai_compatible")
    hint = ModelRouter.config_hint(db)
    assert "缺" in hint


def test_is_config_complete_mock(db):
    """is_config_complete should return True for mock mode."""
    SettingsService.init_defaults(db)
    assert ModelRouter.is_config_complete(db) is True


def test_is_config_complete_incomplete_live(db):
    """is_config_complete should return False when live config is incomplete."""
    SettingsService.set(db, "ai_enable_live", "true")
    SettingsService.set(db, "ai_provider", "openai_compatible")
    assert ModelRouter.is_config_complete(db) is False


def test_is_config_complete_full_live(db):
    """is_config_complete should return True when live config is complete."""
    _setup_live_config(db)
    assert ModelRouter.is_config_complete(db) is True
