"""
AI World Engine - Test Novel Draft Integration
"""
import json

from app.main import app
from app.database import get_db
from app.models import NovelVolumeOutline, NovelChapterOutline, NovelDraft


def _create_world(client) -> int:
    client.post("/worlds", data={"name": "集成世界", "world_type": "奇幻"}, follow_redirects=False)
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


def test_world_console_has_novel_draft_entries(client):
    w_id = _create_world(client)
    resp = client.get(f"/worlds/{w_id}")
    assert "正文草稿" in resp.text
    assert "生成正文草稿" in resp.text
    assert "全书演化" in resp.text
    assert "分卷大纲" in resp.text
    assert "章节大纲" in resp.text


def test_homepage_no_invalid_draft_links(client):
    resp = client.get("/")
    assert "/worlds/None/novel/drafts" not in resp.text
    assert "/worlds//novel/drafts" not in resp.text


def test_existing_pages_still_200(client):
    w_id = _create_world(client)
    assert client.get(f"/worlds/{w_id}/novel/chapter-outlines").status_code == 200
    assert client.get(f"/worlds/{w_id}/novel/volume-outlines").status_code == 200
    assert client.get(f"/worlds/{w_id}/setting-suggestions").status_code == 200
    assert client.get(f"/worlds/{w_id}/context").status_code == 200
    assert client.get("/settings/ai").status_code == 200
    assert client.get("/data/export").status_code == 200


def test_mock_draft_acceptance_flow(client):
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
    draft_url = resp.headers["location"]
    draft_id = int(draft_url.rsplit("/", 1)[-1])
    client.post(f"/worlds/{w_id}/novel/drafts/{draft_id}/set-accepted", follow_redirects=False)

    db = next(app.dependency_overrides[get_db]())
    try:
        d1 = db.query(NovelDraft).filter_by(id=draft_id).first()
        assert d1.is_accepted is True
    finally:
        db.close()

    # Create another candidate for same chapter and accept it
    db = next(app.dependency_overrides[get_db]())
    try:
        d2 = NovelDraft(world_id=w_id, chapter_outline_id=co.id, chapter_index=1, content="第二份")
        d3 = NovelDraft(world_id=w_id, chapter_outline_id=co.id, chapter_index=2, content="第三份")
        db.add_all([d2, d3]); db.commit(); db.refresh(d2); db.refresh(d3)
        second_id = d2.id
        third_id = d3.id
    finally:
        db.close()

    client.post(f"/worlds/{w_id}/novel/drafts/{second_id}/set-accepted", follow_redirects=False)
    client.post(f"/worlds/{w_id}/novel/drafts/{third_id}/set-accepted", follow_redirects=False)

    db = next(app.dependency_overrides[get_db]())
    try:
        accepted_ch1 = db.query(NovelDraft).filter_by(
            world_id=w_id, chapter_outline_id=co.id, chapter_index=1, is_accepted=True
        ).all()
        accepted_ch2 = db.query(NovelDraft).filter_by(
            world_id=w_id, chapter_outline_id=co.id, chapter_index=2, is_accepted=True
        ).all()
        assert len(accepted_ch1) == 1
        assert len(accepted_ch2) == 1
    finally:
        db.close()
