"""
Tests for the AI Service module.
"""

from app.services.ai_service import AIService


def test_ai_service_instantiation():
    """Test that AIService can be instantiated."""
    service = AIService()
    assert service is not None


def test_ai_service_has_is_mock_property():
    """Test that AIService has is_mock property."""
    service = AIService()
    assert hasattr(service, "is_mock")
    # Without API key, it should be mock mode
    assert service.is_mock is True


def test_mock_simulation_returns_string():
    """Test that mock simulation returns a non-empty string."""
    service = AIService()
    context = {
        "world_name": "测试世界",
        "world_type": "奇幻",
        "characters": [{"name": "测试角色", "role": "战士"}],
        "factions": [{"name": "测试势力", "faction_type": "王国"}],
    }
    result = service._mock_simulation(context, "如果战争爆发会怎样？")
    assert isinstance(result, str)
    assert len(result) > 0
    assert "Mock AI" in result


def test_mock_simulation_includes_world_name():
    """Test that mock simulation includes the world name."""
    service = AIService()
    context = {"world_name": "中土世界"}
    result = service._mock_simulation(context, "测试问题")
    assert "中土世界" in result


def test_mock_simulation_includes_question():
    """Test that mock simulation references the question."""
    service = AIService()
    context = {"world_name": "测试"}
    result = service._mock_simulation(context, "龙族是否会灭绝？")
    assert "龙族是否会灭绝" in result


def test_generate_simulation_uses_mock_when_no_api_key():
    """Test that generate_simulation uses mock when no API key is set."""
    service = AIService()
    result = service.generate_simulation({"world_name": "测试"}, "问题")
    assert "Mock AI" in result


def test_build_prompt_includes_context():
    """Test that _build_prompt includes world context."""
    service = AIService()
    context = {
        "world_name": "艾泽拉斯",
        "world_type": "奇幻",
        "current_era": "第三纪元",
        "tone": "史诗",
        "characters": [{"name": "阿尔萨斯", "role": "王子", "personality": "骄傲"}],
        "factions": [{"name": "洛丹伦", "faction_type": "王国", "goal": "和平"}],
    }
    prompt = service._build_prompt(context, "测试")
    assert "艾泽拉斯" in prompt
    assert "奇幻" in prompt
    assert "阿尔萨斯" in prompt
    assert "洛丹伦" in prompt
