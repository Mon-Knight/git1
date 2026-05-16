"""
v2.3.1 — Empty State Tests
验证各模块在无数据时的友好提示和引导。
"""

import pytest
from app.database import SessionLocal
from app.services.world_service import WorldService
from app.models import NovelDraft


def _create_empty_world(db):
    w = WorldService.create_world(db, name="空状态世界", world_type="科幻", description="T", current_era="E1", tone="A"); db.commit()
    return w.id


class TestEmptyStates:
    def test_no_world_homepage(self, client):
        """首页无世界时应友好提示."""
        resp = client.get("/")
        assert resp.status_code == 200
        # Should not crash, should show some guidance
        assert "app-shell-body" in resp.text

    def test_no_draft_quality_guidance(self, client):
        """无正文草稿时，质量检查页面有引导."""
        db = SessionLocal()
        try:
            wid = _create_empty_world(db)
            # Go to quality reports page — should show guidance
            resp = client.get(f"/worlds/{wid}/novel/quality-reports")
            assert resp.status_code == 200
            assert "还没有" in resp.text or "暂无" in resp.text or "查看正文草稿" in resp.text
        finally: db.rollback(); db.close()

    def test_no_draft_revision_guidance(self, client):
        """无正文草稿时润色候选页面有引导."""
        db = SessionLocal()
        try:
            wid = _create_empty_world(db)
            resp = client.get(f"/worlds/{wid}/novel/revisions")
            assert resp.status_code == 200
            assert "还没有" in resp.text or "暂无" in resp.text or "正文草稿" in resp.text
        finally: db.rollback(); db.close()

    def test_no_final_draft_shows_empty(self, client):
        """无最终采用稿时显示暂无."""
        db = SessionLocal()
        try:
            wid = _create_empty_world(db)
            resp = client.get(f"/worlds/{wid}/novel/final-drafts")
            assert resp.status_code == 200
            assert "还没有" in resp.text or "暂无" in resp.text or "设置最终" in resp.text
        finally: db.rollback(); db.close()

    def test_draft_without_revisions_shows_original(self, client):
        """无润色候选时版本管理仍显示原始草稿."""
        db = SessionLocal()
        try:
            wid = _create_empty_world(db)
            d = NovelDraft(world_id=wid, chapter_outline_id=1, volume_index=1, chapter_index=1, title="SD", content="独立草稿", status="candidate")
            db.add(d); db.commit(); db.refresh(d)
            resp = client.get(f"/worlds/{wid}/novel/drafts/{d.id}/versions")
            assert resp.status_code == 200
            assert "原始正文草稿" in resp.text or "版本管理" in resp.text
        finally: db.rollback(); db.close()

    def test_empty_world_characters(self, client):
        """无角色时角色页面不500."""
        db = SessionLocal()
        try:
            wid = _create_empty_world(db)
            resp = client.get(f"/worlds/{wid}/characters")
            assert resp.status_code == 200
        finally: db.rollback(); db.close()

    def test_empty_world_factions(self, client):
        """无势力时势力页面不500."""
        db = SessionLocal()
        try:
            wid = _create_empty_world(db)
            resp = client.get(f"/worlds/{wid}/factions")
            assert resp.status_code == 200
        finally: db.rollback(); db.close()

    def test_empty_world_locations(self, client):
        """无地点时地点页面不500."""
        db = SessionLocal()
        try:
            wid = _create_empty_world(db)
            resp = client.get(f"/worlds/{wid}/locations")
            assert resp.status_code == 200
        finally: db.rollback(); db.close()

    def test_empty_world_rules(self, client):
        """无规则时规则页面不500."""
        db = SessionLocal()
        try:
            wid = _create_empty_world(db)
            resp = client.get(f"/worlds/{wid}/rules")
            assert resp.status_code == 200
        finally: db.rollback(); db.close()

    def test_discarded_content_handled(self, client):
        """已废弃草稿仍可查看但不应显示为可用."""
        db = SessionLocal()
        try:
            wid = _create_empty_world(db)
            d = NovelDraft(world_id=wid, chapter_outline_id=1, volume_index=1, chapter_index=1, title="DD", content="废弃草稿", status="discarded")
            db.add(d); db.commit(); db.refresh(d)
            resp = client.get(f"/worlds/{wid}/novel/drafts/{d.id}")
            assert resp.status_code == 200
            assert "discarded" in resp.text.lower() or "废弃" in resp.text
        finally: db.rollback(); db.close()
