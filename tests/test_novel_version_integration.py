"""v2.3.0 — Novel Version Integration Tests"""
import pytest, json
from app.database import SessionLocal
from app.services.world_service import WorldService
from app.services.novel_version_service import NovelVersionService
from app.services.novel_revision_service import NovelRevisionService
from app.services.novel_quality_service import NovelQualityService
from app.models import NovelDraft


def _setup(db):
    w = WorldService.create_world(db, name="VI", world_type="F", description="T", current_era="E1", tone="A"); db.commit()
    d = NovelDraft(world_id=w.id, chapter_outline_id=1, volume_index=1, chapter_index=1, title="ID", content="集成测试正文。", status="candidate")
    db.add(d); db.commit(); db.refresh(d)
    rj = json.dumps({"title":"QR","overall_score":82}, ensure_ascii=False)
    qr = NovelQualityService.save_quality_report(db, w.id, d.id, "p", rj)
    rev = NovelRevisionService.generate_revision(db, w.id, d.id, qr.id, {"extra_requirements":""})
    return w.id, d.id, rev.id


class TestVersionIntegration:
    def test_world_console_has_entry(self, client):
        db=SessionLocal()
        try:
            wid,did,_=_setup(db)
            r=client.get(f"/worlds/{wid}")
            assert f"/worlds/{wid}/novel/final-drafts" in r.text
        finally: db.rollback(); db.close()

    def test_draft_detail_has_version_entry(self, client):
        db=SessionLocal()
        try:
            wid,did,_=_setup(db)
            r=client.get(f"/worlds/{wid}/novel/drafts/{did}")
            assert "版本管理" in r.text
        finally: db.rollback(); db.close()

    def test_set_final_shows_on_draft_detail(self, client):
        db=SessionLocal()
        try:
            wid,did,_=_setup(db)
            NovelVersionService.set_final_version(db, wid, did, "draft", did)
            r=client.get(f"/worlds/{wid}/novel/drafts/{did}")
            assert "最终采用稿" in r.text
        finally: db.rollback(); db.close()

    def test_revoke_shows_none(self, client):
        db=SessionLocal()
        try:
            wid,did,_=_setup(db)
            NovelVersionService.set_final_version(db, wid, did, "draft", did)
            NovelVersionService.revoke_final_version(db, wid, did)
            r=client.get(f"/worlds/{wid}/novel/drafts/{did}")
            assert "暂无最终采用稿" in r.text or "暂无" in r.text
        finally: db.rollback(); db.close()

    def test_draft_content_not_modified(self, client):
        db=SessionLocal()
        try:
            wid,did,_=_setup(db)
            orig=db.query(NovelDraft).filter_by(id=did).first().content
            NovelVersionService.set_final_version(db, wid, did, "draft", did)
            assert db.query(NovelDraft).filter_by(id=did).first().content == orig
        finally: db.rollback(); db.close()

    def test_existing_features_ok(self, client):
        db=SessionLocal()
        try:
            wid,did,_=_setup(db)
            assert client.get("/").status_code==200
            assert client.get(f"/worlds/{wid}").status_code==200
            assert client.get(f"/worlds/{wid}/context").status_code==200
            assert client.get(f"/worlds/{wid}/simulation").status_code==200
            assert client.get(f"/worlds/{wid}/checks").status_code==200
            assert client.get(f"/worlds/{wid}/novel/quality-reports").status_code==200
            assert client.get(f"/worlds/{wid}/novel/revisions").status_code==200
            assert client.get("/settings/ai").status_code==200
            assert client.get("/data").status_code==200
        finally: db.rollback(); db.close()

    def test_v2013_sidebar_persists(self, client):
        db=SessionLocal()
        try:
            wid,_,_=_setup(db)
            r=client.get(f"/worlds/{wid}/context")
            assert "请先选择世界以管理创作资产" not in r.text
            assert f"/worlds/{wid}/simulation" in r.text
        finally: db.rollback(); db.close()
