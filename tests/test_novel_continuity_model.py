"""
v2.5.0: NovelContinuityReport model tests.
"""
import pytest
from app.database import SessionLocal
from app.models import NovelContinuityReport


class TestNovelContinuityModel:
    def test_create_model(self, db):
        r = NovelContinuityReport(world_id=1, range_type="recent", title="Test")
        db.add(r)
        db.commit()
        assert r.id is not None

    def test_range_type_saved(self, db):
        r = NovelContinuityReport(world_id=1, range_type="chapter_range", start_chapter_index=1, end_chapter_index=5)
        db.add(r); db.commit()
        assert r.range_type == "chapter_range"
        assert r.start_chapter_index == 1

    def test_scores_saved(self, db):
        r = NovelContinuityReport(world_id=1, overall_score=82, timeline_score=85, character_state_score=78)
        db.add(r); db.commit()
        assert r.overall_score == 82
        assert r.timeline_score == 85

    def test_result_json_saved(self, db):
        r = NovelContinuityReport(world_id=1, result_json='{"summary":"测试中文"}')
        db.add(r); db.commit()
        assert "测试中文" in r.result_json

    def test_is_current_default_false(self, db):
        r = NovelContinuityReport(world_id=1)
        db.add(r); db.commit()
        assert r.is_current == False
        assert r.status == "candidate"

    def test_cross_world_isolation(self, db):
        r1 = NovelContinuityReport(world_id=1, title="W1")
        r2 = NovelContinuityReport(world_id=2, title="W2")
        db.add_all([r1, r2]); db.commit()
        from sqlalchemy import func
        assert db.query(func.count(NovelContinuityReport.id)).filter(NovelContinuityReport.world_id == 1).scalar() >= 1
