"""
AI World Engine - Test Novel Evolution Service
Tests for NovelEvolutionService.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base

_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
_Session = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


@pytest.fixture()
def db():
    Base.metadata.create_all(bind=_engine)
    session = _Session()
    yield session
    session.rollback()
    session.close()
    Base.metadata.drop_all(bind=_engine)


from app.services.world_service import WorldService
from app.services.simulation_service import SimulationService
from app.services.style_profile_service import StyleProfileService
from app.services.plot_anchor_service import PlotAnchorService
from app.services.context_package_service import ContextPackageService
from app.services.novel_evolution_service import NovelEvolutionService


def _create_world(db) -> int:
    return WorldService.create_world(db, name="测试世界", world_type="奇幻").id


def _create_sim(db, world_id: int, sim_type: str = "novel_evolution") -> int:
    return SimulationService.create_simulation_record(
        db=db, world_id=world_id, question="测试", simulation_type=sim_type,
        ai_response="结果",
    ).id


class TestNovelEvolutionContext:
    """Tests for build_novel_evolution_context."""

    def test_build_context_with_world_only(self, db):
        w_id = _create_world(db)
        ctx = NovelEvolutionService.build_novel_evolution_context(db, w_id, 0)
        assert ctx["error"] is None
        assert ctx["world"] is not None
        assert ctx["world_context"] is not None
        assert ctx["context_package"] is None

    def test_build_context_with_valid_package(self, db):
        w_id = _create_world(db)
        sim_id = _create_sim(db, w_id)
        sp = StyleProfileService.create_style_profile(db=db, world_id=w_id, name="S")
        anchor = PlotAnchorService.create_plot_anchor(db=db, world_id=w_id, name="A")
        pkg = ContextPackageService.create_context_package(
            db=db, world_id=w_id, name="P",
            simulation_record_id=sim_id, style_profile_id=sp.id,
            plot_anchor_id=anchor.id,
        )
        ctx = NovelEvolutionService.build_novel_evolution_context(db, w_id, pkg.id)
        assert ctx["error"] is None
        assert ctx["context_package"] is not None
        assert ctx["pkg_data"] is not None

    def test_build_context_package_not_found(self, db):
        w_id = _create_world(db)
        ctx = NovelEvolutionService.build_novel_evolution_context(db, w_id, 999)
        assert ctx["error"] == "上下文包不存在"

    def test_build_context_cross_world(self, db):
        w1 = _create_world(db)
        w2 = _create_world(db)
        sim_id = _create_sim(db, w2)
        pkg = ContextPackageService.create_context_package(
            db=db, world_id=w2, name="W2Pkg", simulation_record_id=sim_id,
        )
        ctx = NovelEvolutionService.build_novel_evolution_context(db, w1, pkg.id)
        assert ctx["error"] == "上下文包不属于当前世界"


class TestNovelEvolutionPrompt:
    """Tests for build_novel_evolution_prompt."""

    def test_build_prompt_without_package(self, db):
        w_id = _create_world(db)
        ctx = NovelEvolutionService.build_novel_evolution_context(db, w_id, 0)
        messages = NovelEvolutionService.build_novel_evolution_prompt(
            world_context=ctx["world_context"],
            pkg_data=None,
            user_goal="测试目标",
        )
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert "测试目标" in messages[1]["content"]
        assert "世界基础信息" in messages[1]["content"]

    def test_build_prompt_with_package(self, db):
        w_id = _create_world(db)
        sim_id = _create_sim(db, w_id)
        sp = StyleProfileService.create_style_profile(
            db=db, world_id=w_id, name="Style", genre="奇幻", pacing="快速"
        )
        anchor = PlotAnchorService.create_plot_anchor(
            db=db, world_id=w_id, name="Anchor", stage="Vol1"
        )
        pkg = ContextPackageService.create_context_package(
            db=db, world_id=w_id, name="Pkg",
            simulation_record_id=sim_id, style_profile_id=sp.id,
            plot_anchor_id=anchor.id,
        )
        ctx = NovelEvolutionService.build_novel_evolution_context(db, w_id, pkg.id)
        messages = NovelEvolutionService.build_novel_evolution_prompt(
            world_context=ctx["world_context"],
            pkg_data=ctx["pkg_data"],
            user_goal="带包的推演",
        )
        content = messages[1]["content"]
        assert "Style" in content
        assert "Anchor" in content
        assert "Vol1" in content
        assert "创作上下文包信息" in content

    def test_build_prompt_contains_12_section_instruction(self, db):
        w_id = _create_world(db)
        ctx = NovelEvolutionService.build_novel_evolution_context(db, w_id, 0)
        messages = NovelEvolutionService.build_novel_evolution_prompt(
            world_context=ctx["world_context"], user_goal="12章节测试"
        )
        system = messages[0]["content"]
        assert "## 十二、" in system
        assert "结局候选" in system
        assert "设定风险" in system


class TestContextSnapshot:
    """Tests for build_context_snapshot."""

    def test_snapshot_without_package(self, db):
        snap = NovelEvolutionService.build_context_snapshot(1, None, None, "目标")
        assert "world_id" in snap
        assert "user_goal" in snap
        assert '"user_goal": "目标"' in snap

    def test_snapshot_with_package(self, db):
        snap = NovelEvolutionService.build_context_snapshot(
            1, 5,
            {"package_name": "MyPkg", "generation_type": "test", "strict_canon": True},
            "目标"
        )
        assert '"context_package_id": 5' in snap
        assert '"package_name": "MyPkg"' in snap


class TestNovelEvolutionRecords:
    """Tests for save/list/get/status operations."""

    def test_save_and_list(self, db):
        w_id = _create_world(db)
        NovelEvolutionService.save_novel_evolution_record(
            db=db, world_id=w_id, question="Q1",
            ai_response="A1", context_snapshot="{}",
        )
        NovelEvolutionService.save_novel_evolution_record(
            db=db, world_id=w_id, question="Q2",
            ai_response="A2", context_snapshot="{}",
        )
        records = NovelEvolutionService.list_novel_evolution_records(db, w_id)
        assert len(records) == 2
        assert records[0].simulation_type == "novel_evolution"

    def test_get_record(self, db):
        w_id = _create_world(db)
        rec = NovelEvolutionService.save_novel_evolution_record(
            db=db, world_id=w_id, question="Get", ai_response="R", context_snapshot="{}"
        )
        fetched = NovelEvolutionService.get_novel_evolution_record(db, rec.id)
        assert fetched is not None
        assert fetched.question == "Get"

    def test_default_status_pending(self, db):
        w_id = _create_world(db)
        rec = NovelEvolutionService.save_novel_evolution_record(
            db=db, world_id=w_id, question="P", ai_response="R", context_snapshot="{}"
        )
        assert rec.status == "pending"

    def test_set_mainline(self, db):
        w_id = _create_world(db)
        rec = NovelEvolutionService.save_novel_evolution_record(
            db=db, world_id=w_id, question="M", ai_response="R", context_snapshot="{}"
        )
        result = NovelEvolutionService.set_record_status(db, rec.id, "adopted", w_id)
        assert result is not None
        assert result["status"] == "adopted"

    def test_set_candidate(self, db):
        w_id = _create_world(db)
        rec = NovelEvolutionService.save_novel_evolution_record(
            db=db, world_id=w_id, question="C", ai_response="R", context_snapshot="{}"
        )
        result = NovelEvolutionService.set_record_status(db, rec.id, "branched", w_id)
        assert result["status"] == "branched"

    def test_discard(self, db):
        w_id = _create_world(db)
        rec = NovelEvolutionService.save_novel_evolution_record(
            db=db, world_id=w_id, question="D", ai_response="R", context_snapshot="{}"
        )
        result = NovelEvolutionService.set_record_status(db, rec.id, "discarded", w_id)
        assert result["status"] == "discarded"

    def test_cross_world_status_change_rejected(self, db):
        w1 = _create_world(db)
        w2 = _create_world(db)
        rec = NovelEvolutionService.save_novel_evolution_record(
            db=db, world_id=w1, question="X", ai_response="R", context_snapshot="{}"
        )
        result = NovelEvolutionService.set_record_status(db, rec.id, "adopted", w2)
        assert result is None

    def test_non_evolution_record_not_affected(self, db):
        w_id = _create_world(db)
        # Create a non-novel_evolution record
        sim = SimulationService.create_simulation_record(
            db=db, world_id=w_id, question="General", simulation_type="general",
            ai_response="R",
        )
        result = NovelEvolutionService.set_record_status(db, sim.id, "adopted", w_id)
        assert result is None  # Should not match

    def test_get_status_label(self):
        assert NovelEvolutionService.get_status_label("pending") == "待确认"
        assert NovelEvolutionService.get_status_label("adopted") == "主线方案"
        assert NovelEvolutionService.get_status_label("branched") == "备选方案"
        assert NovelEvolutionService.get_status_label("discarded") == "已废弃"

    def test_status_does_not_create_historical_event(self, db):
        w_id = _create_world(db)
        rec = NovelEvolutionService.save_novel_evolution_record(
            db=db, world_id=w_id, question="H", ai_response="R", context_snapshot="{}"
        )
        NovelEvolutionService.set_record_status(db, rec.id, "adopted", w_id)
        from app.models import HistoricalEvent
        events = db.query(HistoricalEvent).filter(HistoricalEvent.world_id == w_id).all()
        assert len(events) == 0
