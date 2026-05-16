"""
v2.2.0 — Novel Draft Revision Model Tests
验证 NovelDraftRevision 模型创建、字段、跨世界隔离。
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import NovelDraftRevision, NovelDraft, World


@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    try: yield db
    finally: db.close()


def _create_world(db): w = World(name="T"); db.add(w); db.commit(); db.refresh(w); return w

def _create_draft(db, wid):
    d = NovelDraft(world_id=wid, chapter_outline_id=1, volume_index=1, chapter_index=1, title="T", content="C", status="candidate")
    db.add(d); db.commit(); db.refresh(d); return d


class TestNovelDraftRevisionModel:
    def test_create_basic(self, test_db):
        w = _create_world(test_db); d = _create_draft(test_db, w.id)
        r = NovelDraftRevision(world_id=w.id, draft_id=d.id, title="R", content="CC")
        test_db.add(r); test_db.commit()
        assert r.id is not None; assert r.status == "candidate"

    def test_default_status(self, test_db):
        w = _create_world(test_db); d = _create_draft(test_db, w.id)
        r = NovelDraftRevision(world_id=w.id, draft_id=d.id)
        test_db.add(r); test_db.commit()
        assert r.status == "candidate"; assert r.is_accepted is False

    def test_saves_chinese_content(self, test_db):
        w = _create_world(test_db); d = _create_draft(test_db, w.id)
        r = NovelDraftRevision(world_id=w.id, draft_id=d.id, content="中文润色正文", original_content_snapshot="原正文")
        test_db.add(r); test_db.commit()
        assert "中文润色正文" in r.content; assert "原正文" in r.original_content_snapshot

    def test_saves_word_count(self, test_db):
        w = _create_world(test_db); d = _create_draft(test_db, w.id)
        r = NovelDraftRevision(world_id=w.id, draft_id=d.id, content="一二三四五六七八九十", word_count=10)
        test_db.add(r); test_db.commit(); assert r.word_count == 10

    def test_cross_world_isolation(self, test_db):
        w1 = _create_world(test_db); w2 = World(name="B"); test_db.add(w2); test_db.commit()
        d1 = _create_draft(test_db, w1.id)
        r = NovelDraftRevision(world_id=w1.id, draft_id=d1.id)
        test_db.add(r); test_db.commit()
        assert test_db.query(NovelDraftRevision).filter_by(id=r.id, world_id=w1.id).first() is not None
        assert test_db.query(NovelDraftRevision).filter_by(id=r.id, world_id=w2.id).first() is None

    def test_multiple_revisions_same_draft(self, test_db):
        w = _create_world(test_db); d = _create_draft(test_db, w.id)
        test_db.add_all([NovelDraftRevision(world_id=w.id, draft_id=d.id) for _ in range(3)])
        test_db.commit()
        assert test_db.query(NovelDraftRevision).filter_by(draft_id=d.id).count() == 3
