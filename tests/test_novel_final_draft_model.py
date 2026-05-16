"""v2.3.0 — Novel Final Draft Model Tests"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import NovelFinalDraft, NovelDraft, World


@pytest.fixture
def db():
    e = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=e)
    s = sessionmaker(bind=e)()
    try: yield s
    finally: s.close()


def _w(db): w=World(name="T"); db.add(w); db.commit(); return w
def _d(db, wid):
    d=NovelDraft(world_id=wid, chapter_outline_id=1, volume_index=1, chapter_index=1, title="D", content="C", status="candidate")
    db.add(d); db.commit(); return d


class TestNovelFinalDraftModel:
    def test_create(self, db):
        w=_w(db); d=_d(db, w.id)
        f=NovelFinalDraft(world_id=w.id, draft_id=d.id, source_type="draft", source_id=d.id, content_snapshot="CS", word_count=100)
        db.add(f); db.commit()
        assert f.id is not None; assert f.is_active is True

    def test_source_types(self, db):
        w=_w(db); d=_d(db, w.id)
        f1=NovelFinalDraft(world_id=w.id, draft_id=d.id, source_type="draft", source_id=d.id)
        f2=NovelFinalDraft(world_id=w.id, draft_id=d.id, source_type="revision", source_id=99)
        db.add_all([f1, f2]); db.commit()
        assert f1.source_type == "draft"; assert f2.source_type == "revision"

    def test_chinese_snapshot(self, db):
        w=_w(db); d=_d(db, w.id)
        f=NovelFinalDraft(world_id=w.id, draft_id=d.id, source_type="draft", source_id=d.id, content_snapshot="中文快照内容")
        db.add(f); db.commit()
        assert "中文快照" in f.content_snapshot

    def test_cross_world_isolation(self, db):
        w1=_w(db); w2=World(name="B"); db.add(w2); db.commit()
        d1=_d(db, w1.id)
        f=NovelFinalDraft(world_id=w1.id, draft_id=d1.id, source_type="draft", source_id=d1.id)
        db.add(f); db.commit()
        assert db.query(NovelFinalDraft).filter_by(id=f.id, world_id=w1.id).first() is not None
        assert db.query(NovelFinalDraft).filter_by(id=f.id, world_id=w2.id).first() is None

    def test_accepted_at_and_revoked_at(self, db):
        w=_w(db); d=_d(db, w.id)
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        f=NovelFinalDraft(world_id=w.id, draft_id=d.id, source_type="draft", source_id=d.id, accepted_at=now, revoked_at=now)
        db.add(f); db.commit()
        assert f.accepted_at is not None; assert f.revoked_at is not None
