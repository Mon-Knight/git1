"""
AI World Engine - Test Chapter Outline Integration
Integration tests for chapter outlines within the world console and novel engineering flow.
"""

import json
import pytest
from fastapi.testclient import TestClient

from app.database import Base
from app.models import World, NovelVolumeOutline, NovelChapterOutline
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db

_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
_Session = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


def _get_test_db():
    db = _Session()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def override_db():
    """Override FastAPI DB dependency for this test module."""
    app.dependency_overrides[get_db] = _get_test_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=_engine)
    yield
    Base.metadata.drop_all(bind=_engine)


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


def _make_world_vo(db):
    w = World(name="集成测试世界", world_type="奇幻")
    db.add(w); db.commit(); db.refresh(w)
    wid = w.id
    vo = NovelVolumeOutline(
        world_id=wid, title="主线分卷方案", volume_count=3,
        result_json=json.dumps({
            "title": "主线分卷方案", "volume_count": 3,
            "volumes": [
                {"volume_index": 1, "title": "第一卷：觉醒", "core_theme": "觉醒",
                 "main_conflict": "外部威胁", "protagonist_goal": "成长",
                 "key_characters": ["主角"], "key_factions": [], "key_locations": [],
                 "major_events": ["事件1"], "turning_point": "转折",
                 "ending_hook": "钩子", "estimated_chapters": 15},
                {"volume_index": 2, "title": "第二卷：远征", "core_theme": "远征",
                 "main_conflict": "冲突", "protagonist_goal": "探索",
                 "key_characters": ["主角"], "key_factions": [], "key_locations": [],
                 "major_events": ["事件2"], "turning_point": "转折2",
                 "ending_hook": "钩子2", "estimated_chapters": 20},
            ],
        }, ensure_ascii=False),
        status="main", is_main=True, prompt="test",
    )
    db.add(vo); db.commit(); db.refresh(vo)
    return wid, vo.id


def _make_co(db, wid: int, vid: int, vi: int = 1):
    co = NovelChapterOutline(
        world_id=wid, volume_outline_id=vid,
        volume_index=vi, volume_title=f"第{vi}卷",
        title=f"方案-卷{vi}", chapter_count=8,
        result_json=json.dumps({"title": f"方案-卷{vi}", "chapters": []}, ensure_ascii=False),
    )
    db.add(co); db.commit(); db.refresh(co)
    return co.id


class TestWorldConsoleIntegration:
    def test_world_console_has_chapter_outline_link(self, client):
        db = _Session(); wid, vid = _make_world_vo(db); db.close()
        resp = client.get(f"/worlds/{wid}")
        assert resp.status_code == 200
        assert "章节大纲" in resp.text

    def test_world_console_has_chapter_outlines_url(self, client):
        db = _Session(); wid, vid = _make_world_vo(db); db.close()
        resp = client.get(f"/worlds/{wid}")
        assert "chapter-outlines" in resp.text

    def test_novel_engineering_has_evolution(self, client):
        db = _Session(); wid, vid = _make_world_vo(db); db.close()
        resp = client.get(f"/worlds/{wid}")
        assert "全书演化" in resp.text or "evolution" in resp.text.lower()

    def test_novel_engineering_has_volume_outlines(self, client):
        db = _Session(); wid, vid = _make_world_vo(db); db.close()
        resp = client.get(f"/worlds/{wid}")
        assert "分卷大纲" in resp.text or "volume-outlines" in resp.text.lower()


class TestHomepageNoErrorLinks:
    def test_homepage_no_none_links(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "/worlds/None/novel/chapter-outlines" not in resp.text
        assert "/worlds//novel/chapter-outlines" not in resp.text


class TestRegression:
    def test_volume_outlines_returns_200(self, client):
        db = _Session(); wid, vid = _make_world_vo(db); db.close()
        assert client.get(f"/worlds/{wid}/novel/volume-outlines").status_code == 200

    def test_homepage_returns_200(self, client):
        assert client.get("/").status_code == 200

    def test_worlds_list_returns_200(self, client):
        assert client.get("/worlds").status_code == 200


class TestMainChapterPerVolume:
    def test_same_volume_only_one_main(self, client):
        db = _Session(); wid, vid = _make_world_vo(db)
        cid1 = _make_co(db, wid, vid, vi=1)
        cid2 = _make_co(db, wid, vid, vi=1); db.close()

        r1 = client.post(f"/worlds/{wid}/novel/chapter-outlines/{cid1}/set-main", follow_redirects=False)
        assert r1.status_code in (303, 302)
        r2 = client.post(f"/worlds/{wid}/novel/chapter-outlines/{cid2}/set-main", follow_redirects=False)
        assert r2.status_code in (303, 302)

        db2 = _Session()
        co1 = db2.query(NovelChapterOutline).filter_by(id=cid1).first()
        co2 = db2.query(NovelChapterOutline).filter_by(id=cid2).first()
        assert co1.is_main is False
        assert co2.is_main is True
        db2.close()

    def test_different_volumes_can_have_main(self, client):
        db = _Session(); wid, vid = _make_world_vo(db)
        cid1 = _make_co(db, wid, vid, vi=1)
        cid2 = _make_co(db, wid, vid, vi=2); db.close()

        client.post(f"/worlds/{wid}/novel/chapter-outlines/{cid1}/set-main")
        client.post(f"/worlds/{wid}/novel/chapter-outlines/{cid2}/set-main")

        db2 = _Session()
        co1 = db2.query(NovelChapterOutline).filter_by(id=cid1).first()
        co2 = db2.query(NovelChapterOutline).filter_by(id=cid2).first()
        assert co1.is_main is True
        assert co2.is_main is True
        db2.close()
