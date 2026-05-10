"""
AI World Engine - Test Novel Prompt Builder
Tests for PromptBuilder.build_novel_evolution_prompt.
"""

from app.services.ai.prompt_builder import PromptBuilder


def test_build_novel_evolution_prompt_exists():
    assert hasattr(PromptBuilder, "build_novel_evolution_prompt")


def test_build_novel_returns_messages():
    world_ctx = {"world_name": "测试世界", "world_type": "奇幻"}
    result = PromptBuilder.build_novel_evolution_prompt(world_ctx, {"main_story_direction": "主线"})
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["role"] == "system"
    assert result[1]["role"] == "user"


def test_novel_prompt_contains_world_context():
    world_ctx = {"world_name": "中土世界", "world_type": "奇幻"}
    result = PromptBuilder.build_novel_evolution_prompt(world_ctx, {"main_story_direction": "test"})
    user_msg = result[1]["content"]
    assert "中土世界" in user_msg
    assert "奇幻" in user_msg


def test_novel_prompt_contains_protagonist_info():
    world_ctx = {"world_name": "test"}
    novel_form = {
        "protagonist_name": "林楚",
        "protagonist_identity": "穿越者",
        "protagonist_power": "AI系统",
        "protagonist_start": "边陲小镇",
    }
    result = PromptBuilder.build_novel_evolution_prompt(world_ctx, novel_form)
    user_msg = result[1]["content"]
    assert "林楚" in user_msg
    assert "穿越者" in user_msg
    assert "AI系统" in user_msg


def test_novel_prompt_contains_direction():
    world_ctx = {"world_name": "test"}
    novel_form = {"main_story_direction": "探索世界法则真相"}
    result = PromptBuilder.build_novel_evolution_prompt(world_ctx, novel_form)
    user_msg = result[1]["content"]
    assert "探索世界法则真相" in user_msg


def test_novel_prompt_contains_style():
    world_ctx = {"world_name": "test"}
    novel_form = {"writing_style": "理性克制", "main_story_direction": "test"}
    result = PromptBuilder.build_novel_evolution_prompt(world_ctx, novel_form)
    user_msg = result[1]["content"]
    assert "理性克制" in user_msg


def test_novel_prompt_system_no_auto_canon():
    system_msg = PromptBuilder.NOVEL_SYSTEM
    assert "不能直接推翻" in system_msg or "替用户决定正史" in system_msg


def test_novel_prompt_system_no_prose():
    system_msg = PromptBuilder.NOVEL_SYSTEM
    assert "正文" in system_msg
    assert "全书演化方向" in system_msg


def test_novel_prompt_no_api_key():
    world_ctx = {"world_name": "test"}
    novel_form = {"main_story_direction": "test", "protagonist_name": "sk-fakekey12345"}
    result = PromptBuilder.build_novel_evolution_prompt(world_ctx, novel_form)
    user_msg = result[1]["content"]
    # The key should appear since it's in the form, but we check system prompt doesn't leak anything
    assert result[0]["content"] == PromptBuilder.NOVEL_SYSTEM


def test_novel_prompt_with_characters():
    world_ctx = {
        "world_name": "test",
        "characters": [
            {"name": "Alice", "role": "法师", "personality": "聪明冷静", "goal": "探索真理"},
            {"name": "Bob", "role": "战士", "personality": "忠厚", "goal": "保护家人"},
        ],
    }
    novel_form = {"main_story_direction": "test"}
    result = PromptBuilder.build_novel_evolution_prompt(world_ctx, novel_form)
    user_msg = result[1]["content"]
    assert "Alice" in user_msg
    assert "Bob" in user_msg


def test_novel_prompt_with_events():
    world_ctx = {
        "world_name": "test",
        "canon_events": [
            {"title": "诸神黄昏", "content": "远古大战导致文明崩塌"},
        ],
    }
    novel_form = {"main_story_direction": "test"}
    result = PromptBuilder.build_novel_evolution_prompt(world_ctx, novel_form)
    user_msg = result[1]["content"]
    assert "诸神黄昏" in user_msg


def test_novel_prompt_with_rules():
    world_ctx = {
        "world_name": "test",
        "rules": [{"name": "等价交换", "content": "魔法使用必须消耗等价的生命力"}],
    }
    novel_form = {"main_story_direction": "test"}
    result = PromptBuilder.build_novel_evolution_prompt(world_ctx, novel_form)
    user_msg = result[1]["content"]
    assert "等价交换" in user_msg
    assert "生命力" in user_msg
