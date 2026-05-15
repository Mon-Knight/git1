"""
AI World Engine - Test Chapter Outline UI Adaptation
Tests that chapter outline pages use the desktop app shell layout.
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
    w = World(name="UI测试世界", world_type="奇幻")
    db.add(w); db.commit(); db.refresh(w)
    wid = w.id
    vo = NovelVolumeOutline(
        world_id=wid, title="主线分卷方案", volume_count=2,
        result_json=json.dumps({
            "title": "主线分卷方案", "volume_count": 2,
            "volumes": [
                {"volume_index": 1, "title": "第一卷", "core_theme": "觉醒",
                 "main_conflict": "冲突", "protagonist_goal": "成长",
                 "key_characters": [], "key_factions": [], "key_locations": [],
                 "major_events": [], "turning_point": "", "ending_hook": "",
                 "estimated_chapters": 10},
            ],
        }, ensure_ascii=False),
        status="main", is_main=True, prompt="test",
    )
    db.add(vo); db.commit(); db.refresh(vo)
    return wid, vo.id


def _make_co(db, wid: int, vid: int, vi: int = 1, status: str = "candidate", is_main: bool = False):
    co = NovelChapterOutline(
        world_id=wid, volume_outline_id=vid,
        volume_index=vi, volume_title=f"第{vi}卷",
        title="章节大纲测试", chapter_count=3,
        result_json=json.dumps({
            "title": "章节大纲测试", "volume_index": vi,
            "chapters": [
                {"chapter_index": 1, "title": "第一章", "chapter_goal": "目标",
                 "main_conflict": "冲突", "pov_character": "主角",
                 "key_characters": [], "key_locations": [],
                 "plot_events": [], "emotional_beat": "", "foreshadowing": "",
                 "ending_hook": "", "estimated_words": 3000, "notes": ""},
            ],
        }, ensure_ascii=False),
        status=status, is_main=is_main, prompt="test",
    )
    db.add(co); db.commit(); db.refresh(co)
    return co.id


class TestListPageUI:
    def test_list_page_uses_app_shell(self, client):
        db = _Session(); wid, vid = _make_world_vo(db); db.close()
        resp = client.get(f"/worlds/{wid}/novel/chapter-outlines")
        assert "app-shell-body" in resp.text or "topbar" in resp.text

    def test_list_page_has_status_labels(self, client):
        db = _Session(); wid, vid = _make_world_vo(db)
        _make_co(db, wid, vid); db.close()
        resp = client.get(f"/worlds/{wid}/novel/chapter-outlines")
        assert "候选" in resp.text or "co-status" in resp.text

    def test_list_page_shows_main_tag(self, client):
        db = _Session(); wid, vid = _make_world_vo(db)
        _make_co(db, wid, vid, status="main", is_main=True); db.close()
        resp = client.get(f"/worlds/{wid}/novel/chapter-outlines")
        assert "主线" in resp.text

    def test_discarded_buttons_disabled_in_list(self, client):
        db = _Session(); wid, vid = _make_world_vo(db)
        _make_co(db, wid, vid, status="discarded"); db.close()
        resp = client.get(f"/worlds/{wid}/novel/chapter-outlines")
        assert resp.status_code == 200


class TestNewPageUI:
    def test_new_page_uses_page_form(self, client):
        db = _Session(); wid, vid = _make_world_vo(db); db.close()
        resp = client.get(f"/worlds/{wid}/novel/chapter-outlines/new")
        assert "page-form" in resp.text

    def test_new_page_max_width(self, client):
        db = _Session(); wid, vid = _make_world_vo(db); db.close()
        resp = client.get(f"/worlds/{wid}/novel/chapter-outlines/new")
        assert "960px" in resp.text


class TestDetailPageUI:
    def test_detail_page_has_main_button(self, client):
        db = _Session(); wid, vid = _make_world_vo(db)
        cid = _make_co(db, wid, vid); db.close()
        resp = client.get(f"/worlds/{wid}/novel/chapter-outlines/{cid}")
        assert "设为主线" in resp.text

    def test_detail_page_has_discard_button(self, client):
        db = _Session(); wid, vid = _make_world_vo(db)
        cid = _make_co(db, wid, vid); db.close()
        resp = client.get(f"/worlds/{wid}/novel/chapter-outlines/{cid}")
        assert "废弃" in resp.text

    def test_detail_page_has_edit_button(self, client):
        db = _Session(); wid, vid = _make_world_vo(db)
        cid = _make_co(db, wid, vid); db.close()
        resp = client.get(f"/worlds/{wid}/novel/chapter-outlines/{cid}")
        assert "编辑" in resp.text

    def test_discarded_detail_disables_actions(self, client):
        db = _Session(); wid, vid = _make_world_vo(db)
        cid = _make_co(db, wid, vid, status="discarded"); db.close()
        resp = client.get(f"/worlds/{wid}/novel/chapter-outlines/{cid}")
        assert resp.status_code == 200


class TestEditPageUI:
    def test_edit_page_uses_page_form(self, client):
        db = _Session(); wid, vid = _make_world_vo(db)
        cid = _make_co(db, wid, vid); db.close()
        resp = client.get(f"/worlds/{wid}/novel/chapter-outlines/{cid}/edit")
        assert "page-form" in resp.text

    def test_edit_page_has_save_button(self, client):
        db = _Session(); wid, vid = _make_world_vo(db)
        cid = _make_co(db, wid, vid); db.close()
        resp = client.get(f"/worlds/{wid}/novel/chapter-outlines/{cid}/edit")
        assert "保存" in resp.text
