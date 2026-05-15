"""
AI World Engine - Test Chapter Outline Routes
Tests for chapter outline HTTP routes.
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
    """Override FastAPI DB dependency, preserving any previous override."""
    previous = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = _get_test_db
    yield
    if previous is not None:
        app.dependency_overrides[get_db] = previous
    else:
        app.dependency_overrides.pop(get_db, None)


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
    """Create world + main volume outline, return (world_id, vo_id)."""
    w = World(name="测试世界", world_type="奇幻")
    db.add(w); db.commit(); db.refresh(w)
    wid = w.id
    vo = NovelVolumeOutline(
        world_id=wid, title="主线分卷方案", volume_count=3,
        result_json=json.dumps({
            "title": "主线分卷方案", "volume_count": 3,
            "volumes": [
                {"volume_index": 1, "title": "第一卷", "core_theme": "觉醒",
                 "main_conflict": "外部威胁", "protagonist_goal": "成长",
                 "key_characters": ["主角"], "key_factions": [], "key_locations": [],
                 "major_events": ["事件1"], "turning_point": "转折",
                 "ending_hook": "钩子", "estimated_chapters": 15},
                {"volume_index": 2, "title": "第二卷", "core_theme": "远征",
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
    """Create chapter outline, return co_id."""
    co = NovelChapterOutline(
        world_id=wid, volume_outline_id=vid,
        volume_index=vi, volume_title=f"第{vi}卷",
        title=f"第{vi}卷章节大纲", chapter_count=8,
        result_json=json.dumps({
            "title": f"第{vi}卷章节大纲", "volume_index": vi,
            "chapters": [{
                "chapter_index": 1, "title": "第一章", "chapter_goal": "目标",
                "main_conflict": "冲突", "pov_character": "主角",
                "key_characters": ["A"], "key_locations": ["B"],
                "plot_events": ["事件"], "emotional_beat": "情绪",
                "foreshadowing": "伏笔", "ending_hook": "钩子",
                "estimated_words": 3000, "notes": "",
            }],
        }, ensure_ascii=False),
        prompt="test",
    )
    db.add(co); db.commit(); db.refresh(co)
    return co.id


def _make_world_only(db):
    """Create just a world, return world_id."""
    w = World(name="测试世界", world_type="奇幻")
    db.add(w); db.commit(); db.refresh(w)
    return w.id


class TestChapterOutlineListRoute:
    def test_list_returns_200(self, client):
        db = _Session(); wid, vid = _make_world_vo(db); db.close()
        assert client.get(f"/worlds/{wid}/novel/chapter-outlines").status_code == 200

    def test_list_contains_page_title(self, client):
        db = _Session(); wid, vid = _make_world_vo(db); db.close()
        assert "章节大纲" in client.get(f"/worlds/{wid}/novel/chapter-outlines").text

    def test_list_shows_outline_when_present(self, client):
        db = _Session(); wid, vid = _make_world_vo(db)
        _make_co(db, wid, vid); db.close()
        assert client.get(f"/worlds/{wid}/novel/chapter-outlines").status_code == 200

    def test_nonexistent_world_returns_404(self, client):
        assert client.get("/worlds/99999/novel/chapter-outlines").status_code == 404

    def test_no_main_volume_outline_shows_guidance(self, client):
        db = _Session(); wid = _make_world_only(db); db.close()
        assert client.get(f"/worlds/{wid}/novel/chapter-outlines").status_code == 200


class TestChapterOutlineNewRoute:
    def test_new_returns_200(self, client):
        db = _Session(); wid, vid = _make_world_vo(db); db.close()
        assert client.get(f"/worlds/{wid}/novel/chapter-outlines/new").status_code == 200

    def test_new_contains_volume_selection(self, client):
        db = _Session(); wid, vid = _make_world_vo(db); db.close()
        resp = client.get(f"/worlds/{wid}/novel/chapter-outlines/new")
        assert "选择分卷" in resp.text or "volume_index" in resp.text

    def test_new_contains_chapter_count(self, client):
        db = _Session(); wid, vid = _make_world_vo(db); db.close()
        resp = client.get(f"/worlds/{wid}/novel/chapter-outlines/new")
        assert "chapter_count" in resp.text or "章节数量" in resp.text

    def test_new_no_main_volume_outline_shows_warning(self, client):
        db = _Session(); wid = _make_world_only(db); db.close()
        resp = client.get(f"/worlds/{wid}/novel/chapter-outlines/new")
        assert resp.status_code == 200

    def test_new_nonexistent_world_returns_404(self, client):
        assert client.get("/worlds/99999/novel/chapter-outlines/new").status_code == 404


class TestChapterOutlineCreateRoute:
    def test_create_mock_generates_and_redirects(self, client):
        db = _Session(); wid, vid = _make_world_vo(db); db.close()
        resp = client.post(
            f"/worlds/{wid}/novel/chapter-outlines",
            data={"volume_outline_id": str(vid), "volume_index": "1",
                  "chapter_count": "8", "extra_requirements": "测试要求"},
            follow_redirects=False,
        )
        assert resp.status_code in (303, 302)

    def test_create_missing_volume_outline_shows_error(self, client):
        db = _Session(); wid = _make_world_only(db); db.close()
        resp = client.post(
            f"/worlds/{wid}/novel/chapter-outlines",
            data={"volume_index": "1", "chapter_count": "8"},
            follow_redirects=False,
        )
        assert resp.status_code == 200

    def test_create_missing_volume_index_shows_error(self, client):
        db = _Session(); wid, vid = _make_world_vo(db); db.close()
        resp = client.post(
            f"/worlds/{wid}/novel/chapter-outlines",
            data={"volume_outline_id": str(vid), "chapter_count": "8"},
            follow_redirects=False,
        )
        assert resp.status_code == 200


class TestChapterOutlineDetailRoute:
    def test_detail_returns_200(self, client):
        db = _Session(); wid, vid = _make_world_vo(db)
        cid = _make_co(db, wid, vid); db.close()
        assert client.get(f"/worlds/{wid}/novel/chapter-outlines/{cid}").status_code == 200

    def test_detail_shows_chapter_content(self, client):
        db = _Session(); wid, vid = _make_world_vo(db)
        cid = _make_co(db, wid, vid); db.close()
        resp = client.get(f"/worlds/{wid}/novel/chapter-outlines/{cid}")
        assert "第一章" in resp.text or "章节目标" in resp.text

    def test_detail_nonexistent_outline_returns_404(self, client):
        db = _Session(); wid = _make_world_only(db); db.close()
        assert client.get(f"/worlds/{wid}/novel/chapter-outlines/99999").status_code == 404

    def test_detail_cross_world_returns_404(self, client):
        db = _Session(); wid1, vid1 = _make_world_vo(db)
        cid = _make_co(db, wid1, vid1)
        wid2 = _make_world_only(db); db.close()
        assert client.get(f"/worlds/{wid2}/novel/chapter-outlines/{cid}").status_code == 404

    def test_detail_nonexistent_world_returns_404(self, client):
        assert client.get("/worlds/99999/novel/chapter-outlines/1").status_code == 404


class TestChapterOutlineEditRoute:
    def test_edit_get_returns_200(self, client):
        db = _Session(); wid, vid = _make_world_vo(db)
        cid = _make_co(db, wid, vid); db.close()
        assert client.get(f"/worlds/{wid}/novel/chapter-outlines/{cid}/edit").status_code == 200

    def test_edit_post_saves(self, client):
        db = _Session(); wid, vid = _make_world_vo(db)
        cid = _make_co(db, wid, vid); db.close()
        resp = client.post(
            f"/worlds/{wid}/novel/chapter-outlines/{cid}/edit",
            data={"title": "已编辑标题", "summary": "已编辑概述",
                  "chapter_titles": ["新章标题"], "chapter_goals": ["新目标"],
                  "chapter_conflicts": ["新冲突"], "chapter_events": ["新事件"],
                  "chapter_hooks": ["新钩子"], "chapter_words": ["4000"]},
            follow_redirects=False,
        )
        assert resp.status_code in (303, 302)


class TestSetMainAndDiscard:
    def test_set_main_post_works(self, client):
        db = _Session(); wid, vid = _make_world_vo(db)
        cid = _make_co(db, wid, vid); db.close()
        resp = client.post(
            f"/worlds/{wid}/novel/chapter-outlines/{cid}/set-main",
            follow_redirects=False,
        )
        assert resp.status_code in (303, 302)

    def test_discard_post_works(self, client):
        db = _Session(); wid, vid = _make_world_vo(db)
        cid = _make_co(db, wid, vid); db.close()
        resp = client.post(
            f"/worlds/{wid}/novel/chapter-outlines/{cid}/discard",
            follow_redirects=False,
        )
        assert resp.status_code in (303, 302)


class TestTemplateInheritance:
    def test_list_page_extends_base(self, client):
        db = _Session(); wid, vid = _make_world_vo(db); db.close()
        resp = client.get(f"/worlds/{wid}/novel/chapter-outlines")
        assert "app-shell-body" in resp.text or "topbar" in resp.text

    def test_detail_page_has_actions(self, client):
        db = _Session(); wid, vid = _make_world_vo(db)
        cid = _make_co(db, wid, vid); db.close()
        resp = client.get(f"/worlds/{wid}/novel/chapter-outlines/{cid}")
        assert "设为主线" in resp.text or "废弃" in resp.text
