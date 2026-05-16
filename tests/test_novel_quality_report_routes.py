"""
v2.1.0 — Novel Quality Report Routes Tests
验证质量检查报告相关路由返回正确的状态码和内容。
"""

import pytest
from app.database import SessionLocal
from app.services.world_service import WorldService
from app.models import NovelDraft, NovelDraftQualityReport
import json


def _create_test_world_and_draft(db):
    world = WorldService.create_world(db, name="路由测试世界", world_type="科幻", description="测试", current_era="纪元1", tone="冒险")
    db.commit()
    draft = NovelDraft(
        world_id=world.id, chapter_outline_id=1,
        volume_index=1, chapter_index=1,
        title="路由测试草稿", content="正文内容示例。",
        status="candidate",
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return world.id, draft.id


def _create_test_report(db, world_id, draft_id):
    from app.services.novel_quality_service import NovelQualityService
    result_json = json.dumps({"title": "测试报告", "overall_score": 82}, ensure_ascii=False)
    return NovelQualityService.save_quality_report(db, world_id, draft_id, "测试prompt", result_json)


class TestNovelQualityReportRoutes:
    """Route tests for quality reports."""

    def test_world_reports_page_returns_200(self, client):
        """GET quality-reports 返回200."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            resp = client.get(f"/worlds/{world_id}/novel/quality-reports")
            assert resp.status_code == 200
        finally:
            db.rollback()
            db.close()

    def test_draft_reports_page_returns_200(self, client):
        """GET draft quality-reports 返回200."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            resp = client.get(f"/worlds/{world_id}/novel/drafts/{draft_id}/quality-reports")
            assert resp.status_code == 200
        finally:
            db.rollback()
            db.close()

    def test_new_report_page_returns_200(self, client):
        """GET new quality-report 返回200."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            resp = client.get(f"/worlds/{world_id}/novel/drafts/{draft_id}/quality-reports/new")
            assert resp.status_code == 200
        finally:
            db.rollback()
            db.close()

    def test_new_page_contains_check_focus_labels(self, client):
        """新建页包含检查重点."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            resp = client.get(f"/worlds/{world_id}/novel/drafts/{draft_id}/quality-reports/new")
            assert "检查重点" in resp.text
        finally:
            db.rollback()
            db.close()

    def test_create_report_mock_redirects(self, client):
        """POST创建报告重定向到详情页."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            resp = client.post(
                f"/worlds/{world_id}/novel/drafts/{draft_id}/quality-reports",
                data={"check_focus": "", "extra_requirements": ""},
                follow_redirects=False,
            )
            # Should redirect to detail page (303)
            assert resp.status_code == 303
            assert f"/quality-reports/" in resp.headers["location"]
        finally:
            db.rollback()
            db.close()

    def test_detail_page_returns_200(self, client):
        """报告详情页返回200."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            report = _create_test_report(db, world_id, draft_id)
            resp = client.get(f"/worlds/{world_id}/novel/quality-reports/{report.id}")
            assert resp.status_code == 200
        finally:
            db.rollback()
            db.close()

    def test_detail_page_shows_score(self, client):
        """详情页显示综合评分."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            report = _create_test_report(db, world_id, draft_id)
            resp = client.get(f"/worlds/{world_id}/novel/quality-reports/{report.id}")
            assert "82" in resp.text or "综合评分" in resp.text
        finally:
            db.rollback()
            db.close()

    def test_detail_page_shows_issues(self, client):
        """详情页显示问题列表."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            from app.services.novel_quality_service import NovelQualityService
            report = NovelQualityService.generate_quality_report(db, world_id, draft_id, {"check_focus": "", "extra_requirements": ""})
            resp = client.get(f"/worlds/{world_id}/novel/quality-reports/{report.id}")
            assert "发现的问题" in resp.text or "章节目标偏离" in resp.text
        finally:
            db.rollback()
            db.close()

    def test_set_current_works(self, client):
        """set-current POST可设置当前参考报告."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            report = _create_test_report(db, world_id, draft_id)
            resp = client.post(
                f"/worlds/{world_id}/novel/quality-reports/{report.id}/set-current",
                follow_redirects=False,
            )
            assert resp.status_code == 303
        finally:
            db.rollback()
            db.close()

    def test_discard_works(self, client):
        """discard POST可废弃报告."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            report = _create_test_report(db, world_id, draft_id)
            resp = client.post(
                f"/worlds/{world_id}/novel/quality-reports/{report.id}/discard",
                follow_redirects=False,
            )
            assert resp.status_code == 303
        finally:
            db.rollback()
            db.close()

    def test_nonexistent_world_returns_404(self, client):
        """不存在world_id返回404."""
        resp = client.get("/worlds/99999/novel/quality-reports")
        assert resp.status_code == 404

    def test_nonexistent_draft_returns_404(self, client):
        """不存在draft_id返回404."""
        db = SessionLocal()
        try:
            world_id, _ = _create_test_world_and_draft(db)
            resp = client.get(f"/worlds/{world_id}/novel/drafts/99999/quality-reports")
            assert resp.status_code == 404
        finally:
            db.rollback()
            db.close()

    def test_nonexistent_report_returns_404(self, client):
        """不存在report_id返回404."""
        db = SessionLocal()
        try:
            world_id, _ = _create_test_world_and_draft(db)
            resp = client.get(f"/worlds/{world_id}/novel/quality-reports/99999")
            assert resp.status_code == 404
        finally:
            db.rollback()
            db.close()

    def test_cross_world_report_access_returns_404(self, client):
        """跨世界访问返回404."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            report = _create_test_report(db, world_id, draft_id)

            # Create another world
            world2 = WorldService.create_world(db, name="世界B", world_type="魔幻", description="测试2", current_era="纪元2", tone="黑暗")
            db.commit()

            resp = client.get(f"/worlds/{world2.id}/novel/quality-reports/{report.id}")
            assert resp.status_code == 404
        finally:
            db.rollback()
            db.close()

    def test_page_extends_base(self, client):
        """页面继承base.html."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            report = _create_test_report(db, world_id, draft_id)
            resp = client.get(f"/worlds/{world_id}/novel/quality-reports/{report.id}")
            assert "app-shell-body" in resp.text
            assert "app-main-inner" in resp.text
        finally:
            db.rollback()
            db.close()

    def test_no_none_world_links(self, client):
        """不生成/worlds/None."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            for path in [
                f"/worlds/{world_id}/novel/quality-reports",
                f"/worlds/{world_id}/novel/drafts/{draft_id}/quality-reports",
                f"/worlds/{world_id}/novel/drafts/{draft_id}/quality-reports/new",
            ]:
                resp = client.get(path)
                assert "/worlds/None" not in resp.text
                assert "/worlds//" not in resp.text
        finally:
            db.rollback()
            db.close()
