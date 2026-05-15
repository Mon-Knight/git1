"""
AI World Engine - Test Chapter Outline Service
Tests for ChapterOutlineService.
"""

import json
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base

_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
_Session = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


@pytest.fixture()
def db():
    Base.metadata.create_all(bind=_engine)
    session = _Session()
    yield session
    session.rollback()
    session.close()
    Base.metadata.drop_all(bind=_engine)


from app.models import World, Character, Faction, Location, WorldRule, HistoricalEvent, NovelVolumeOutline
from app.services.world_service import WorldService
from app.services.chapter_outline_service import ChapterOutlineService


def _create_world(db) -> World:
    return WorldService.create_world(db, name="测试世界", world_type="奇幻")


def _create_volume_outline(db, world_id: int, is_main: bool = True) -> NovelVolumeOutline:
    vo = NovelVolumeOutline(
        world_id=world_id,
        title="测试分卷方案",
        volume_count=3,
        result_json=json.dumps({
            "title": "测试分卷方案",
            "summary": "测试用分卷大纲",
            "volume_count": 3,
            "volumes": [
                {
                    "volume_index": 1,
                    "title": "第一卷：觉醒",
                    "core_theme": "觉醒与成长",
                    "main_conflict": "外部威胁",
                    "protagonist_goal": "成为强者",
                    "key_characters": ["主角", "导师"],
                    "key_factions": ["正义联盟"],
                    "key_locations": ["主城"],
                    "major_events": ["事件A", "事件B"],
                    "turning_point": "关键转折",
                    "ending_hook": "下一卷伏笔",
                    "estimated_chapters": 15,
                },
                {
                    "volume_index": 2,
                    "title": "第二卷：远征",
                    "core_theme": "远征与发现",
                    "main_conflict": "文化冲突",
                    "protagonist_goal": "探索未知",
                    "key_characters": ["主角", "新盟友"],
                    "key_factions": ["远征军"],
                    "key_locations": ["边境"],
                    "major_events": ["事件C", "事件D"],
                    "turning_point": "转折点2",
                    "ending_hook": "伏笔2",
                    "estimated_chapters": 20,
                },
                {
                    "volume_index": 3,
                    "title": "第三卷：决战",
                    "core_theme": "决战与新生",
                    "main_conflict": "终极对抗",
                    "protagonist_goal": "拯救世界",
                    "key_characters": ["主角", "最终反派"],
                    "key_factions": ["全势力"],
                    "key_locations": ["最终战场"],
                    "major_events": ["事件E", "事件F"],
                    "turning_point": "最终转折",
                    "ending_hook": "结局",
                    "estimated_chapters": 25,
                },
            ],
        }, ensure_ascii=False),
        status="main",
        is_main=is_main,
        prompt="测试prompt",
    )
    db.add(vo)
    db.commit()
    db.refresh(vo)
    return vo


