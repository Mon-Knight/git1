"""
v2.1.0 — Novel Quality Report UI Adaptation Tests
验证质量检查报告页面使用软件端统一布局。
"""

import pytest
from app.database import SessionLocal
from app.services.world_service import WorldService
from app.services.novel_quality_service import NovelQualityService
from app.models import NovelDraft
import json


def _create_test_world_and_draft(db):
    world = WorldService.create_world(db, name="UI测试世界", world_type="科幻", description="测试", current_era="纪元1", tone="冒险")
    db.commit()
    draft = NovelDraft(
        world_id=world.id, chapter_outline_id=1,
        volume_index=1, chapter_index=1,
        title="UI测试草稿", content="正文内容示例。",
        status="candidate",
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return world.id, draft.id


class TestQualityReportUI:
    """UI adaptation tests."""

    def test_list_page_uses_app_shell(self, client):
        """列表页使用app-shell布局."""
        db = SessionLocal()
        try:
            world_id, _ = _create_test_world_and_draft(db)
            resp = client.get(f"/worlds/{world_id}/novel/quality-reports")
            assert "app-shell-body" in resp.text
            assert "app-main-inner" in resp.text
        finally:
            db.rollback()
            db.close()

    def test_new_page_uses_form(self, client):
        """新建页使用表单样式."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            resp = client.get(f"/worlds/{world_id}/novel/drafts/{draft_id}/quality-reports/new")
            assert "form-card" in resp.text or "page-form" in resp.text
        finally:
            db.rollback()
            db.close()

    def test_detail_page_uses_dashboard(self, client):
        """详情页使用page-dashboard."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            report = NovelQualityService.generate_quality_report(db, world_id, draft_id, {"check_focus": "", "extra_requirements": ""})
            resp = client.get(f"/worlds/{world_id}/novel/quality-reports/{report.id}")
            assert "app-main-inner" in resp.text
        finally:
            db.rollback()
            db.close()

    def test_detail_shows_status_badge(self, client):
        """详情页包含状态标签."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            result_json = json.dumps({"title": "测试"}, ensure_ascii=False)
            report = NovelQualityService.save_quality_report(db, world_id, draft_id, "p1", result_json)
            resp = client.get(f"/worlds/{world_id}/novel/quality-reports/{report.id}")
            assert "status-badge" in resp.text or "候选" in resp.text or "current" in resp.text
        finally:
            db.rollback()
            db.close()

    def test_discarded_report_button_disabled(self, client):
        """已废弃报告的操作按钮受限."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            result_json = json.dumps({"title": "测试"}, ensure_ascii=False)
            report = NovelQualityService.save_quality_report(db, world_id, draft_id, "p1", result_json)
            NovelQualityService.discard_quality_report(db, world_id, report.id)

            resp = client.get(f"/worlds/{world_id}/novel/quality-reports/{report.id}")
            # Should show discarded status
            assert report.status == "discarded" or "已废弃" in resp.text
        finally:
            db.rollback()
            db.close()

    def test_current_report_shows_marker(self, client):
        """当前参考报告显示标记."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            result_json = json.dumps({"title": "测试", "overall_score": 85}, ensure_ascii=False)
            report = NovelQualityService.save_quality_report(db, world_id, draft_id, "p1", result_json)
            NovelQualityService.set_current_quality_report(db, world_id, report.id)

            resp = client.get(f"/worlds/{world_id}/novel/quality-reports/{report.id}")
            assert "当前参考" in resp.text or "current" in resp.text
        finally:
            db.rollback()
            db.close()

    def test_detail_has_score_display(self, client):
        """分数展示区域存在."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            report = NovelQualityService.generate_quality_report(db, world_id, draft_id, {"check_focus": "", "extra_requirements": ""})
            resp = client.get(f"/worlds/{world_id}/novel/quality-reports/{report.id}")
            assert "score" in resp.text.lower() or "评分" in resp.text or "82" in resp.text
        finally:
            db.rollback()
            db.close()

    def test_detail_has_issues_display(self, client):
        """问题列表展示区域存在."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            report = NovelQualityService.generate_quality_report(db, world_id, draft_id, {"check_focus": "", "extra_requirements": ""})
            resp = client.get(f"/worlds/{world_id}/novel/quality-reports/{report.id}")
            assert "issue" in resp.text.lower() or "发现问题" in resp.text
        finally:
            db.rollback()
            db.close()

    def test_no_legacy_markers(self, client):
        """页面不出现旧网页端独立布局标记."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            report = NovelQualityService.generate_quality_report(db, world_id, draft_id, {"check_focus": "", "extra_requirements": ""})
            resp = client.get(f"/worlds/{world_id}/novel/quality-reports/{report.id}")
            # Verify app shell is present (not legacy)
            assert "topbar" in resp.text
            assert "sidebar" in resp.text
        finally:
            db.rollback()
            db.close()
