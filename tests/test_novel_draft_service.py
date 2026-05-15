"""
AI World Engine - Test Novel Draft Service
"""
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import (
    World,
    Character,
    Faction,
    Location,
    WorldRule,
    HistoricalEvent,
    SimulationRecord,
    StyleProfile,
    PlotAnchor,
    ContextPackage,
    NovelVolumeOutline,
    NovelChapterOutline,
    NovelDraft,
)
from app.services.novel_draft_service import NovelDraftService

_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
_Session = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


def _make_world(db) -> World:
    w = World(name="测试世界", world_type="奇幻", description="世界简介", current_era="时代", tone="史诗")
    db.add(w); db.commit(); db.refresh(w)
    return w


def _make_assets(db, world_id: int):
    db.add(Character(world_id=world_id, name="主角", role="英雄", personality="坚定", current_status="存活"))
    db.add(Faction(world_id=world_id, name="盟友势力", faction_type="联盟", goal="守护"))
    db.add(Location(world_id=world_id, name="主城", location_type="城市", description="中心城市"))
    db.add(WorldRule(world_id=world_id, name="规则", rule_type="魔法", content="规则内容"))
    db.add(HistoricalEvent(world_id=world_id, title="正史事件", content="事件内容", is_canon=True))
    db.commit()


def _make_evolution(db, world_id: int):
    record = SimulationRecord(
        world_id=world_id,
        question="全书演化方案",
        ai_response="演化内容",
        status="adopted",
        simulation_type="novel_evolution",
    )
    db.add(record); db.commit(); db.refresh(record)
    return record


def _make_volume_outline(db, world_id: int):
    vo = NovelVolumeOutline(
        world_id=world_id,
        title="主线分卷方案",
        volume_count=1,
        result_json=json.dumps({
            "title": "主线分卷方案",
            "volumes": [{"volume_index": 1, "title": "第一卷"}],
        }, ensure_ascii=False),
        status="main",
        is_main=True,
        prompt="test",
    )
    db.add(vo); db.commit(); db.refresh(vo)
    return vo


def _make_chapter_outline(db, world_id: int, volume_outline_id: int):
    co = NovelChapterOutline(
        world_id=world_id,
        volume_outline_id=volume_outline_id,
        volume_index=1,
        volume_title="第一卷",
        title="主线章节方案",
        chapter_count=1,
        result_json=json.dumps({
            "title": "主线章节方案",
            "chapters": [
                {
                    "chapter_index": 1,
                    "title": "第一章",
                    "chapter_goal": "达到目标",
                    "main_conflict": "主要冲突",
                    "key_characters": ["主角"],
                    "key_locations": ["主城"],
                    "plot_events": ["事件1"],
                    "emotional_beat": "情绪推进",
                    "foreshadowing": "伏笔",
                    "ending_hook": "钩子",
                    "estimated_words": 2000,
                }
            ],
        }, ensure_ascii=False),
        status="main",
        is_main=True,
        prompt="test",
    )
    db.add(co); db.commit(); db.refresh(co)
    return co


def _make_context_assets(db, world_id: int):
    sp = StyleProfile(world_id=world_id, name="史诗风格", genre="史诗", narrative_pov="第三人称", pacing="稳健")
    pa = PlotAnchor(world_id=world_id, name="起点", stage="起始", current_conflict="冲突")
    cp = ContextPackage(world_id=world_id, name="默认上下文", description="上下文描述")
    db.add_all([sp, pa, cp])
    db.commit()
    return sp, pa, cp


