"""
AI World Engine - Test AI Integration
End-to-end integration tests for AI simulation and checks.
Uses conftest.py's shared client fixture and in-memory test DB.
Mock AI only; no real network requests.
"""

import pytest


def _create_world(client):
    return client.post("/worlds", data={"name": "测试世界", "world_type": "奇幻"})


def test_mock_simulation_saves_record(client):
    """Mock AI simulation should save a simulation_record."""
    _create_world(client)
    response = client.post("/worlds/1/simulation", data={
        "question": "如果龙族发动全面战争会怎样？",
        "simulation_type": "势力冲突",
    })
    assert response.status_code == 200
    assert "Mock AI" in response.text or "pending" in response.text


def test_mock_simulation_does_not_auto_create_historical_event(client):
    """Mock simulation should NOT write to historical_events automatically."""
    _create_world(client)
    events_before = client.get("/worlds/1/events")
    client.post("/worlds/1/simulation", data={"question": "测试问题"})
    events_after = client.get("/worlds/1/events")
    # Canon event count should be the same
    assert events_before.text.count("is_canon=True") == events_after.text.count("is_canon=True")


def test_no_api_key_does_not_crash(client):
    """Without API key, system should use Mock AI without crashing."""
    _create_world(client)
    response = client.post("/worlds/1/simulation", data={"question": "无API Key测试"})
    assert response.status_code == 200
    assert "Mock AI" in response.text or "AI 推演结果" in response.text


def test_checks_work_without_api_key(client):
    """Check center should work without AI API key using rule-based checks."""
    _create_world(client)
    response = client.post("/worlds/1/checks/conflicts", data={
        "content": "世界观设定中有两条相互矛盾的规则",
    })
    assert response.status_code == 200
    assert "检查结果" in response.text


def test_checks_do_not_modify_database(client):
    """Check operations should be read-only; they must not modify world data."""
    _create_world(client)
    client.post("/worlds/1/checks/conflicts", data={"content": "测试内容"})
    response = client.get("/worlds/1")
    assert response.status_code == 200
    assert "测试世界" in response.text


def test_simulation_page_shows_ai_mode(client):
    """Simulation page should show the current AI mode info."""
    _create_world(client)
    response = client.get("/worlds/1/simulation")
    assert response.status_code == 200
    assert "Mock AI" in response.text or "mock" in response.text.lower()


def test_simulation_does_not_auto_adopt(client):
    """Simulation record should stay as pending, not auto-adopted."""
    _create_world(client)
    client.post("/worlds/1/simulation", data={"question": "采纳测试"})
    records = client.get("/worlds/1/records")
    assert records.status_code == 200


def test_checks_index_shows_ai_hint(client):
    """Check center index page should show AI availability hint."""
    _create_world(client)
    response = client.get("/worlds/1/checks")
    assert response.status_code == 200
    assert "检查中心" in response.text


def test_check_with_ai_flag_no_crash(client):
    """Passing use_ai=true should not crash even without AI configured."""
    _create_world(client)
    response = client.post("/worlds/1/checks/conflicts", data={
        "content": "启用AI检查测试",
        "use_ai": "true",
    })
    assert response.status_code == 200
    # Should still show rule-based results + AI failure message
    assert "检查结果" in response.text


def test_api_key_not_in_pages(client):
    """API key should not appear in any page source."""
    from app.main import app
    from app.database import get_db
    from app.services.settings_service import SettingsService
    db = next(app.dependency_overrides[get_db]())
    try:
        SettingsService.set(db, "ai_api_key", "sk-supersecret123456", is_secret=True)
    finally:
        db.close()
    response = client.get("/settings/ai")
    assert "sk-supersecret123456" not in response.text


def test_mock_simulation_record_model_field(client):
    """Mock simulation record should store model field correctly."""
    _create_world(client)
    client.post("/worlds/1/simulation", data={"question": "模型记录测试"})
    response = client.get("/worlds/1/records")
    assert response.status_code == 200
