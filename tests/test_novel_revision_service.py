"""
v2.2.0 — Novel Revision Service Tests
"""
import pytest, json
from app.database import SessionLocal
from app.services.world_service import WorldService
from app.services.novel_revision_service import NovelRevisionService
from app.services.novel_quality_service import NovelQualityService
from app.models import NovelDraft


def _setup(db):
    w = WorldService.create_world(db, name="S", world_type="F", description="T", current_era="E1", tone="A")
    db.commit()
    d = NovelDraft(world_id=w.id, chapter_outline_id=1, volume_index=1, chapter_index=1, title="TD", content="测试正文。主角出发冒险。", status="candidate")
    db.add(d); db.commit(); db.refresh(d)
    rj = json.dumps({"title": "QR", "overall_score": 82}, ensure_ascii=False)
    qr = NovelQualityService.save_quality_report(db, w.id, d.id, "p", rj)
    qr2 = NovelQualityService.save_quality_report(db, w.id, d.id, "p2", rj)
    return w.id, d.id, qr.id


class TestRevisionServicePrompt:
    def test_prompt_has_draft_title(self):
        db = SessionLocal()
        try:
            wid, did, qid = _setup(db)
            p = NovelRevisionService.build_revision_prompt(db, wid, did, qid, {"extra_requirements": ""})
            assert "TD" in p
        finally: db.rollback(); db.close()

    def test_prompt_has_draft_content(self):
        db = SessionLocal()
        try:
            wid, did, qid = _setup(db)
            p = NovelRevisionService.build_revision_prompt(db, wid, did, qid, {"extra_requirements": ""})
            assert "测试正文" in p
        finally: db.rollback(); db.close()

    def test_prompt_has_report_score(self):
        db = SessionLocal()
        try:
            wid, did, qid = _setup(db)
            p = NovelRevisionService.build_revision_prompt(db, wid, did, qid, {"extra_requirements": ""})
            assert "82" in p
        finally: db.rollback(); db.close()

    def test_prompt_forbids_overwrite(self):
        db = SessionLocal()
        try:
            wid, did, qid = _setup(db)
            p = NovelRevisionService.build_revision_prompt(db, wid, did, qid, {"extra_requirements": ""})
            assert "不能覆盖" in p or "不能自动替换" in p
        finally: db.rollback(); db.close()

    def test_prompt_requires_single_chapter(self):
        db = SessionLocal()
        try:
            wid, did, qid = _setup(db)
            p = NovelRevisionService.build_revision_prompt(db, wid, did, qid, {"extra_requirements": ""})
            assert "单章" in p or "不能生成下一章" in p
        finally: db.rollback(); db.close()

    def test_prompt_has_world_info(self):
        db = SessionLocal()
        try:
            wid, did, qid = _setup(db)
            p = NovelRevisionService.build_revision_prompt(db, wid, did, qid, {"extra_requirements": ""})
            assert "S" in p
        finally: db.rollback(); db.close()

    def test_prompt_has_extra_requirements(self):
        db = SessionLocal()
        try:
            wid, did, qid = _setup(db)
            p = NovelRevisionService.build_revision_prompt(db, wid, did, qid, {"extra_requirements": "加强对话"})
            assert "加强对话" in p
        finally: db.rollback(); db.close()