def test_build_prompt_contains_required_sections():
    Base.metadata.create_all(bind=_engine)
    db = _Session()
    try:
        w = _make_world(db)
        _make_assets(db, w.id)
        _make_evolution(db, w.id)
        vo = _make_volume_outline(db, w.id)
        co = _make_chapter_outline(db, w.id, vo.id)
        sp, pa, cp = _make_context_assets(db, w.id)

        prompt = NovelDraftService.build_novel_draft_prompt(db, w.id, {
            "chapter_outline_id": co.id,
            "chapter_index": 1,
            "style_profile_id": sp.id,
            "plot_anchor_id": pa.id,
            "context_package_id": cp.id,
            "target_words": "2000",
            "narrative_pov": "第三人称",
            "pacing_requirement": "冲突推进",
            "extra_requirements": "强调心理变化",
        })

        assert "测试世界" in prompt
        assert "主线章节方案" in prompt
        assert "第一章" in prompt
        assert "达到目标" in prompt
        assert "主要冲突" in prompt
        assert "主角" in prompt
        assert "盟友势力" in prompt
        assert "主城" in prompt
        assert "规则内容" in prompt
        assert "史诗风格" in prompt
        assert "默认上下文" in prompt
        assert "不生成整卷" in prompt
        assert "候选草稿" in prompt
    finally:
        db.close()
        Base.metadata.drop_all(bind=_engine)


def test_extract_draft_content():
    raw = "标题：示例\n\n正文：\n这是正文内容。\n\n作者备注：测试"
    content = NovelDraftService.extract_draft_content(raw)
    assert "这是正文内容" in content
    assert "作者备注" not in content


def test_mock_generate_returns_stable_draft():
    Base.metadata.create_all(bind=_engine)
    db = _Session()
    try:
        w = _make_world(db)
        vo = _make_volume_outline(db, w.id)
        co = _make_chapter_outline(db, w.id, vo.id)
        result = NovelDraftService.generate_novel_draft(db, w.id, {
            "chapter_outline_id": co.id,
            "chapter_index": 1,
        })
        assert result["content"]
        assert len(result["content"]) >= 800
    finally:
        db.close()
        Base.metadata.drop_all(bind=_engine)


def test_save_and_list_draft():
    Base.metadata.create_all(bind=_engine)
    db = _Session()
    try:
        w = _make_world(db)
        vo = _make_volume_outline(db, w.id)
        co = _make_chapter_outline(db, w.id, vo.id)
        draft = NovelDraftService.save_novel_draft(
            db,
            w.id,
            {"chapter_outline_id": co.id, "chapter_index": 1},
            prompt="prompt",
            content="正文内容",
            raw_text="raw",
        )
        drafts = NovelDraftService.list_novel_drafts(db, w.id)
        assert len(drafts) == 1
        assert drafts[0].id == draft.id
    finally:
        db.close()
        Base.metadata.drop_all(bind=_engine)


def test_get_and_accept_unique_draft():
    Base.metadata.create_all(bind=_engine)
    db = _Session()
    try:
        w = _make_world(db)
        vo = _make_volume_outline(db, w.id)
        co = _make_chapter_outline(db, w.id, vo.id)

        d1 = NovelDraft(world_id=w.id, chapter_outline_id=co.id, chapter_index=1, content="A")
        d2 = NovelDraft(world_id=w.id, chapter_outline_id=co.id, chapter_index=1, content="B")
        db.add_all([d1, d2]); db.commit(); db.refresh(d1); db.refresh(d2)

        NovelDraftService.set_accepted_novel_draft(db, w.id, d1.id)
        NovelDraftService.set_accepted_novel_draft(db, w.id, d2.id)

        d1_ref = NovelDraftService.get_novel_draft(db, w.id, d1.id)
        d2_ref = NovelDraftService.get_novel_draft(db, w.id, d2.id)
        assert d2_ref.is_accepted is True
        assert d1_ref.is_accepted is False
    finally:
        db.close()
        Base.metadata.drop_all(bind=_engine)


def test_discard_draft():
    Base.metadata.create_all(bind=_engine)
    db = _Session()
    try:
        w = _make_world(db)
        vo = _make_volume_outline(db, w.id)
        co = _make_chapter_outline(db, w.id, vo.id)
        draft = NovelDraft(world_id=w.id, chapter_outline_id=co.id, chapter_index=1, content="A")
        db.add(draft); db.commit(); db.refresh(draft)

        NovelDraftService.discard_novel_draft(db, w.id, draft.id)
        updated = NovelDraftService.get_novel_draft(db, w.id, draft.id)
        assert updated.status == "discarded"
        assert updated.is_accepted is False
    finally:
        db.close()
        Base.metadata.drop_all(bind=_engine)
