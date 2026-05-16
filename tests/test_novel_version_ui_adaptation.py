"""v2.3.0 — Novel Version UI Adaptation Tests"""
import pytest, json
from app.database import SessionLocal
from app.services.world_service import WorldService
from app.services.novel_version_service import NovelVersionService
from app.services.novel_revision_service import NovelRevisionService
from app.services.novel_quality_service import NovelQualityService
from app.models import NovelDraft


def _setup(db):
    w = WorldService.create_world(db, name="VU", world_type="F", description="T", current_era="E1", tone="A"); db.commit()
    d = NovelDraft(world_id=w.id, chapter_outline_id=1, volume_index=1, chapter_index=1, title="UD", content="UI测试正文。", status="candidate")
    db.add(d); db.commit(); db.refresh(d)
    rj = json.dumps({"title":"QR","overall_score":82}, ensure_ascii=False)
    qr = NovelQualityService.save_quality_report(db, w.id, d.id, "p", rj)
    rev = NovelRevisionService.generate_revision(db, w.id, d.id, qr.id, {"extra_requirements":""})
    return w.id, d.id, rev.id


class TestVersionUI:
    def test_versions_uses_shell(self, client):
        db=SessionLocal()
        try:
            wid,did,_=_setup(db)
            r=client.get(f"/worlds/{wid}/novel/drafts/{did}/versions")
            assert "app-shell-body" in r.text; assert "app-main-inner" in r.text
        finally: db.rollback(); db.close()

    def test_compare_has_both_panes(self, client):
        db=SessionLocal()
        try:
            wid,did,rid=_setup(db)
            r=client.get(f"/worlds/{wid}/novel/drafts/{did}/versions/compare?left_type=draft&left_id={did}&right_type=revision&right_id={rid}")
            assert "左侧" in r.text or "left" in r.text.lower() or "cmp-pane" in r.text
        finally: db.rollback(); db.close()

    def test_final_drafts_uses_dashboard(self, client):
        db=SessionLocal()
        try:
            wid,_,_=_setup(db)
            r=client.get(f"/worlds/{wid}/novel/final-drafts")
            assert "app-main-inner" in r.text or "dashboard" in r.text
        finally: db.rollback(); db.close()

    def test_final_detail_uses_dashboard(self, client):
        db=SessionLocal()
        try:
            wid,did,_=_setup(db)
            f=NovelVersionService.set_final_version(db, wid, did, "draft", did)
            r=client.get(f"/worlds/{wid}/novel/final-drafts/{f.id}")
            assert "app-main-inner" in r.text
        finally: db.rollback(); db.close()

    def test_active_shows_badge(self, client):
        db=SessionLocal()
        try:
            wid,did,_=_setup(db)
            f=NovelVersionService.set_final_version(db, wid, did, "draft", did)
            r=client.get(f"/worlds/{wid}/novel/drafts/{did}/versions")
            assert "最终稿" in r.text or "最终采用稿" in r.text
        finally: db.rollback(); db.close()

    def test_no_legacy_markers(self, client):
        db=SessionLocal()
        try:
            wid,did,_=_setup(db)
            r=client.get(f"/worlds/{wid}/novel/drafts/{did}/versions")
            assert "topbar" in r.text; assert "sidebar" in r.text
        finally: db.rollback(); db.close()
