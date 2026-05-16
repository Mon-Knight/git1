"""
v2.2.0 — Novel Revision Integration Tests
"""
import pytest, json
from app.database import SessionLocal
from app.services.world_service import WorldService
from app.services.novel_revision_service import NovelRevisionService
from app.services.novel_quality_service import NovelQualityService
from app.models import NovelDraft


def _setup(db):
    w = WorldService.create_world(db, name="IT", world_type="F", description="T", current_era="E1", tone="A")
    db.commit()
    d = NovelDraft(world_id=w.id, chapter_outline_id=1, volume_index=1, chapter_index=1, title="ID", content="测试正文。", status="candidate")
    db.add(d); db.commit(); db.refresh(d)
    rj = json.dumps({"title": "QR", "overall_score": 82}, ensure_ascii=False)
    qr = NovelQualityService.save_quality_report(db, w.id, d.id, "p", rj)
    return w.id, d.id, qr.id


class TestRevisionIntegration:
    def test_world_console_has_revision_entry(self, client):
        db = SessionLocal()
        try:
            wid, did, _ = _setup(db)
            resp = client.get(f"/worlds/{wid}")
            assert f"/worlds/{wid}/novel/revisions" in resp.text
        finally: db.rollback(); db.close()

    def test_draft_detail_has_revision_entry(self, client):
        db = SessionLocal()
        try:
            wid, did, _ = _setup(db)
            resp = client.get(f"/worlds/{wid}/novel/drafts/{did}")
            assert "润色候选" in resp.text
        finally: db.rollback(); db.close()

    def test_quality_report_detail_has_revision_entry(self, client):
        db = SessionLocal()
        try:
            wid, did, qid = _setup(db)
            resp = client.get(f"/worlds/{wid}/novel/quality-reports/{qid}")
            assert "润色候选稿" in resp.text
        finally: db.rollback(); db.close()

    def test_draft_detail_shows_revision_count(self, client):
        db = SessionLocal()
        try:
            wid, did, qid = _setup(db)
            NovelRevisionService.save_revision(db, wid, did, qid, "p1", "c1")
            resp = client.get(f"/worlds/{wid}/novel/drafts/{did}")
            assert "1" in resp.text
        finally: db.rollback(); db.close()

    def test_unique_accepted_per_draft(self, client):
        db = SessionLocal()
        try:
            wid, did, qid = _setup(db)
            r1 = NovelRevisionService.save_revision(db, wid, did, qid, "p1", "c1")
            r2 = NovelRevisionService.save_revision(db, wid, did, qid, "p2", "c2")
            client.post(f"/worlds/{wid}/novel/revisions/{r1.id}/set-accepted")
            client.post(f"/worlds/{wid}/novel/revisions/{r2.id}/set-accepted")
            import app.database as adb
            db2 = adb.SessionLocal()
            try:
                assert NovelRevisionService.get_revision(db2, wid, r1.id).is_accepted is False
                assert NovelRevisionService.get_revision(db2, wid, r2.id).is_accepted is True
            finally: db2.close()
        finally: db.rollback(); db.close()

    def test_original_draft_not_modified(self, client):
        db = SessionLocal()
        try:
            wid, did, qid = _setup(db)
            original_content = db.query(NovelDraft).filter_by(id=did).first().content
            NovelRevisionService.generate_revision(db, wid, did, qid, {"extra_requirements": ""})
            current_content = db.query(NovelDraft).filter_by(id=did).first().content
            assert current_content == original_content
        finally: db.rollback(); db.close()

    def test_existing_features_still_work(self, client):
        db = SessionLocal()
        try:
            wid, did, _ = _setup(db)
            assert client.get("/").status_code == 200
            assert client.get(f"/worlds/{wid}").status_code == 200
            assert client.get(f"/worlds/{wid}/context").status_code == 200
            assert client.get(f"/worlds/{wid}/simulation").status_code == 200
            assert client.get(f"/worlds/{wid}/checks").status_code == 200
            assert client.get(f"/worlds/{wid}/novel/quality-reports").status_code == 200
            assert client.get("/settings/ai").status_code == 200
            assert client.get("/data").status_code == 200
        finally: db.rollback(); db.close()

    def test_v2013_sidebar_persists(self, client):
        db = SessionLocal()
        try:
            wid, did, _ = _setup(db)
            resp = client.get(f"/worlds/{wid}/context")
            assert "请先选择世界以管理创作资产" not in resp.text
            assert f"/worlds/{wid}/simulation" in resp.text
        finally: db.rollback(); db.close()
