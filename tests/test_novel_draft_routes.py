"""
AI World Engine - Test Novel Draft Routes
"""
import json
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db
from app.models import NovelVolumeOutline, NovelChapterOutline, NovelDraft


def _create_world(client) -> int:
    client.post("/worlds", data={"name": "测试世界", "world_type": "奇幻"}, follow_redirects=False)
    return 1


def _setup_main_chapter_outline(db, world_id: int):
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

    co = NovelChapterOutline(
        world_id=world_id,
        volume_outline_id=vo.id,
        volume_index=1,
        volume_title="第一卷",
        title="主线章节方案",
        chapter_count=2,
        result_json=json.dumps({
            "title": "主线章节方案",
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
                },
                {
                    "chapter_index": 2,
                    "title": "第二章",
                    "chapter_goal": "推进",
                    "main_conflict": "对抗",
                    "key_characters": ["主角"],
                    "key_locations": ["主城"],
                    "plot_events": ["事件2"],
                    "emotional_beat": "变化",
                    "foreshadowing": "伏笔2",
                    "ending_hook": "钩子2",
                    "estimated_words": 2000,
                },
            ],
        }, ensure_ascii=False),
        status="main",
        is_main=True,
        prompt="test",
    )
    db.add(co); db.commit(); db.refresh(co)
    return co


def test_list_returns_200(client):
    w_id = _create_world(client)
    resp = client.get(f"/worlds/{w_id}/novel/drafts")
    assert resp.status_code == 200
    assert "正文草稿" in resp.text


def test_new_page_returns_200(client):
    w_id = _create_world(client)
    db = next(app.dependency_overrides[get_db]())
    try:
        _setup_main_chapter_outline(db, w_id)
    finally:
        db.close()
    resp = client.get(f"/worlds/{w_id}/novel/drafts/new")
    assert resp.status_code == 200
    assert "选择章节" in resp.text
    assert "目标字数" in resp.text
    assert "补充要求" in resp.text


def test_no_main_chapter_outline_prompt(client):
    w_id = _create_world(client)
    resp = client.get(f"/worlds/{w_id}/novel/drafts/new")
    assert "请先生成并确认一个主线章节方案" in resp.text


def test_create_draft_and_view_detail(client):
    w_id = _create_world(client)
    db = next(app.dependency_overrides[get_db]())
    try:
        co = _setup_main_chapter_outline(db, w_id)
        chapter_key = f"{co.id}:1"
    finally:
        db.close()

    resp = client.post(
        f"/worlds/{w_id}/novel/drafts",
        data={"chapter_key": chapter_key, "target_words": "2000"},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    detail_url = resp.headers["location"]
    detail = client.get(detail_url)
    assert detail.status_code == 200
    assert "正文内容" in detail.text or "正文草稿" in detail.text


def test_edit_and_save_draft(client):
    w_id = _create_world(client)
    db = next(app.dependency_overrides[get_db]())
    try:
        co = _setup_main_chapter_outline(db, w_id)
        draft = NovelDraft(world_id=w_id, chapter_outline_id=co.id, chapter_index=1, content="旧内容")
        db.add(draft); db.commit(); db.refresh(draft)
        draft_id = draft.id
    finally:
        db.close()

    edit_page = client.get(f"/worlds/{w_id}/novel/drafts/{draft_id}/edit")
    assert edit_page.status_code == 200
    resp = client.post(
        f"/worlds/{w_id}/novel/drafts/{draft_id}/edit",
        data={"title": "新标题", "content": "新内容", "notes": "备注"},
        follow_redirects=False,
    )
    assert resp.status_code == 303


def test_set_accepted_and_discard(client):
    w_id = _create_world(client)
    db = next(app.dependency_overrides[get_db]())
    try:
        co = _setup_main_chapter_outline(db, w_id)
        draft = NovelDraft(world_id=w_id, chapter_outline_id=co.id, chapter_index=1, content="内容")
        db.add(draft); db.commit(); db.refresh(draft)
        draft_id = draft.id
    finally:
        db.close()

    resp = client.post(f"/worlds/{w_id}/novel/drafts/{draft_id}/set-accepted", follow_redirects=False)
    assert resp.status_code == 303
    resp = client.post(f"/worlds/{w_id}/novel/drafts/{draft_id}/discard", follow_redirects=False)
    assert resp.status_code == 303


def test_missing_world_or_draft_returns_404(client):
    resp = client.get("/worlds/9999/novel/drafts")
    assert resp.status_code == 404
    w_id = _create_world(client)
    resp = client.get(f"/worlds/{w_id}/novel/drafts/99999")
    assert resp.status_code == 404


def test_cross_world_access_404(client):
    w1 = _create_world(client)
    client.post("/worlds", data={"name": "另一个世界", "world_type": "奇幻"}, follow_redirects=False)
    w2 = 2
    db = next(app.dependency_overrides[get_db]())
    try:
        co = _setup_main_chapter_outline(db, w1)
        draft = NovelDraft(world_id=w1, chapter_outline_id=co.id, chapter_index=1, content="内容")
        db.add(draft); db.commit(); db.refresh(draft)
        draft_id = draft.id
    finally:
        db.close()

    resp = client.get(f"/worlds/{w2}/novel/drafts/{draft_id}")
    assert resp.status_code == 404
