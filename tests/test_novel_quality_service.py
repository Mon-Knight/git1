"""
v2.1.0 — Novel Quality Service Tests
验证 build_quality_report_prompt, generate, save, list, get, set_current, discard, parse.
"""

import pytest
import json
from app.database import SessionLocal
from app.services.world_service import WorldService
from app.services.novel_draft_service import NovelDraftService
from app.services.novel_quality_service import NovelQualityService
from app.models import NovelDraft, NovelDraftQualityReport


def _create_test_world_and_draft(db):
    """Create test world and draft, return world_id, draft_id."""
    world = WorldService.create_world(db, name="测试世界", world_type="科幻", description="测试", current_era="纪元1", tone="冒险")
    db.commit()

    # Create a minimal draft
    draft = NovelDraft(
        world_id=world.id,
        chapter_outline_id=1,
        volume_index=1,
        chapter_index=1,
        title="测试草稿",
        content="这是一段正文内容，用于测试质量检查。主角小明踏上冒险旅程。",
        status="candidate",
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return world.id, draft.id


class TestNovelQualityServicePrompt:
    """Prompt building tests."""

    def test_prompt_contains_draft_title(self):
        """Prompt包含正文草稿标题."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            data = {"check_focus": "", "extra_requirements": ""}
            prompt = NovelQualityService.build_quality_report_prompt(db, world_id, draft_id, data)
            assert "测试草稿" in prompt
        finally:
            db.rollback()
            db.close()

    def test_prompt_contains_draft_content(self):
        """Prompt包含正文内容."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            data = {"check_focus": "", "extra_requirements": ""}
            prompt = NovelQualityService.build_quality_report_prompt(db, world_id, draft_id, data)
            assert "正文内容" in prompt
        finally:
            db.rollback()
            db.close()

    def test_prompt_contains_world_info(self):
        """Prompt包含世界设定."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            data = {"check_focus": "", "extra_requirements": ""}
            prompt = NovelQualityService.build_quality_report_prompt(db, world_id, draft_id, data)
            assert "测试世界" in prompt
        finally:
            db.rollback()
            db.close()

    def test_prompt_forbids_auto_rewrite(self):
        """Prompt明确禁止自动润色正文."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            data = {"check_focus": "", "extra_requirements": ""}
            prompt = NovelQualityService.build_quality_report_prompt(db, world_id, draft_id, data)
            assert "不能润色正文" in prompt or "不能修改正文" in prompt
        finally:
            db.rollback()
            db.close()

    def test_prompt_forbids_overwrite_draft(self):
        """Prompt明确禁止覆盖正文草稿."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            data = {"check_focus": "", "extra_requirements": ""}
            prompt = NovelQualityService.build_quality_report_prompt(db, world_id, draft_id, data)
            assert "不能覆盖正文草稿" in prompt
        finally:
            db.rollback()
            db.close()

    def test_prompt_requires_json_output(self):
        """Prompt明确要求输出JSON."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            data = {"check_focus": "", "extra_requirements": ""}
            prompt = NovelQualityService.build_quality_report_prompt(db, world_id, draft_id, data)
            assert "JSON" in prompt
        finally:
            db.rollback()
            db.close()

    def test_prompt_includes_check_focus(self):
        """Prompt包含用户检查重点."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            data = {"check_focus": "节奏", "extra_requirements": ""}
            prompt = NovelQualityService.build_quality_report_prompt(db, world_id, draft_id, data)
            assert "节奏" in prompt
        finally:
            db.rollback()
            db.close()

    def test_prompt_includes_extra_requirements(self):
        """Prompt包含用户补充要求."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            data = {"check_focus": "", "extra_requirements": "重点检查对话"}
            prompt = NovelQualityService.build_quality_report_prompt(db, world_id, draft_id, data)
            assert "重点检查对话" in prompt
        finally:
            db.rollback()
            db.close()


class TestNovelQualityServiceMock:
    """Mock mode tests."""

    def test_mock_returns_stable_report(self):
        """Mock模式返回稳定质量报告."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            report = NovelQualityService.generate_quality_report(
                db, world_id, draft_id, {"check_focus": "", "extra_requirements": ""}
            )
            assert report is not None
            assert report.overall_score == 82
            assert report.status == "candidate"
            # Parse result JSON
            result = json.loads(report.result_json)
            assert result["overall_score"] == 82
            assert len(result["strengths"]) >= 2
            assert len(result["issues"]) >= 3
            assert len(result["revision_suggestions"]) >= 3
            assert len(result["risk_flags"]) >= 1
            assert "next_step" in result
        finally:
            db.rollback()
            db.close()

    def test_mock_saves_scores(self):
        """Mock报告保存各维度评分."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            report = NovelQualityService.generate_quality_report(
                db, world_id, draft_id, {"check_focus": "", "extra_requirements": ""}
            )
            assert report.outline_alignment_score == 85
            assert report.world_consistency_score == 80
            assert report.character_consistency_score == 78
            assert report.plot_coherence_score == 84
            assert report.pacing_score == 76
            assert report.prose_score == 82
            assert report.hook_score == 88
        finally:
            db.rollback()
            db.close()


