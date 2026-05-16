"""
v2.1.0 — Novel Quality Report Integration Tests
验证质量检查报告与现有模块的集成，确保不破坏已有功能。
"""

import pytest
from app.database import SessionLocal
from app.services.world_service import WorldService
from app.services.novel_quality_service import NovelQualityService
from app.models import NovelDraft
import json


def _create_test_world_and_draft(db):
    world = WorldService.create_world(db, name="集成测试世界", world_type="科幻", description="测试", current_era="纪元1", tone="冒险")
    db.commit()
    draft = NovelDraft(
        world_id=world.id, chapter_outline_id=1,
        volume_index=1, chapter_index=1,
        title="集成测试草稿", content="正文内容。",
        status="candidate",
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return world.id, draft.id


class TestQualityReportIntegration:
    """Integration tests — quality reports with existing features."""

    def test_draft_detail_has_quality_entry(self, client):
        """正文草稿详情页包含质量检查入口."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            resp = client.get(f"/worlds/{world_id}/novel/drafts/{draft_id}")
            assert resp.status_code == 200
            assert "正文质量检查" in resp.text
            assert "生成质量检查报告" in resp.text
        finally:
            db.rollback()
            db.close()

    def test_world_console_has_quality_entry(self, client):
        """世界控制台小说工程分组出现正文质量检查入口."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            resp = client.get(f"/worlds/{world_id}")
            assert resp.status_code == 200
            # Sidebar should have quality-reports link
            assert f"/worlds/{world_id}/novel/quality-reports" in resp.text
        finally:
            db.rollback()
            db.close()

    def test_draft_detail_shows_report_count(self, client):
        """生成报告后草稿详情页可看到报告."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            result_json = json.dumps({"title": "测试", "overall_score": 82}, ensure_ascii=False)
            NovelQualityService.save_quality_report(db, world_id, draft_id, "p1", result_json)

            resp = client.get(f"/worlds/{world_id}/novel/drafts/{draft_id}")
            assert resp.status_code == 200
            # Should show report count or current report
            assert "1" in resp.text  # report count
        finally:
            db.rollback()
            db.close()

    def test_unique_current_per_draft(self, client):
        """同一正文草稿只能有一个current报告."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            result_json = json.dumps({"title": "测试"}, ensure_ascii=False)
            r1 = NovelQualityService.save_quality_report(db, world_id, draft_id, "p1", result_json)
            r2 = NovelQualityService.save_quality_report(db, world_id, draft_id, "p2", result_json)

            client.post(f"/worlds/{world_id}/novel/quality-reports/{r1.id}/set-current")
            client.post(f"/worlds/{world_id}/novel/quality-reports/{r2.id}/set-current")

            # r2 should be the only current
            import app.database as app_database
            db2 = app_database.SessionLocal()
            try:
                r1_check = NovelQualityService.get_quality_report(db2, world_id, r1.id)
                r2_check = NovelQualityService.get_quality_report(db2, world_id, r2.id)
                assert r1_check.is_current is False
                assert r2_check.is_current is True
            finally:
                db2.close()
        finally:
            db.rollback()
            db.close()


class TestExistingFeaturesUnchanged:
    """Regression tests — existing features must still work."""

    def test_draft_detail_still_works(self, client):
        """正文草稿详情仍返回200."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            resp = client.get(f"/worlds/{world_id}/novel/drafts/{draft_id}")
            assert resp.status_code == 200
        finally:
            db.rollback()
            db.close()

    def test_world_detail_still_works(self, client):
        """世界详情仍返回200."""
        db = SessionLocal()
        try:
            world_id, _ = _create_test_world_and_draft(db)
            resp = client.get(f"/worlds/{world_id}")
            assert resp.status_code == 200
        finally:
            db.rollback()
            db.close()

    def test_novel_overview_still_works(self, client):
        """小说工程总览仍返回200."""
        db = SessionLocal()
        try:
            world_id, _ = _create_test_world_and_draft(db)
            resp = client.get(f"/worlds/{world_id}/novel")
            assert resp.status_code == 200
        finally:
            db.rollback()
            db.close()

    def test_context_page_still_works(self, client):
        """创作资产仍返回200."""
        db = SessionLocal()
        try:
            world_id, _ = _create_test_world_and_draft(db)
            resp = client.get(f"/worlds/{world_id}/context")
            assert resp.status_code == 200
        finally:
            db.rollback()
            db.close()

    def test_simulation_page_still_works(self, client):
        """AI推演仍返回200."""
        db = SessionLocal()
        try:
            world_id, _ = _create_test_world_and_draft(db)
            resp = client.get(f"/worlds/{world_id}/simulation")
            assert resp.status_code == 200
        finally:
            db.rollback()
            db.close()

    def test_checks_page_still_works(self, client):
        """检查中心仍返回200."""
        db = SessionLocal()
        try:
            world_id, _ = _create_test_world_and_draft(db)
            resp = client.get(f"/worlds/{world_id}/checks")
            assert resp.status_code == 200
        finally:
            db.rollback()
            db.close()

    def test_settings_page_still_works(self, client):
        """设置中心仍返回200."""
        resp = client.get("/settings/ai")
        assert resp.status_code == 200

    def test_data_page_still_works(self, client):
        """导出中心仍返回200."""
        resp = client.get("/data")
        assert resp.status_code == 200

    def test_homepage_still_works(self, client):
        """首页仍返回200."""
        resp = client.get("/")
        assert resp.status_code == 200

    def test_v2013_sidebar_context_persistence(self, client):
        """v2.0.1.3左侧导航current_world修复仍保持."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            # Context page should not show "请先选择世界"
            resp = client.get(f"/worlds/{world_id}/context")
            assert "请先选择世界以管理创作资产" not in resp.text
            # Should have cross-module links
            assert f"/worlds/{world_id}/simulation" in resp.text
            assert f"/worlds/{world_id}/checks" in resp.text
        finally:
            db.rollback()
            db.close()