class TestChapterOutlinePromptBuilding:
    """Tests for build_chapter_outline_prompt."""

    def test_prompt_contains_world_name(self, db):
        w = _create_world(db)
        vo = _create_volume_outline(db, w.id)
        prompt = ChapterOutlineService.build_chapter_outline_prompt(
            db, w.id, vo.id, volume_index=1
        )
        assert "测试世界" in prompt

    def test_prompt_contains_volume_outline(self, db):
        w = _create_world(db)
        vo = _create_volume_outline(db, w.id)
        prompt = ChapterOutlineService.build_chapter_outline_prompt(
            db, w.id, vo.id, volume_index=1
        )
        assert "测试分卷方案" in prompt

    def test_prompt_contains_selected_volume_title(self, db):
        w = _create_world(db)
        vo = _create_volume_outline(db, w.id)
        prompt = ChapterOutlineService.build_chapter_outline_prompt(
            db, w.id, vo.id, volume_index=1
        )
        assert "第一卷：觉醒" in prompt or "觉醒" in prompt

    def test_prompt_contains_selected_volume_conflict(self, db):
        w = _create_world(db)
        vo = _create_volume_outline(db, w.id)
        prompt = ChapterOutlineService.build_chapter_outline_prompt(
            db, w.id, vo.id, volume_index=1
        )
        assert "外部威胁" in prompt

    def test_prompt_contains_adopted_characters(self, db):
        w = _create_world(db)
        c = Character(world_id=w.id, name="测试角色", role="主角", personality="勇敢")
        db.add(c)
        db.commit()
        vo = _create_volume_outline(db, w.id)
        prompt = ChapterOutlineService.build_chapter_outline_prompt(
            db, w.id, vo.id, volume_index=1
        )
        assert "测试角色" in prompt

    def test_prompt_contains_adopted_factions(self, db):
        w = _create_world(db)
        f = Faction(world_id=w.id, name="测试势力", faction_type="王国")
        db.add(f)
        db.commit()
        vo = _create_volume_outline(db, w.id)
        prompt = ChapterOutlineService.build_chapter_outline_prompt(
            db, w.id, vo.id, volume_index=1
        )
        assert "测试势力" in prompt

    def test_prompt_contains_adopted_locations(self, db):
        w = _create_world(db)
        l = Location(world_id=w.id, name="测试地点", location_type="城市")
        db.add(l)
        db.commit()
        vo = _create_volume_outline(db, w.id)
        prompt = ChapterOutlineService.build_chapter_outline_prompt(
            db, w.id, vo.id, volume_index=1
        )
        assert "测试地点" in prompt

    def test_prompt_contains_adopted_rules(self, db):
        w = _create_world(db)
        r = WorldRule(world_id=w.id, name="测试规则", rule_type="魔法", content="魔力体系")
        db.add(r)
        db.commit()
        vo = _create_volume_outline(db, w.id)
        prompt = ChapterOutlineService.build_chapter_outline_prompt(
            db, w.id, vo.id, volume_index=1
        )
        assert "测试规则" in prompt

    def test_prompt_forbids_generating_text(self, db):
        """System prompt should forbid generating full text."""
        sys_prompt = ChapterOutlineService.CHAPTER_SYSTEM_PROMPT
        assert "不生成正文" in sys_prompt

    def test_prompt_states_candidate_nature(self, db):
        """System prompt should state that output is candidate only."""
        sys_prompt = ChapterOutlineService.CHAPTER_SYSTEM_PROMPT
        assert "候选" in sys_prompt


class TestMockGeneration:
    """Tests for mock chapter outline generation."""

    def test_mock_returns_structured_data(self, db):
        w = _create_world(db)
        vo = _create_volume_outline(db, w.id)
        result = ChapterOutlineService.generate_chapter_outline(
            db, w.id, vo.id, volume_index=1, chapter_count=8
        )
        assert "result_json" in result
        assert "prompt" in result
        data = json.loads(result["result_json"])
        assert "chapters" in data
        assert len(data["chapters"]) == 8

    def test_mock_chapters_have_complete_fields(self, db):
        w = _create_world(db)
        vo = _create_volume_outline(db, w.id)
        result = ChapterOutlineService.generate_chapter_outline(
            db, w.id, vo.id, volume_index=1, chapter_count=8
        )
        data = json.loads(result["result_json"])
        ch = data["chapters"][0]
        required_fields = ["chapter_index", "title", "chapter_goal", "main_conflict",
                          "pov_character", "key_characters", "key_locations",
                          "plot_events", "emotional_beat", "foreshadowing",
                          "ending_hook", "estimated_words", "notes"]
        for field in required_fields:
            assert field in ch, f"Missing field: {field}"

    def test_mock_minimum_8_chapters(self, db):
        w = _create_world(db)
        vo = _create_volume_outline(db, w.id)
        result = ChapterOutlineService.generate_chapter_outline(
            db, w.id, vo.id, volume_index=1, chapter_count=5
        )
        data = json.loads(result["result_json"])
        # chapter_count=5 is clamped to min 8
        assert len(data["chapters"]) >= 8

    def test_mock_generates_chinese_content(self, db):
        w = _create_world(db)
        vo = _create_volume_outline(db, w.id)
        result = ChapterOutlineService.generate_chapter_outline(
            db, w.id, vo.id, volume_index=1, chapter_count=8
        )
        data = json.loads(result["result_json"])
        # Mock titles should contain Chinese characters
        has_chinese = any('\u4e00' <= c <= '\u9fff' for c in data["chapters"][0]["title"])
        assert has_chinese


