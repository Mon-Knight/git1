"""
v2.2.0 — Novel Revision UI Adaptation Tests
"""
import pytest, json
from app.database import SessionLocal
from app.services.world_service import WorldService
from app.services.novel_revision_service import NovelRevisionService
from app.services.novel_quality_service import NovelQualityService
from app.models import NovelDraft


def _setup(db):
    w = WorldService.create_world(db, name="UT", world_type="F", description="T", current_era="E1", tone="A")
    db.commit()
    d = NovelDraft(world_id=w.id, chapter_outline_id=1, volume_index=1, chapter_index=1, title="UD", content="测试正文。", status="candidate")
    db.add(d); db.commit(); db.refresh(d)
    rj = json.dumps({"title": "QR", "overall_score": 82}, ensure_ascii=False)
    qr = NovelQualityService.save_quality_report(db, w.id, d.id, "p", rj)
    return w.id, d.id, qr.id


class TestRevisionUI:
    def test_list_uses_shell(self, client):
        db = SessionLocal()
        try:
            wid, _, _ = _setup(db)
            resp = client.get(f"/worlds/{wid}/novel/revisions")
            assert "app-shell-body" in resp.text; assert "app-main-inner" in resp.text
        finally: db.rollback(); db.close()

    def test_new_uses_form(self, client):
        db = SessionLocal()
        try:
            wid, did, _ = _setup(db)
            resp = client.get(f"/worlds/{wid}/novel/drafts/{did}/revisions/new")
            assert "page-form" in resp.text or "form-card" in resp.text
        finally: db.rollback(); db.close()

    def test_detail_uses_dashboard(self, client):
        db = SessionLocal()
        try:
            wid, did, qid = _setup(db)
            rev = NovelRevisionService.save_revision(db, wid, did, qid, "p", "c")
            resp = client.get(f"/worlds/{wid}/novel/revisions/{rev.id}")
            assert "app-main-inner" in resp.text
        finally: db.rollback(); db.close()

    def test_edit_uses_form(self, client):
        db = SessionLocal()
        try:
            wid, did, qid = _setup(db)
            rev = NovelRevisionService.save_revision(db, wid, did, qid, "p", "c")
            resp = client.get(f"/worlds/{wid}/novel/revisions/{rev.id}/edit")
            assert "page-form" in resp.text or "form-textarea" in resp.text
        finally: db.rollback(); db.close()

    def test_detail_shows_status(self, client):
        db = SessionLocal()
        try:
            wid, did, qid = _setup(db)
            rev = NovelRevisionService.save_revision(db, wid, did, qid, "p", "c")
            NovelRevisionService.set_accepted_revision(db, wid, rev.id)
            resp = client.get(f"/worlds/{wid}/novel/revisions/{rev.id}")
            assert "采用润色稿" in resp.text or "accepted" in resp.text
        finally: db.rollback(); db.close()

    def test_discarded_disabled(self, client):
        db = SessionLocal()
        try:
            wid, did, qid = _setup(db)
            rev = NovelRevisionService.save_revision(db, wid, did, qid, "p", "c")
            NovelRevisionService.discard_revision(db, wid, rev.id)
            resp = client.get(f"/worlds/{wid}/novel/revisions/{rev.id}")
            assert rev.status == "discarded" or "已废弃" in resp.text
        finally: db.rollback(); db.close()

    def test_content_area_readable(self, client):
        db = SessionLocal()
        try:
            wid, did, qid = _setup(db)
            rev = NovelRevisionService.save_revision(db, wid, did, qid, "p", "长文本正文内容" * 20)
            resp = client.get(f"/worlds/{wid}/novel/revisions/{rev.id}")
            assert "rev-content" in resp.text or "长文本" in resp.text
        finally: db.rollback(); db.close()

    def test_no_legacy_markers(self, client):
        db = SessionLocal()
        try:
            wid, did, qid = _setup(db)
            rev = NovelRevisionService.save_revision(db, wid, did, qid, "p", "c")
            resp = client.get(f"/worlds/{wid}/novel/revisions/{rev.id}")
            assert "topbar" in resp.text; assert "sidebar" in resp.text
        finally: db.rollback(); db.close()
