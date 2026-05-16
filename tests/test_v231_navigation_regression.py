"""
v2.3.1 — Navigation Regression Tests
验证左侧导航 current_world 不丢失、跨模块切换正常。
"""

import pytest, json
from app.database import SessionLocal
from app.services.world_service import WorldService
from app.services.novel_quality_service import NovelQualityService
from app.services.novel_revision_service import NovelRevisionService
from app.services.novel_version_service import NovelVersionService
from app.models import NovelDraft


def _setup(db):
    w = WorldService.create_world(db, name="导航测试世界", world_type="科幻", description="T", current_era="E1", tone="A"); db.commit()
    d = NovelDraft(world_id=w.id, chapter_outline_id=1, volume_index=1, chapter_index=1, title="ND", content="导航测试。", status="candidate")
    db.add(d); db.commit(); db.refresh(d)
    rj = json.dumps({"title":"QR","overall_score":82}, ensure_ascii=False)
    qr = NovelQualityService.save_quality_report(db, w.id, d.id, "p", rj)
    rev = NovelRevisionService.save_revision(db, w.id, d.id, qr.id, "p", "润色正文")
    return w.id, d.id, qr.id, rev.id


class TestNavigationRegression:
    def test_context_has_current_world(self, client):
        """创作资产页面仍保留当前世界."""
        db = SessionLocal()
        try:
            wid, _, _, _ = _setup(db)
            resp = client.get(f"/worlds/{wid}/context")
            assert "请先选择世界以管理创作资产" not in resp.text
            assert f"/worlds/{wid}/simulation" in resp.text
            assert f"/worlds/{wid}/checks" in resp.text
        finally: db.rollback(); db.close()

    def test_simulation_has_current_world(self, client):
        """AI推演页面仍保留当前世界."""
        db = SessionLocal()
        try:
            wid, _, _, _ = _setup(db)
            resp = client.get(f"/worlds/{wid}/simulation")
            assert "请先选择世界以进行 AI 推演" not in resp.text
            assert f"/worlds/{wid}/context" in resp.text
        finally: db.rollback(); db.close()

    def test_checks_has_current_world(self, client):
        """质量检查页面仍保留当前世界."""
        db = SessionLocal()
        try:
            wid, _, _, _ = _setup(db)
            resp = client.get(f"/worlds/{wid}/checks")
            assert "请先选择世界以进行质量检查" not in resp.text
            assert f"/worlds/{wid}/context" in resp.text
        finally: db.rollback(); db.close()

    def test_draft_page_has_current_world(self, client):
        """正文草稿页面不丢 current_world."""
        db = SessionLocal()
        try:
            wid, did, _, _ = _setup(db)
            resp = client.get(f"/worlds/{wid}/novel/drafts/{did}")
            assert "请先选择世界" not in resp.text
        finally: db.rollback(); db.close()

    def test_quality_report_has_current_world(self, client):
        """质量报告页面不丢 current_world."""
        db = SessionLocal()
        try:
            wid, _, qid, _ = _setup(db)
            resp = client.get(f"/worlds/{wid}/novel/quality-reports/{qid}")
            assert "请先选择世界" not in resp.text
        finally: db.rollback(); db.close()

    def test_revision_has_current_world(self, client):
        """润色候选页面不丢 current_world."""
        db = SessionLocal()
        try:
            wid, _, _, rid = _setup(db)
            resp = client.get(f"/worlds/{wid}/novel/revisions/{rid}")
            assert "请先选择世界" not in resp.text
        finally: db.rollback(); db.close()

    def test_versions_has_current_world(self, client):
        """版本管理页面不丢 current_world."""
        db = SessionLocal()
        try:
            wid, did, _, _ = _setup(db)
            resp = client.get(f"/worlds/{wid}/novel/drafts/{did}/versions")
            assert "请先选择世界" not in resp.text
        finally: db.rollback(); db.close()

    def test_final_drafts_has_current_world(self, client):
        """最终采用稿页面不丢 current_world."""
        db = SessionLocal()
        try:
            wid, _, _, _ = _setup(db)
            resp = client.get(f"/worlds/{wid}/novel/final-drafts")
            assert "请先选择世界" not in resp.text
        finally: db.rollback(); db.close()

    def test_active_has_href(self, client):
        """active项保留href."""
        db = SessionLocal()
        try:
            wid, _, _, _ = _setup(db)
            resp = client.get(f"/worlds/{wid}")
            import re
            match = re.search(r'<a[^>]*class="[^"]*active[^"]*"[^>]*>', resp.text)
            assert match, "应存在active链接"
            assert 'href=' in match.group(0), "active项应保留href"
        finally: db.rollback(); db.close()

    def test_no_broken_nav_links(self, client):
        """所有世界内页面不生成 /worlds/None 或 /worlds//."""
        db = SessionLocal()
        try:
            wid, did, qid, rid = _setup(db)
            paths = [
                f"/worlds/{wid}", f"/worlds/{wid}/context", f"/worlds/{wid}/simulation",
                f"/worlds/{wid}/checks", f"/worlds/{wid}/novel/drafts/{did}",
                f"/worlds/{wid}/novel/quality-reports/{qid}",
                f"/worlds/{wid}/novel/revisions/{rid}",
                f"/worlds/{wid}/novel/drafts/{did}/versions",
                f"/worlds/{wid}/novel/final-drafts",
            ]
            for p in paths:
                r = client.get(p)
                assert "/worlds/None" not in r.text, f"{p} 含 /worlds/None"
                assert "/worlds//" not in r.text, f"{p} 含 /worlds//"
        finally: db.rollback(); db.close()