class TestParseResponse:
    """Tests for parse_chapter_outline_response."""

    def test_parse_valid_json(self, db):
        raw = '{"title":"测试","chapters":[{"chapter_index":1,"title":"第一章"}]}'
        result = ChapterOutlineService.parse_response(raw)
        assert isinstance(result, dict)
        assert result["title"] == "测试"

    def test_parse_non_json_fallback(self, db):
        raw = "这不是JSON格式的文本"
        result = ChapterOutlineService.parse_response(raw)
        assert isinstance(result, dict)
        assert result.get("parse_error") is True

    def test_parse_json_with_markdown_wrapper(self, db):
        raw = '```json\n{"title":"测试","chapters":[]}\n```'
        result = ChapterOutlineService.parse_response(raw)
        assert isinstance(result, dict)
        assert result["title"] == "测试"


class TestSaveAndList:
    """Tests for save and list operations."""

    def test_save_chapter_outline(self, db):
        w = _create_world(db)
        vo = _create_volume_outline(db, w.id)
        co = ChapterOutlineService.save_chapter_outline(
            db, w.id, volume_outline_id=vo.id, volume_index=1,
            prompt="测试prompt",
            result_json='{"title":"测试章节","chapters":[]}',
            chapter_count=8,
        )
        assert co.id is not None
        assert co.world_id == w.id
        assert co.status == "candidate"

    def test_list_only_returns_current_world(self, db):
        w1 = _create_world(db)
        w2 = WorldService.create_world(db, name="世界2", world_type="科幻")
        vo1 = _create_volume_outline(db, w1.id)
        vo2 = _create_volume_outline(db, w2.id)

        ChapterOutlineService.save_chapter_outline(
            db, w1.id, volume_outline_id=vo1.id, volume_index=1,
            prompt="p", result_json='{"title":"t1"}', chapter_count=8,
        )
        ChapterOutlineService.save_chapter_outline(
            db, w2.id, volume_outline_id=vo2.id, volume_index=1,
            prompt="p", result_json='{"title":"t2"}', chapter_count=10,
        )

        list1 = ChapterOutlineService.list_chapter_outlines(db, w1.id)
        list2 = ChapterOutlineService.list_chapter_outlines(db, w2.id)

        assert len(list1) == 1
        assert len(list2) == 1
        assert list1[0].world_id == w1.id
        assert list2[0].world_id == w2.id

    def test_get_chapter_outline_prevents_cross_world(self, db):
        w1 = _create_world(db)
        w2 = WorldService.create_world(db, name="世界2", world_type="科幻")
        vo1 = _create_volume_outline(db, w1.id)
        vo2 = _create_volume_outline(db, w2.id)

        co1 = ChapterOutlineService.save_chapter_outline(
            db, w1.id, volume_outline_id=vo1.id, volume_index=1,
            prompt="p", result_json='{"title":"t1"}', chapter_count=8,
        )

        # Try to access from wrong world
        result = ChapterOutlineService.get_chapter_outline(db, w2.id, co1.id)
        assert result is None

        # Access from correct world
        result = ChapterOutlineService.get_chapter_outline(db, w1.id, co1.id)
        assert result is not None
        assert result.id == co1.id