class TestRevisionServiceMock:
    def test_mock_returns_content(self):
        db = SessionLocal()
        try:
            wid, did, qid = _setup(db)
            rev = NovelRevisionService.generate_revision(db, wid, did, qid, {"extra_requirements": ""})
            assert rev is not None; assert rev.content; assert rev.status == "candidate"
        finally: db.rollback(); db.close()

    def test_mock_has_summary(self):
        db = SessionLocal()
        try:
            wid, did, qid = _setup(db)
            rev = NovelRevisionService.generate_revision(db, wid, did, qid, {"extra_requirements": ""})
            assert rev.revision_summary
        finally: db.rollback(); db.close()

    def test_extract_content(self):
        raw = "标题: T\n润色正文:\nCCC\n润色说明:\nSSS"
        content = NovelRevisionService.extract_revision_content(raw)
        assert "CCC" in content

    def test_save_revision(self):
        db = SessionLocal()
        try:
            wid, did, qid = _setup(db)
            rev = NovelRevisionService.save_revision(db, wid, did, qid, "prompt", "content", "raw", "summary")
            assert rev.id is not None; assert rev.world_id == wid
        finally: db.rollback(); db.close()

    def test_list_by_world(self):
        db = SessionLocal()
        try:
            wid, did, qid = _setup(db)
            NovelRevisionService.save_revision(db, wid, did, qid, "p1", "c1")
            NovelRevisionService.save_revision(db, wid, did, qid, "p2", "c2")
            revs = NovelRevisionService.list_revisions(db, wid)
            assert len(revs) == 2
        finally: db.rollback(); db.close()

    def test_list_by_draft(self):
        db = SessionLocal()
        try:
            wid, did, qid = _setup(db)
            NovelRevisionService.save_revision(db, wid, did, qid, "p1", "c1")
            revs = NovelRevisionService.list_revisions(db, wid, draft_id=did)
            assert len(revs) == 1; assert revs[0].draft_id == did
        finally: db.rollback(); db.close()

    def test_get_revision(self):
        db = SessionLocal()
        try:
            wid, did, qid = _setup(db)
            rev = NovelRevisionService.save_revision(db, wid, did, qid, "p1", "c1")
            got = NovelRevisionService.get_revision(db, wid, rev.id)
            assert got is not None; assert got.id == rev.id
        finally: db.rollback(); db.close()

    def test_get_cross_world_rejected(self):
        db = SessionLocal()
        try:
            wid, did, qid = _setup(db)
            rev = NovelRevisionService.save_revision(db, wid, did, qid, "p1", "c1")
            assert NovelRevisionService.get_revision(db, 99999, rev.id) is None
        finally: db.rollback(); db.close()

    def test_set_accepted_unique(self):
        db = SessionLocal()
        try:
            wid, did, qid = _setup(db)
            r1 = NovelRevisionService.save_revision(db, wid, did, qid, "p1", "c1")
            r2 = NovelRevisionService.save_revision(db, wid, did, qid, "p2", "c2")
            NovelRevisionService.set_accepted_revision(db, wid, r1.id)
            NovelRevisionService.set_accepted_revision(db, wid, r2.id)
            assert NovelRevisionService.get_revision(db, wid, r1.id).is_accepted is False
            assert NovelRevisionService.get_revision(db, wid, r2.id).is_accepted is True
        finally: db.rollback(); db.close()

    def test_discard(self):
        db = SessionLocal()
        try:
            wid, did, qid = _setup(db)
            rev = NovelRevisionService.save_revision(db, wid, did, qid, "p1", "c1")
            d = NovelRevisionService.discard_revision(db, wid, rev.id)
            assert d.status == "discarded"; assert d.is_accepted is False
        finally: db.rollback(); db.close()

    def test_discarded_not_accepted(self):
        db = SessionLocal()
        try:
            wid, did, qid = _setup(db)
            rev = NovelRevisionService.save_revision(db, wid, did, qid, "p1", "c1")
            NovelRevisionService.discard_revision(db, wid, rev.id)
            with pytest.raises(ValueError, match="已废弃"):
                NovelRevisionService.set_accepted_revision(db, wid, rev.id)
        finally: db.rollback(); db.close()

    def test_update_revision(self):
        db = SessionLocal()
        try:
            wid, did, qid = _setup(db)
            rev = NovelRevisionService.save_revision(db, wid, did, qid, "p1", "c1")
            updated = NovelRevisionService.update_revision(db, wid, rev.id, {"title": "新标题", "content": "新正文"})
            assert updated.title == "新标题"; assert "新正文" in updated.content
        finally: db.rollback(); db.close()
