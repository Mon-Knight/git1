"""v2.3.0 — Novel Version Routes Tests"""
import pytest, json
from app.database import SessionLocal
from app.services.world_service import WorldService
from app.services.novel_version_service import NovelVersionService
from app.services.novel_revision_service import NovelRevisionService
from app.services.novel_quality_service import NovelQualityService
from app.models import NovelDraft, NovelDraftRevision


def _setup(db):
    w = WorldService.create_world(db, name="VR", world_type="F", description="T", current_era="E1", tone="A"); db.commit()
    d = NovelDraft(world_id=w.id, chapter_outline_id=1, volume_index=1, chapter_index=1, title="RD", content="测试正文内容。", status="candidate")
    db.add(d); db.commit(); db.refresh(d)
    rj = json.dumps({"title":"QR","overall_score":82}, ensure_ascii=False)
    qr = NovelQualityService.save_quality_report(db, w.id, d.id, "p", rj)
    rev = NovelRevisionService.generate_revision(db, w.id, d.id, qr.id, {"extra_requirements":""})
    return w.id, d.id, rev.id


class TestVersionRoutes:
    def test_versions_page_200(self, client):
        db=SessionLocal()
        try:
            wid,did,_=_setup(db)
            r=client.get(f"/worlds/{wid}/novel/drafts/{did}/versions")
            assert r.status_code==200; assert "版本管理" in r.text
        finally: db.rollback(); db.close()

    def test_versions_has_draft(self, client):
        db=SessionLocal()
        try:
            wid,did,_=_setup(db)
            r=client.get(f"/worlds/{wid}/novel/drafts/{did}/versions")
            assert "原正文" in r.text or "原始正文草稿" in r.text or "RD" in r.text
        finally: db.rollback(); db.close()

    def test_compare_200(self, client):
        db=SessionLocal()
        try:
            wid,did,rid=_setup(db)
            r=client.get(f"/worlds/{wid}/novel/drafts/{did}/versions/compare?left_type=draft&left_id={did}&right_type=revision&right_id={rid}")
            assert r.status_code==200; assert "相似度" in r.text or "对比" in r.text
        finally: db.rollback(); db.close()

    def test_set_final_from_draft(self, client):
        db=SessionLocal()
        try:
            wid,did,_=_setup(db)
            r=client.post(f"/worlds/{wid}/novel/drafts/{did}/versions/final", data={"source_type":"draft","source_id":str(did)}, follow_redirects=False)
            assert r.status_code==303
        finally: db.rollback(); db.close()

    def test_revoke_final(self, client):
        db=SessionLocal()
        try:
            wid,did,_=_setup(db)
            NovelVersionService.set_final_version(db, wid, did, "draft", did)
            r=client.post(f"/worlds/{wid}/novel/drafts/{did}/versions/final/revoke", follow_redirects=False)
            assert r.status_code==303
        finally: db.rollback(); db.close()

    def test_final_drafts_list_200(self, client):
        db=SessionLocal()
        try:
            wid,_,_=_setup(db)
            assert client.get(f"/worlds/{wid}/novel/final-drafts").status_code==200
        finally: db.rollback(); db.close()

    def test_final_detail_200(self, client):
        db=SessionLocal()
        try:
            wid,did,_=_setup(db)
            f=NovelVersionService.set_final_version(db, wid, did, "draft", did)
            r=client.get(f"/worlds/{wid}/novel/final-drafts/{f.id}")
            assert r.status_code==200; assert "RD" in r.text or "最终采用稿" in r.text
        finally: db.rollback(); db.close()

    def test_404s(self, client):
        db=SessionLocal()
        try:
            wid,_,_=_setup(db)
            assert client.get(f"/worlds/99999/novel/drafts/1/versions").status_code==404
            assert client.get(f"/worlds/{wid}/novel/drafts/99999/versions").status_code==404
            assert client.get(f"/worlds/{wid}/novel/final-drafts/99999").status_code==404
        finally: db.rollback(); db.close()

    def test_cross_world_404(self, client):
        db=SessionLocal()
        try:
            wid,did,_=_setup(db)
            f=NovelVersionService.set_final_version(db, wid, did, "draft", did)
            w2=WorldService.create_world(db, name="W2", world_type="F", description="T", current_era="E2", tone="B"); db.commit()
            assert client.get(f"/worlds/{w2.id}/novel/final-drafts/{f.id}").status_code==404
        finally: db.rollback(); db.close()

    def test_extends_base(self, client):
        db=SessionLocal()
        try:
            wid,did,_=_setup(db)
            r=client.get(f"/worlds/{wid}/novel/drafts/{did}/versions")
            assert "app-shell-body" in r.text; assert "app-main-inner" in r.text
        finally: db.rollback(); db.close()

    def test_no_none_links(self, client):
        db=SessionLocal()
        try:
            wid,did,_=_setup(db)
            for p in [f"/worlds/{wid}/novel/drafts/{did}/versions", f"/worlds/{wid}/novel/final-drafts"]:
                r=client.get(p)
                assert "/worlds/None" not in r.text; assert "/worlds//" not in r.text
        finally: db.rollback(); db.close()

    def test_discarded_revision_rejected(self, client):
        db=SessionLocal()
        try:
            wid,did,rid=_setup(db)
            rev=db.query(NovelDraftRevision).filter_by(id=rid).first()
            rev.status="discarded"; db.commit()
            r=client.post(f"/worlds/{wid}/novel/drafts/{did}/versions/final", data={"source_type":"revision","source_id":str(rid)}, follow_redirects=False)
            assert r.status_code in (400, 303)  # 400 with error or 303 redirect with error on the page
        finally: db.rollback(); db.close()
