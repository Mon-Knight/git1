"""
v2.1.0 — Novel Quality Report Model Tests
验证 NovelDraftQualityReport 模型创建、字段、跨世界隔离。
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import NovelDraftQualityReport, NovelDraft, World
from datetime import datetime, timezone


@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        yield db
    finally:
        db.close()


def _create_test_world(db):
    w = World(name="测试世界", world_type="科幻")
    db.add(w)
    db.commit()
    db.refresh(w)
    return w


def _create_test_draft(db, world_id):
    d = NovelDraft(
        world_id=world_id,
        chapter_outline_id=1,
        volume_index=1,
        chapter_index=1,
        title="测试草稿",
        content="正文内容示例。",
        status="candidate",
    )
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


class TestNovelDraftQualityReportModel:
    """Model creation and field tests."""

    def test_report_create_basic(self, test_db):
        """QualityReport 模型可创建."""
        world = _create_test_world(test_db)
        draft = _create_test_draft(test_db, world.id)
        report = NovelDraftQualityReport(
            world_id=world.id,
            draft_id=draft.id,
            title="测试报告",
            overall_score=85,
            status="candidate",
        )
        test_db.add(report)
        test_db.commit()

        assert report.id is not None
        assert report.world_id == world.id
        assert report.draft_id == draft.id
        assert report.status == "candidate"

    def test_report_default_status_candidate(self, test_db):
        """默认 status 为 candidate."""
        world = _create_test_world(test_db)
        draft = _create_test_draft(test_db, world.id)
        report = NovelDraftQualityReport(
            world_id=world.id,
            draft_id=draft.id,
        )
        test_db.add(report)
        test_db.commit()
        assert report.status == "candidate"

    def test_report_is_current_default_false(self, test_db):
        """is_current 默认为 False."""
        world = _create_test_world(test_db)
        draft = _create_test_draft(test_db, world.id)
        report = NovelDraftQualityReport(
            world_id=world.id,
            draft_id=draft.id,
        )
        test_db.add(report)
        test_db.commit()
        assert report.is_current is False

    def test_report_saves_chinese_json(self, test_db):
        """result_json 可保存中文."""
        world = _create_test_world(test_db)
        draft = _create_test_draft(test_db, world.id)
        chinese_json = '{"title": "中文检查报告", "summary": "整体评价很好"}'
        report = NovelDraftQualityReport(
            world_id=world.id,
            draft_id=draft.id,
            result_json=chinese_json,
        )
        test_db.add(report)
        test_db.commit()
        assert "中文检查报告" in report.result_json

    def test_report_saves_scores(self, test_db):
        """各维度评分可保存."""
        world = _create_test_world(test_db)
        draft = _create_test_draft(test_db, world.id)
        report = NovelDraftQualityReport(
            world_id=world.id,
            draft_id=draft.id,
            overall_score=82,
            outline_alignment_score=85,
            world_consistency_score=80,
            character_consistency_score=78,
            plot_coherence_score=84,
            pacing_score=76,
            prose_score=82,
            hook_score=88,
        )
        test_db.add(report)
        test_db.commit()
        assert report.overall_score == 82
        assert report.outline_alignment_score == 85
        assert report.hook_score == 88

    def test_report_cross_world_isolation(self, test_db):
        """跨世界隔离基础检查."""
        world_a = _create_test_world(test_db)
        world_b = World(name="世界B")
        test_db.add(world_b)
        test_db.commit()

        draft_a = _create_test_draft(test_db, world_a.id)
        report_a = NovelDraftQualityReport(
            world_id=world_a.id,
            draft_id=draft_a.id,
        )
        test_db.add(report_a)
        test_db.commit()

        # Check that report belongs to world A
        from_db = test_db.query(NovelDraftQualityReport).filter_by(
            id=report_a.id, world_id=world_a.id
        ).first()
        assert from_db is not None

        # Check that report is NOT found under world B
        from_b = test_db.query(NovelDraftQualityReport).filter_by(
            id=report_a.id, world_id=world_b.id
        ).first()
        assert from_b is None

    def test_report_draft_relationship(self, test_db):
        """报告与草稿关联正确."""
        world = _create_test_world(test_db)
        draft = _create_test_draft(test_db, world.id)
        report = NovelDraftQualityReport(
            world_id=world.id,
            draft_id=draft.id,
        )
        test_db.add(report)
        test_db.commit()
        test_db.refresh(report)

        assert report.draft is not None
        assert report.draft.id == draft.id

    def test_multiple_reports_same_draft(self, test_db):
        """同一篇正文草稿可以有多份检查报告."""
        world = _create_test_world(test_db)
        draft = _create_test_draft(test_db, world.id)

        r1 = NovelDraftQualityReport(world_id=world.id, draft_id=draft.id)
        r2 = NovelDraftQualityReport(world_id=world.id, draft_id=draft.id)
        r3 = NovelDraftQualityReport(world_id=world.id, draft_id=draft.id)
        test_db.add_all([r1, r2, r3])
        test_db.commit()

        count = test_db.query(NovelDraftQualityReport).filter_by(
            draft_id=draft.id
        ).count()
        assert count == 3
