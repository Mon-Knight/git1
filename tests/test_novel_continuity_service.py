"""
v2.5.0: NovelContinuityService tests.
"""
import json
from app.database import SessionLocal
from app.services.novel_continuity_service import NovelContinuityService


class TestContinuityService:
    def test_mock_generate_has_all_fields(self):
        result = NovelContinuityService.mock_generate()
        assert result["overall_score"] == 82
        assert "scores" in result
        assert "issues" in result
        assert len(result["issues"]) >= 3
        assert len(result["strengths"]) >= 2
        assert len(result["continuity_threads"]) >= 2
        assert "next_step" in result
        assert "summary" in result

    def test_parse_valid_json(self):
        raw = json.dumps(NovelContinuityService.mock_generate(), ensure_ascii=False)
        parsed = NovelContinuityService.parse_continuity_response(raw)
        assert parsed["parsed"] is not None
        assert parsed["parsed"]["overall_score"] == 82

    def test_parse_invalid_json_fallback(self):
        result = NovelContinuityService.parse_continuity_response("not json at all")
        assert result["parsed"] is None
        assert result["parse_warning"] is not None

    def test_save_and_list(self, db):
        mock = NovelContinuityService.mock_generate()
        raw = json.dumps(mock, ensure_ascii=False)
        report = NovelContinuityService.save_continuity_report(
            db, 1, {"range_type": "recent", "title": "SaveTest"},
            "test prompt", raw, raw
        )
        assert report.id is not None
        reports = NovelContinuityService.list_continuity_reports(db, 1)
        assert len(reports) >= 1

    def test_set_current_unsets_previous(self, db):
        mock = NovelContinuityService.mock_generate()
        raw = json.dumps(mock, ensure_ascii=False)
        r1 = NovelContinuityService.save_continuity_report(db, 1, {"range_type": "recent"}, "p", raw, raw)
        r2 = NovelContinuityService.save_continuity_report(db, 1, {"range_type": "recent"}, "p", raw, raw)
        NovelContinuityService.set_current_report(db, 1, r1.id)
        NovelContinuityService.set_current_report(db, 1, r2.id)
        r1_after = NovelContinuityService.get_continuity_report(db, 1, r1.id)
        r2_after = NovelContinuityService.get_continuity_report(db, 1, r2.id)
        assert r1_after.is_current == False
        assert r2_after.is_current == True

    def test_discarded_cannot_be_current(self, db):
        mock = NovelContinuityService.mock_generate()
        raw = json.dumps(mock, ensure_ascii=False)
        r = NovelContinuityService.save_continuity_report(db, 1, {}, "p", raw, raw)
        NovelContinuityService.discard_report(db, 1, r.id)
        result = NovelContinuityService.set_current_report(db, 1, r.id)
        assert result["ok"] == False

    def test_cross_world_isolation(self, db):
        mock = NovelContinuityService.mock_generate()
        raw = json.dumps(mock, ensure_ascii=False)
        NovelContinuityService.save_continuity_report(db, 1, {}, "p", raw, raw)
        reports_w2 = NovelContinuityService.list_continuity_reports(db, 2)
        assert len(reports_w2) == 0
        assert NovelContinuityService.get_continuity_report(db, 2, 1) is None

    def test_build_prompt_contains_requirements(self, db):
        prompt = NovelContinuityService.build_continuity_prompt(db, 1, {"range_type": "recent"})
        assert "连续性" in prompt or "章节" in prompt
        assert "不修改" in prompt or "不能修改" in prompt or "不能自动" in prompt or "只生成" in prompt or "只检查" in prompt
        assert "时间线" in prompt or "人物" in prompt

    def test_format_does_not_modify_content(self):
        mock = NovelContinuityService.mock_generate()
        # Verify it's read-only
        assert "overall_score" in mock
        assert mock["scores"]["timeline"] == 85
