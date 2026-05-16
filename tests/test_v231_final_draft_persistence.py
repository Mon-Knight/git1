"""
v2.3.1 — Final Draft Persistence Tests
验证最终采用稿的持久化、快照不变性、撤销和历史记录。
"""

import pytest, json
from app.database import SessionLocal
from app.services.world_service import WorldService
from app.services.novel_quality_service import NovelQualityService
from app.services.novel_revision_service import NovelRevisionService
from app.services.novel_version_service import NovelVersionService
from app.models import NovelDraft, NovelFinalDraft


def _setup(db):
    w = WorldService.create_world(db, name="持久化测试世界", world_type="科幻", description="T", current_era="E1", tone="A"); db.commit()
    d = NovelDraft(world_id=w.id, chapter_outline_id=1, volume_index=1, chapter_index=1, title="PD", content="持久化测试正文。", status="candidate")
    db.add(d); db.commit(); db.refresh(d)
    rj = json.dumps({"title":"QR","overall_score":82}, ensure_ascii=False)
    qr = NovelQualityService.save_quality_report(db, w.id, d.id, "p", rj)
    return w.id, d.id, qr.id


class TestFinalDraftPersistence:
    def test_set_and_read_final(self):
        """设置最终采用稿后可读取."""
        db = SessionLocal()
        try:
            wid, did, _ = _setup(db)
            f = NovelVersionService.set_final_version(db, wid, did, "draft", did)
            current = NovelVersionService.get_current_final_version(db, wid, did)
            assert current is not None; assert current.id == f.id
            assert current.is_active is True
        finally: db.rollback(); db.close()

    def test_content_snapshot_stable(self):
        """content_snapshot不因原文修改而改变."""
        db = SessionLocal()
        try:
            wid, did, _ = _setup(db)
            orig_content = db.query(NovelDraft).filter_by(id=did).first().content
            f = NovelVersionService.set_final_version(db, wid, did, "draft", did)
            snapshot = f.content_snapshot
            # Modify the original draft
            db.query(NovelDraft).filter_by(id=did).update({"content": "修改后的内容"})
            db.commit()
            # Re-read final draft - snapshot should be unchanged
            db.refresh(f)
            assert f.content_snapshot == snapshot
            assert f.content_snapshot != "修改后的内容"
            # Restore
            db.query(NovelDraft).filter_by(id=did).update({"content": orig_content})
            db.commit()
        finally: db.rollback(); db.close()

    def test_revoke_clears_active(self):
        """撤销后 is_active 变为 False."""
        db = SessionLocal()
        try:
            wid, did, _ = _setup(db)
            NovelVersionService.set_final_version(db, wid, did, "draft", did)
            assert NovelVersionService.revoke_final_version(db, wid, did) is True
            assert NovelVersionService.get_current_final_version(db, wid, did) is None
        finally: db.rollback(); db.close()

    def test_history_preserved_after_revoke(self):
        """撤销后历史记录仍存在."""
        db = SessionLocal()
        try:
            wid, did, _ = _setup(db)
            f = NovelVersionService.set_final_version(db, wid, did, "draft", did)
            NovelVersionService.revoke_final_version(db, wid, did)
            history = NovelVersionService.list_final_version_history(db, wid, did)
            assert len(history) >= 1
            assert any(h.id == f.id for h in history)
        finally: db.rollback(); db.close()

    def test_revision_final_persistence(self):
        """润色候选设为最终稿后可重新读取."""
        db = SessionLocal()
        try:
            wid, did, qid = _setup(db)
            rev = NovelRevisionService.save_revision(db, wid, did, qid, "p", "润色持久化正文")
            f = NovelVersionService.set_final_version(db, wid, did, "revision", rev.id)
            current = NovelVersionService.get_current_final_version(db, wid, did)
            assert current is not None; assert current.source_type == "revision"
            assert "润色持久化正文" in current.content_snapshot
        finally: db.rollback(); db.close()

    def test_multiple_drafts_independent_finals(self):
        """不同草稿的最终采用稿互不影响."""
        db = SessionLocal()
        try:
            wid, did1, _ = _setup(db)
            d2 = NovelDraft(world_id=wid, chapter_outline_id=1, volume_index=1, chapter_index=2, title="D2", content="C2", status="candidate")
            db.add(d2); db.commit(); db.refresh(d2)
            f1 = NovelVersionService.set_final_version(db, wid, did1, "draft", did1)
            f2 = NovelVersionService.set_final_version(db, wid, d2.id, "draft", d2.id)
            assert f1.is_active; assert f2.is_active
            assert NovelVersionService.get_current_final_version(db, wid, did1).id == f1.id
            assert NovelVersionService.get_current_final_version(db, wid, d2.id).id == f2.id
        finally: db.rollback(); db.close()