class TestSetMain:
    """Tests for set_main_chapter_outline."""

    def test_set_main_sets_status(self, db):
        w = _create_world(db)
        vo = _create_volume_outline(db, w.id)
        co = ChapterOutlineService.save_chapter_outline(
            db, w.id, volume_outline_id=vo.id, volume_index=1,
            prompt="p", result_json='{"title":"t1"}', chapter_count=8,
        )
        assert co.status == "candidate"

        ChapterOutlineService.set_main_chapter_outline(db, w.id, co.id)
        db.refresh(co)
        assert co.status == "main"
        assert co.is_main is True

    def test_only_one_main_per_world_volume(self, db):
        w = _create_world(db)
        vo = _create_volume_outline(db, w.id)

        co1 = ChapterOutlineService.save_chapter_outline(
            db, w.id, volume_outline_id=vo.id, volume_index=1,
            prompt="p1", result_json='{"title":"t1"}', chapter_count=8,
        )
        co2 = ChapterOutlineService.save_chapter_outline(
            db, w.id, volume_outline_id=vo.id, volume_index=1,
            prompt="p2", result_json='{"title":"t2"}', chapter_count=10,
        )

        ChapterOutlineService.set_main_chapter_outline(db, w.id, co1.id)
        db.refresh(co1)
        assert co1.is_main is True

        ChapterOutlineService.set_main_chapter_outline(db, w.id, co2.id)
        db.refresh(co1)
        db.refresh(co2)
        assert co1.is_main is False  # Old main unset
        assert co2.is_main is True   # New main set

    def test_different_volumes_can_each_have_main(self, db):
        w = _create_world(db)
        vo = _create_volume_outline(db, w.id)

        co1 = ChapterOutlineService.save_chapter_outline(
            db, w.id, volume_outline_id=vo.id, volume_index=1,
            prompt="p1", result_json='{"title":"v1"}', chapter_count=8,
        )
        co2 = ChapterOutlineService.save_chapter_outline(
            db, w.id, volume_outline_id=vo.id, volume_index=2,
            prompt="p2", result_json='{"title":"v2"}', chapter_count=10,
        )

        ChapterOutlineService.set_main_chapter_outline(db, w.id, co1.id)
        ChapterOutlineService.set_main_chapter_outline(db, w.id, co2.id)

        db.refresh(co1)
        db.refresh(co2)
        assert co1.is_main is True  # Different volumes, both can be main
        assert co2.is_main is True

    def test_discarded_cannot_be_main(self, db):
        w = _create_world(db)
        vo = _create_volume_outline(db, w.id)
        co = ChapterOutlineService.save_chapter_outline(
            db, w.id, volume_outline_id=vo.id, volume_index=1,
            prompt="p", result_json='{"title":"t1"}', chapter_count=8,
        )
        ChapterOutlineService.discard_chapter_outline(db, w.id, co.id)

        with pytest.raises(ValueError, match="已废弃"):
            ChapterOutlineService.set_main_chapter_outline(db, w.id, co.id)


class TestDiscard:
    """Tests for discard_chapter_outline."""

    def test_discard_sets_status(self, db):
        w = _create_world(db)
        vo = _create_volume_outline(db, w.id)
        co = ChapterOutlineService.save_chapter_outline(
            db, w.id, volume_outline_id=vo.id, volume_index=1,
            prompt="p", result_json='{"title":"t1"}', chapter_count=8,
        )
        ChapterOutlineService.discard_chapter_outline(db, w.id, co.id)
        db.refresh(co)
        assert co.status == "discarded"
        assert co.is_main is False


class TestUpdate:
    """Tests for update_chapter_outline."""

    def test_update_title(self, db):
        w = _create_world(db)
        vo = _create_volume_outline(db, w.id)
        co = ChapterOutlineService.save_chapter_outline(
            db, w.id, volume_outline_id=vo.id, volume_index=1,
            prompt="p",
            result_json='{"title":"旧标题","chapters":[{"chapter_index":1,"title":"第一章"}]}',
            chapter_count=8,
        )
        ChapterOutlineService.update_chapter_outline(db, w.id, co.id, {"title": "新标题"})
        db.refresh(co)
        assert co.title == "新标题"

    def test_discarded_cannot_be_edited(self, db):
        w = _create_world(db)
        vo = _create_volume_outline(db, w.id)
        co = ChapterOutlineService.save_chapter_outline(
            db, w.id, volume_outline_id=vo.id, volume_index=1,
            prompt="p", result_json='{"title":"t1"}', chapter_count=8,
        )
        ChapterOutlineService.discard_chapter_outline(db, w.id, co.id)

        with pytest.raises(ValueError, match="已废弃"):
            ChapterOutlineService.update_chapter_outline(db, w.id, co.id, {"title": "新标题"})
