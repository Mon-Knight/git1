"""
v2.2.0 — Novel Revision Routes Tests
"""
import pytest, json
from app.database import SessionLocal
from app.services.world_service import WorldService
from app.services.novel_revision_service import NovelRevisionService
from app.services.novel_quality_service import NovelQualityService
from app.models import NovelDraft


def _setup(db):
    w = WorldService.create_world(db, name="RT", world_type="F", description="T", current_era="E1", tone="A")
    db.commit()
    d = NovelDraft(world_id=w.id, chapter_outline_id=1, volume_index=1, chapter_index=1, title="RD", content="测试正文。", status="candidate")
    db.add(d); db.commit(); db.refresh(d)
    rj = json.dumps({"title": "QR", "overall_score": 82}, ensure_ascii=False)
    qr = NovelQualityService.save_quality_report(db, w.id, d.id, "p", rj)
    return w.id, d.id, qr.id


class TestRevisionRoutes:
    def test_world_list_200(self, client):
        db = SessionLocal()
        try:
            wid, did, qid = _setup(db)
            assert client.get(f"/worlds/{wid}/novel/revisions").status_code == 200
        finally: db.rollback(); db.close()

    def test_draft_list_200(self, client):
        db = SessionLocal()
        try:
            wid, did, qid = _setup(db)
            assert client.get(f"/worlds/{wid}/novel/drafts/{did}/revisions").status_code == 200
        finally: db.rollback(); db.close()

    def test_new_page_200(self, client):
        db = SessionLocal()
        try:
            wid, did, qid = _setup(db)
            resp = client.get(f"/worlds/{wid}/novel/drafts/{did}/revisions/new")
            assert resp.status_code == 200; assert "质量检查报告" in resp.text
        finally: db.rollback(); db.close()

    def test_create_redirects(self, client):
        db = SessionLocal()
        try:
            wid, did, qid = _setup(db)
            resp = client.post(f"/worlds/{wid}/novel/drafts/{did}/revisions", data={"quality_report_id": str(qid), "extra_requirements": ""}, follow_redirects=False)
            assert resp.status_code == 303; assert "/revisions/" in resp.headers["location"]
        finally: db.rollback(); db.close()

    def test_detail_200(self, client):
        db = SessionLocal()
        try:
            wid, did, qid = _setup(db)
            rev = NovelRevisionService.save_revision(db, wid, did, qid, "p", "c")
            resp = client.get(f"/worlds/{wid}/novel/revisions/{rev.id}")
            assert resp.status_code == 200; assert "c" in resp.text
        finally: db.rollback(); db.close()

    def test_edit_200(self, client):
        db = SessionLocal()
        try:
            wid, did, qid = _setup(db)
            rev = NovelRevisionService.save_revision(db, wid, did, qid, "p", "c")
            assert client.get(f"/worlds/{wid}/novel/revisions/{rev.id}/edit").status_code == 200
        finally: db.rollback(); db.close()

    def test_edit_save(self, client):
        db = SessionLocal()
        try:
            wid, did, qid = _setup(db)
            rev = NovelRevisionService.save_revision(db, wid, did, qid, "p", "c")
            resp = client.post(f"/worlds/{wid}/novel/revisions/{rev.id}/edit", data={"title": "NT", "content": "NC"}, follow_redirects=False)
            assert resp.status_code == 303
        finally: db.rollback(); db.close()

    def test_set_accepted(self, client):
        db = SessionLocal()
        try:
            wid, did, qid = _setup(db)
            rev = NovelRevisionService.save_revision(db, wid, did, qid, "p", "c")
            resp = client.post(f"/worlds/{wid}/novel/revisions/{rev.id}/set-accepted", follow_redirects=False)
            assert resp.status_code == 303
        finally: db.rollback(); db.close()

    def test_discard(self, client):
        db = SessionLocal()
        try:
            wid, did, qid = _setup(db)
            rev = NovelRevisionService.save_revision(db, wid, did, qid, "p", "c")
            resp = client.post(f"/worlds/{wid}/novel/revisions/{rev.id}/discard", follow_redirects=False)
            assert resp.status_code == 303
        finally: db.rollback(); db.close()

    def test_404_world(self, client):
        assert client.get("/worlds/99999/novel/revisions").status_code == 404

    def test_404_draft(self, client):
        db = SessionLocal()
        try:
            wid, _, _ = _setup(db)
            assert client.get(f"/worlds/{wid}/novel/drafts/99999/revisions").status_code == 404
        finally: db.rollback(); db.close()

    def test_404_revision(self, client):
        db = SessionLocal()
        try:
            wid, _, _ = _setup(db)
            assert client.get(f"/worlds/{wid}/novel/revisions/99999").status_code == 404
        finally: db.rollback(); db.close()

    def test_cross_world_404(self, client):
        db = SessionLocal()
        try:
            wid, did, qid = _setup(db)
            rev = NovelRevisionService.save_revision(db, wid, did, qid, "p", "c")
            w2 = WorldService.create_world(db, name="W2", world_type="F", description="T", current_era="E2", tone="B")
            db.commit()
            assert client.get(f"/worlds/{w2.id}/novel/revisions/{rev.id}").status_code == 404
        finally: db.rollback(); db.close()

    def test_extends_base(self, client):
        db = SessionLocal()
        try:
            wid, _, _ = _setup(db)
            resp = client.get(f"/worlds/{wid}/novel/revisions")
            assert "app-shell-body" in resp.text; assert "app-main-inner" in resp.text
        finally: db.rollback(); db.close()

    def test_no_none_links(self, client):
        db = SessionLocal()
        try:
            wid, did, _ = _setup(db)
            for p in [f"/worlds/{wid}/novel/revisions", f"/worlds/{wid}/novel/drafts/{did}/revisions", f"/worlds/{wid}/novel/drafts/{did}/revisions/new"]:
                r = client.get(p)
                assert "/worlds/None" not in r.text; assert "/worlds//" not in r.text
        finally: db.rollback(); db.close()

    def test_empty_draft_hint(self, client):
        db = SessionLocal()
        try:
            w = WorldService.create_world(db, name="EW", world_type="F", description="T", current_era="E1", tone="A")
            db.commit()
            d = NovelDraft(world_id=w.id, chapter_outline_id=1, volume_index=1, chapter_index=1, title="ED", content="", status="candidate")
            db.add(d); db.commit(); db.refresh(d)
            resp = client.get(f"/worlds/{w.id}/novel/drafts/{d.id}/revisions/new")
            assert "内容为空" in resp.text or "无法生成" in resp.text or "无法润色" in resp.text
        finally: db.rollback(); db.close()
