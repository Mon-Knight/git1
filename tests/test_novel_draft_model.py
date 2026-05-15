"""
AI World Engine - Test Novel Draft Model
"""
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import World, NovelVolumeOutline, NovelChapterOutline, NovelDraft

_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
_Session = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


def _make_world(db, name="测试世界"):
    w = World(name=name, world_type="奇幻")
    db.add(w)
    db.commit()
    db.refresh(w)
    return w


def _make_volume_outline(db, world_id: int):
    vo = NovelVolumeOutline(
        world_id=world_id,
        title="主线分卷方案",
        volume_count=1,
        result_json=json.dumps({
            "title": "主线分卷方案",
            "volume_count": 1,
            "volumes": [{"volume_index": 1, "title": "第一卷"}],
        }, ensure_ascii=False),
        status="main",
        is_main=True,
        prompt="test",
    )
    db.add(vo)
    db.commit()
    db.refresh(vo)
    return vo


def _make_chapter_outline(db, world_id: int, volume_outline_id: int):
    co = NovelChapterOutline(
        world_id=world_id,
        volume_outline_id=volume_outline_id,
        volume_index=1,
        volume_title="第一卷",
        title="章节大纲",
        chapter_count=1,
        result_json=json.dumps({
            "title": "章节大纲",
            "chapters": [
                {
                    "chapter_index": 1,
                    "title": "第一章",
                    "chapter_goal": "目标",
                    "main_conflict": "冲突",
                    "key_characters": ["主角"],
                    "key_locations": ["主城"],
                    "plot_events": ["事件"],
                    "emotional_beat": "情绪",
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
    db.add(co)
    db.commit()
    db.refresh(co)
    return co


def test_novel_draft_model_defaults():
    Base.metadata.create_all(bind=_engine)
    db = _Session()
    try:
        w = _make_world(db)
        vo = _make_volume_outline(db, w.id)
        co = _make_chapter_outline(db, w.id, vo.id)
        draft = NovelDraft(
            world_id=w.id,
            chapter_outline_id=co.id,
            volume_index=1,
            volume_title="第一卷",
            chapter_index=1,
            chapter_title="第一章",
            title="第一章 正文草稿",
            content="这是正文内容",
            word_count=6,
        )
        db.add(draft)
        db.commit()
        db.refresh(draft)

        assert draft.status == "candidate"
        assert draft.is_accepted is False
        assert draft.world_id == w.id
        assert draft.chapter_outline_id == co.id
        assert draft.chapter_index == 1
        assert "正文内容" in draft.content
        assert draft.word_count == 6
    finally:
        db.close()
        Base.metadata.drop_all(bind=_engine)


def test_novel_draft_cross_world_isolation():
    Base.metadata.create_all(bind=_engine)
    db = _Session()
    try:
        w1 = _make_world(db, "世界1")
        w2 = _make_world(db, "世界2")
        vo1 = _make_volume_outline(db, w1.id)
        vo2 = _make_volume_outline(db, w2.id)
        co1 = _make_chapter_outline(db, w1.id, vo1.id)
        co2 = _make_chapter_outline(db, w2.id, vo2.id)

        d1 = NovelDraft(world_id=w1.id, chapter_outline_id=co1.id, chapter_index=1, content="A")
        d2 = NovelDraft(world_id=w2.id, chapter_outline_id=co2.id, chapter_index=1, content="B")
        db.add_all([d1, d2])
        db.commit()

        w1_drafts = db.query(NovelDraft).filter_by(world_id=w1.id).all()
        w2_drafts = db.query(NovelDraft).filter_by(world_id=w2.id).all()
        assert len(w1_drafts) == 1
        assert len(w2_drafts) == 1
    finally:
        db.close()
        Base.metadata.drop_all(bind=_engine)
