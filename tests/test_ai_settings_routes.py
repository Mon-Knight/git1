"""
AI World Engine - Test AI Settings Routes
Tests for /settings/ai GET, POST, POST /settings/ai/test.

Uses conftest.py's shared client fixture (in-memory test DB).
"""

import pytest


def test_get_ai_settings_returns_200(client):
    """GET /settings/ai should return 200."""
    response = client.get("/settings/ai")
    assert response.status_code == 200
    assert "AI 设置" in response.text


def test_page_contains_settings_form(client):
    """AI settings page should contain a form."""
    response = client.get("/settings/ai")
    assert "ai_provider" in response.text
    assert "ai_base_url" in response.text


def test_page_does_not_show_full_api_key(client):
    """AI settings page should never show a full API key."""
    from app.database import SessionLocal
    from app.services.settings_service import SettingsService as SS
    from app.database import get_db
    from app.main import app
    # Use the overridden session
    db = next(app.dependency_overrides[get_db]())
    try:
        SS.init_defaults(db)
        SS.set(db, "ai_api_key", "sk-verysecretkey-abcdef", is_secret=True)
    finally:
        db.close()
    response = client.get("/settings/ai")
    assert "sk-verysecretkey-abcdef" not in response.text
    assert "****" in response.text


def test_post_save_settings(client):
    """POST /settings/ai should save configuration."""
    response = client.post("/settings/ai", data={
        "ai_provider": "openai_compatible",
        "ai_enable_live": "true",
        "ai_base_url": "https://api.deepseek.com/v1",
        "ai_model": "deepseek-chat",
        "ai_api_key": "sk-testkey-12345678",
        "ai_temperature": "0.7",
        "ai_max_tokens": "2000",
        "ai_timeout": "60",
        "ai_simulation_model": "",
        "ai_check_model": "",
        "ai_summary_model": "",
        "action": "save",
    }, follow_redirects=False)
    assert response.status_code == 200
    assert "配置已保存" in response.text


def test_post_save_invalid_temperature(client):
    """Invalid temperature should produce validation error."""
    response = client.post("/settings/ai", data={
        "ai_provider": "mock",
        "ai_enable_live": "",
        "ai_base_url": "",
        "ai_model": "",
        "ai_api_key": "",
        "ai_temperature": "99",
        "ai_max_tokens": "2000",
        "ai_timeout": "60",
        "action": "save",
    })
    assert response.status_code == 422 or "Temperature 必须在 0 到 2 之间" in response.text


def test_post_test_connection_mock_mode(client):
    """POST /settings/ai/test in mock mode should succeed."""
    response = client.post("/settings/ai/test")
    assert response.status_code == 200
    assert "Mock AI" in response.text


def test_post_restore_mock(client):
    """POST with action=restore_mock should disable live AI."""
    client.post("/settings/ai", data={
        "ai_provider": "openai_compatible",
        "ai_enable_live": "true",
        "ai_base_url": "https://test.com/v1",
        "ai_model": "test",
        "ai_api_key": "sk-test",
        "ai_temperature": "0.7",
        "ai_max_tokens": "2000",
        "ai_timeout": "60",
        "action": "save",
    })
    response = client.post("/settings/ai", data={"action": "restore_mock"})
    assert response.status_code == 200
    assert "Mock AI 模式" in response.text


def test_page_has_ai_settings_link_in_home(client):
    """The home page should have an AI settings link."""
    response = client.get("/")
    assert "/settings/ai" in response.text


def test_page_shows_current_mode_info(client):
    """AI settings page should show current mode info."""
    response = client.get("/settings/ai")
    assert "Mock AI" in response.text or "Mock 模式" in response.text


def test_openai_compatible_requires_fields(client):
    """Enabling live AI with openai_compatible should require base_url and model."""
    response = client.post("/settings/ai", data={
        "ai_provider": "openai_compatible",
        "ai_enable_live": "true",
        "ai_base_url": "",
        "ai_model": "",
        "ai_api_key": "sk-test",
        "ai_temperature": "0.7",
        "ai_max_tokens": "2000",
        "ai_timeout": "60",
        "action": "save",
    })
    assert response.status_code == 422
    assert "Base URL 不能为空" in response.text or "Model 不能为空" in response.text


def test_empty_max_tokens_validation(client):
    """Invalid max_tokens should produce error."""
    response = client.post("/settings/ai", data={
        "ai_provider": "mock",
        "ai_enable_live": "",
        "ai_base_url": "",
        "ai_model": "",
        "ai_api_key": "",
        "ai_temperature": "0.7",
        "ai_max_tokens": "100",
        "ai_timeout": "60",
        "action": "save",
    })
    assert response.status_code == 422
    assert "Max Tokens" in response.text
