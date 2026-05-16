"""v2.3.0 — Novel Version Service Tests"""
import pytest, json
from app.database import SessionLocal
from app.services.world_service import WorldService
from app.services.novel_version_service import NovelVersionService
from app.services.novel_revision_service import NovelRevisionService
from app.services.novel_quality_service import NovelQualityService
from app.models import NovelDraft, NovelDraftRevision


def _setup(db):
    w = WorldService.create_world(db, name="VS", world_type="F", description="T", current_era="E1", tone="A")
    db.commit()
    d = NovelDraft(world_id=w.id, chapter_outline_id=1, volume_index=1, chapter_index=1, title="VD", content="原正文内容。主角出发冒险。", status="candidate")
    db.add(d); db.commit(); db.refresh(d)
    rj = json.dumps({"title":"QR","overall_score":82}, ensure_ascii=False)
    qr = NovelQualityService.save_quality_report(db, w.id, d.id, "p", rj)
    rev = NovelRevisionService.generate_revision(db, w.id, d.id, qr.id, {"extra_requirements":""})
    return w.id, d.id, rev.id


class TestListTextVersions:
    def test_has_draft(self):
        db=SessionLocal()
        try:
            wid,did,_=_setup(db)
            vs=NovelVersionService.list_text_versions(db, wid, did)
            assert any(v["version_type"]=="draft" for v in vs)
            assert any("原正文" in v.get("content","") for v in vs if v["version_type"]=="draft")
        finally: db.rollback(); db.close()

    def test_has_revision(self):
        db=SessionLocal()
        try:
            wid,did,_=_setup(db)
            vs=NovelVersionService.list_text_versions(db, wid, did)
            assert any(v["version_type"]=="revision" for v in vs)
        finally: db.rollback(); db.close()


class TestGetTextVersion:
    def test_get_draft(self):
        db=SessionLocal()
        try:
            wid,did,_=_setup(db)
            v=NovelVersionService.get_text_version(db, wid, did, "draft", did)
            assert v is not None; assert "原正文" in v["content"]
        finally: db.rollback(); db.close()

    def test_get_revision(self):
        db=SessionLocal()
        try:
            wid,did,rid=_setup(db)
            v=NovelVersionService.get_text_version(db, wid, did, "revision", rid)
            assert v is not None; assert v["content"]
        finally: db.rollback(); db.close()

    def test_cross_world_rejected(self):
        db=SessionLocal()
        try:
            wid,did,_=_setup(db)
            assert NovelVersionService.get_text_version(db, 99999, did, "draft", did) is None
        finally: db.rollback(); db.close()


class TestCompare:
    def test_compare_diff_versions(self):
        db=SessionLocal()
        try:
            wid,did,rid=_setup(db)
            r=NovelVersionService.compare_text_versions(db, wid, did, "draft", did, "revision", rid)
            assert "error" not in r; assert r["similarity"] is not None
            assert r["left_word_count"] is not None; assert r["right_word_count"] is not None
            assert len(r["diff_blocks"]) > 0
        finally: db.rollback(); db.close()

    def test_compare_same_version(self):
        db=SessionLocal()
        try:
            wid,did,_=_setup(db)
            r=NovelVersionService.compare_text_versions(db, wid, did, "draft", did, "draft", did)
            assert r["same_content"] is True; assert r["similarity"] == 100
        finally: db.rollback(); db.close()

    def test_word_count_delta(self):
        db=SessionLocal()
        try:
            wid,did,rid=_setup(db)
            r=NovelVersionService.compare_text_versions(db, wid, did, "draft", did, "revision", rid)
            assert "word_count_delta" in r
        finally: db.rollback(); db.close()


class TestFinalVersion:
    def test_set_final_from_draft(self):
        db=SessionLocal()
        try:
            wid,did,_=_setup(db)
            f=NovelVersionService.set_final_version(db, wid, did, "draft", did)
            assert f.is_active; assert f.source_type=="draft"
        finally: db.rollback(); db.close()

    def test_set_final_from_revision(self):
        db=SessionLocal()
        try:
            wid,did,rid=_setup(db)
            f=NovelVersionService.set_final_version(db, wid, did, "revision", rid)
            assert f.is_active; assert f.source_type=="revision"
        finally: db.rollback(); db.close()

    def test_set_final_replaces_old(self):
        db=SessionLocal()
        try:
            wid,did,rid=_setup(db)
            f1=NovelVersionService.set_final_version(db, wid, did, "draft", did)
            f2=NovelVersionService.set_final_version(db, wid, did, "revision", rid)
            assert f2.is_active
            import app.database as adb
            db2=adb.SessionLocal()
            try:
                from app.models import NovelFinalDraft
                f1c=db2.query(NovelFinalDraft).filter_by(id=f1.id).first()
                assert f1c.is_active is False
            finally: db2.close()
        finally: db.rollback(); db.close()

    def test_rejects_discarded_revision(self):
        db=SessionLocal()
        try:
            wid,did,rid=_setup(db)
            rev=db.query(NovelDraftRevision).filter_by(id=rid).first()
            rev.status="discarded"; db.commit()
            with pytest.raises(ValueError, match="已废弃"):
                NovelVersionService.set_final_version(db, wid, did, "revision", rid)
        finally: db.rollback(); db.close()

    def test_get_current_final(self):
        db=SessionLocal()
        try:
            wid,did,_=_setup(db)
            NovelVersionService.set_final_version(db, wid, did, "draft", did)
            f=NovelVersionService.get_current_final_version(db, wid, did)
            assert f is not None; assert f.is_active
        finally: db.rollback(); db.close()

    def test_revoke(self):
        db=SessionLocal()
        try:
            wid,did,_=_setup(db)
            NovelVersionService.set_final_version(db, wid, did, "draft", did)
            assert NovelVersionService.revoke_final_version(db, wid, did) is True
            assert NovelVersionService.get_current_final_version(db, wid, did) is None
        finally: db.rollback(); db.close()

    def test_history(self):
        db=SessionLocal()
        try:
            wid,did,rid=_setup(db)
            NovelVersionService.set_final_version(db, wid, did, "draft", did)
            NovelVersionService.set_final_version(db, wid, did, "revision", rid)
            h=NovelVersionService.list_final_version_history(db, wid, did)
            assert len(h) == 2
        finally: db.rollback(); db.close()

    def test_best_context_returns_final(self):
        db=SessionLocal()
        try:
            wid,did,_=_setup(db)
            NovelVersionService.set_final_version(db, wid, did, "draft", did)
            t=NovelVersionService.get_best_context_text_for_draft(db, wid, did)
            assert "原正文" in t
        finally: db.rollback(); db.close()

    def test_best_context_fallback(self):
        db=SessionLocal()
        try:
            wid,did,_=_setup(db)
            t=NovelVersionService.get_best_context_text_for_draft(db, wid, did)
            assert "原正文" in t or "冒险" in t  # falls back to draft content
        finally: db.rollback(); db.close()