class TestNovelQualityServiceCRUD:
    """CRUD operations tests."""

    def test_save_quality_report(self):
        """save_quality_report正常保存."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            result_json = json.dumps({"title": "测试", "overall_score": 80}, ensure_ascii=False)
            report = NovelQualityService.save_quality_report(
                db, world_id, draft_id, "测试prompt", result_json
            )
            assert report.id is not None
            assert report.world_id == world_id
        finally:
            db.rollback()
            db.close()

    def test_list_quality_reports_by_world(self):
        """list_quality_reports只返回当前世界数据."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            result_json = json.dumps({"title": "测试"}, ensure_ascii=False)
            NovelQualityService.save_quality_report(db, world_id, draft_id, "p1", result_json)
            NovelQualityService.save_quality_report(db, world_id, draft_id, "p2", result_json)

            reports = NovelQualityService.list_quality_reports(db, world_id)
            assert len(reports) == 2
        finally:
            db.rollback()
            db.close()

    def test_list_quality_reports_by_draft(self):
        """list_quality_reports可按draft_id过滤."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            result_json = json.dumps({"title": "测试"}, ensure_ascii=False)
            NovelQualityService.save_quality_report(db, world_id, draft_id, "p1", result_json)

            reports = NovelQualityService.list_quality_reports(db, world_id, draft_id=draft_id)
            assert len(reports) == 1
            assert reports[0].draft_id == draft_id
        finally:
            db.rollback()
            db.close()

    def test_get_quality_report(self):
        """get_quality_report正确获取报告."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            result_json = json.dumps({"title": "测试"}, ensure_ascii=False)
            saved = NovelQualityService.save_quality_report(db, world_id, draft_id, "p1", result_json)

            report = NovelQualityService.get_quality_report(db, world_id, saved.id)
            assert report is not None
            assert report.id == saved.id
        finally:
            db.rollback()
            db.close()

    def test_get_quality_report_cross_world_rejected(self):
        """get_quality_report防止跨世界读取."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            result_json = json.dumps({"title": "测试"}, ensure_ascii=False)
            saved = NovelQualityService.save_quality_report(db, world_id, draft_id, "p1", result_json)

            # Try to get with wrong world_id
            report = NovelQualityService.get_quality_report(db, 99999, saved.id)
            assert report is None
        finally:
            db.rollback()
            db.close()

    def test_set_current_quality_report(self):
        """set_current_quality_report设置current."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            result_json = json.dumps({"title": "测试"}, ensure_ascii=False)
            report = NovelQualityService.save_quality_report(db, world_id, draft_id, "p1", result_json)

            updated = NovelQualityService.set_current_quality_report(db, world_id, report.id)
            assert updated.is_current is True
            assert updated.status == "current"
            assert updated.confirmed_at is not None
        finally:
            db.rollback()
            db.close()

    def test_set_current_unique_per_draft(self):
        """设置新current时旧current自动取消."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            result_json = json.dumps({"title": "测试"}, ensure_ascii=False)

            r1 = NovelQualityService.save_quality_report(db, world_id, draft_id, "p1", result_json)
            r2 = NovelQualityService.save_quality_report(db, world_id, draft_id, "p2", result_json)

            NovelQualityService.set_current_quality_report(db, world_id, r1.id)
            NovelQualityService.set_current_quality_report(db, world_id, r2.id)

            # r1 should no longer be current
            r1_check = NovelQualityService.get_quality_report(db, world_id, r1.id)
            assert r1_check.is_current is False

            # r2 should be current
            r2_check = NovelQualityService.get_quality_report(db, world_id, r2.id)
            assert r2_check.is_current is True
        finally:
            db.rollback()
            db.close()

    def test_discard_quality_report(self):
        """discard_quality_report正常废弃."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            result_json = json.dumps({"title": "测试"}, ensure_ascii=False)
            report = NovelQualityService.save_quality_report(db, world_id, draft_id, "p1", result_json)

            discarded = NovelQualityService.discard_quality_report(db, world_id, report.id)
            assert discarded.status == "discarded"
            assert discarded.is_current is False
        finally:
            db.rollback()
            db.close()

    def test_discarded_cannot_be_current(self):
        """废弃报告不能设为current."""
        db = SessionLocal()
        try:
            world_id, draft_id = _create_test_world_and_draft(db)
            result_json = json.dumps({"title": "测试"}, ensure_ascii=False)
            report = NovelQualityService.save_quality_report(db, world_id, draft_id, "p1", result_json)
            NovelQualityService.discard_quality_report(db, world_id, report.id)

            with pytest.raises(ValueError, match="已废弃"):
                NovelQualityService.set_current_quality_report(db, world_id, report.id)
        finally:
            db.rollback()
            db.close()


class TestNovelQualityServiceParse:
    """JSON response parsing tests."""

    def test_parse_valid_json(self):
        """parse_quality_report_response可解析JSON."""
        raw = '{"title": "测试", "overall_score": 85}'
        result = NovelQualityService.parse_quality_report_response(raw)
        parsed = json.loads(result)
        assert parsed["title"] == "测试"

    def test_parse_non_json_fallback(self):
        """parse_quality_report_response遇到非JSON可兜底."""
        raw = "这不是JSON，是普通文本"
        result = NovelQualityService.parse_quality_report_response(raw)
        parsed = json.loads(result)
        assert "parse_warning" in parsed
        assert parsed["raw_text"] == raw[:5000]

    def test_parse_empty_string(self):
        """parse_quality_report_response空字符串."""
        result = NovelQualityService.parse_quality_report_response("")
        parsed = json.loads(result)
        assert "parse_warning" in parsed
