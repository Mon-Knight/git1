"""
AI World Engine - Test Chapter Outline Model
Tests for NovelChapterOutline model.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import NovelChapterOutline, World

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


class TestChapterOutlineModel:
    """Tests for NovelChapterOutline model creation and fields."""

    def test_create_chapter_outline(self, db):
        """Chapter outline can be created with required fields."""
        w = World(name="测试世界")
        db.add(w)
        db.commit()

        co = NovelChapterOutline(
            world_id=w.id, volume_outline_id=1, volume_index=1,
            title="测试章节大纲", chapter_count=8,
        )
        db.add(co)
        db.commit()

        assert co.id is not None
        assert co.world_id == w.id
        assert co.title == "测试章节大纲"
        assert co.chapter_count == 8
        assert co.volume_index == 1

    def test_default_status_is_candidate(self, db):
        """Default status should be 'candidate'."""
        w = World(name="测试世界")
        db.add(w)
        db.commit()

        co = NovelChapterOutline(
            world_id=w.id, volume_outline_id=1, volume_index=1,
            title="测试", chapter_count=5,
        )
        db.add(co)
        db.commit()

        assert co.status == "candidate"

    def test_default_is_main_is_false(self, db):
        """Default is_main should be False."""
        w = World(name="测试世界")
        db.add(w)
        db.commit()

        co = NovelChapterOutline(
            world_id=w.id, volume_outline_id=1, volume_index=1,
            title="测试", chapter_count=5,
        )
        db.add(co)
        db.commit()

        assert co.is_main is False

    def test_world_id_association(self, db):
        """Chapter outline correctly associates with world."""
        w1 = World(name="世界1")
        w2 = World(name="世界2")
        db.add_all([w1, w2])
        db.commit()

        co = NovelChapterOutline(
            world_id=w1.id, volume_outline_id=1, volume_index=1,
            title="章节大纲", chapter_count=8,
        )
        db.add(co)
        db.commit()

        assert co.world_id == w1.id
        assert co.world_id != w2.id

    def test_result_json_stores_chinese(self, db):
        """result_json can store Chinese characters."""
        w = World(name="测试世界")
        db.add(w)
        db.commit()

        chinese_json = '{"title":"第1卷章节大纲","chapters":[{"title":"觉醒"}]}'
        co = NovelChapterOutline(
            world_id=w.id, volume_outline_id=1, volume_index=1,
            title="中文章节大纲", chapter_count=8,
            result_json=chinese_json,
        )
        db.add(co)
        db.commit()

        assert "觉醒" in co.result_json

    def test_cross_world_isolation(self, db):
        """Chapter outlines from different worlds are isolated."""
        w1 = World(name="世界1")
        w2 = World(name="世界2")
        db.add_all([w1, w2])
        db.commit()

        co1 = NovelChapterOutline(
            world_id=w1.id, volume_outline_id=1, volume_index=1,
            title="世界1章节大纲", chapter_count=8,
        )
        co2 = NovelChapterOutline(
            world_id=w2.id, volume_outline_id=1, volume_index=1,
            title="世界2章节大纲", chapter_count=10,
        )
        db.add_all([co1, co2])
        db.commit()

        from_w1 = db.query(NovelChapterOutline).filter_by(world_id=w1.id).all()
        from_w2 = db.query(NovelChapterOutline).filter_by(world_id=w2.id).all()

        assert len(from_w1) == 1
        assert len(from_w2) == 1
        assert from_w1[0].title == "世界1章节大纲"
        assert from_w2[0].title == "世界2章节大纲"

    def test_volume_outline_id_field(self, db):
        """volume_outline_id can be stored."""
        w = World(name="测试世界")
        db.add(w)
        db.commit()

        co = NovelChapterOutline(
            world_id=w.id, volume_outline_id=42, volume_index=3,
            title="章节大纲", chapter_count=8,
        )
        db.add(co)
        db.commit()

        assert co.volume_outline_id == 42

    def test_volume_index_field(self, db):
        """volume_index can be stored."""
        w = World(name="测试世界")
        db.add(w)
        db.commit()

        co = NovelChapterOutline(
            world_id=w.id, volume_outline_id=1, volume_index=5,
            title="章节大纲", chapter_count=8,
        )
        db.add(co)
        db.commit()

        assert co.volume_index == 5

    def test_chapter_count_field(self, db):
        """chapter_count can be stored."""
        w = World(name="测试世界")
        db.add(w)
        db.commit()

        co = NovelChapterOutline(
            world_id=w.id, volume_outline_id=1, volume_index=1,
            title="章节大纲", chapter_count=40,
        )
        db.add(co)
        db.commit()

        assert co.chapter_count == 40

    def test_status_enum_values(self, db):
        """Status accepts candidate, main, discarded."""
        w = World(name="测试世界")
        db.add(w)
        db.commit()

        for status in ["candidate", "main", "discarded"]:
            co = NovelChapterOutline(
                world_id=w.id, volume_outline_id=1, volume_index=1,
                title=f"状态测试-{status}", chapter_count=8,
                status=status,
            )
            db.add(co)
            db.commit()
            assert co.status == status
