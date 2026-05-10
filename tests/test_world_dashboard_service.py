"""
AI World Engine - Test World Dashboard Service
Tests for WorldDashboardService.
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


from app.services.world_dashboard_service import WorldDashboardService
from app.services.world_service import WorldService
from app.services.simulation_service import SimulationService
from app.services.context_package_service import ContextPackageService
from app.services.style_profile_service import StyleProfileService
from app.services.plot_anchor_service import PlotAnchorService
from app.models import Character, Faction, Location, WorldRule, HistoricalEvent


def _create_world(db) -> int:
    return WorldService.create_world(db, name="W", world_type="奇幻").id


class TestWorldDashboardSummary:
    """Tests for get_world_dashboard_summary."""

    def test_empty_world(self, db):
        w_id = _create_world(db)
        s = WorldDashboardService.get_world_dashboard_summary(db, w_id)
        assert s["character_count"] == 0
        assert s["faction_count"] == 0
        assert s["context_package_count"] == 0

    def test_with_character(self, db):
        w_id = _create_world(db)
        db.add(Character(world_id=w_id, name="C"))
        db.commit()
        s = WorldDashboardService.get_world_dashboard_summary(db, w_id)
        assert s["character_count"] == 1

    def test_with_faction(self, db):
        w_id = _create_world(db)
        db.add(Faction(world_id=w_id, name="F"))
        db.commit()
        s = WorldDashboardService.get_world_dashboard_summary(db, w_id)
        assert s["faction_count"] == 1

    def test_with_location(self, db):
        w_id = _create_world(db)
        db.add(Location(world_id=w_id, name="L"))
        db.commit()
        s = WorldDashboardService.get_world_dashboard_summary(db, w_id)
        assert s["location_count"] == 1

    def test_with_rule(self, db):
        w_id = _create_world(db)
        db.add(WorldRule(world_id=w_id, name="R"))
        db.commit()
        s = WorldDashboardService.get_world_dashboard_summary(db, w_id)
        assert s["rule_count"] == 1

    def test_with_canon_event(self, db):
        w_id = _create_world(db)
        db.add(HistoricalEvent(world_id=w_id, title="E", is_canon=True))
        db.commit()
        s = WorldDashboardService.get_world_dashboard_summary(db, w_id)
        assert s["canon_event_count"] == 1

    def test_with_pending_simulation(self, db):
        w_id = _create_world(db)
        SimulationService.create_simulation_record(db=db, world_id=w_id, question="P", ai_response="R")
        s = WorldDashboardService.get_world_dashboard_summary(db, w_id)
        assert s["pending_simulation_count"] == 1

    def test_with_branch(self, db):
        w_id = _create_world(db)
        sim = SimulationService.create_simulation_record(db=db, world_id=w_id, question="B", ai_response="R")
        from app.models import Branch
        db.add(Branch(world_id=w_id, simulation_id=sim.id, branch_name="Br"))
        db.commit()
        s = WorldDashboardService.get_world_dashboard_summary(db, w_id)
        assert s["branch_count"] == 1

    def test_with_context_package(self, db):
        w_id = _create_world(db)
        ContextPackageService.create_context_package(db=db, world_id=w_id, name="Pkg")
        s = WorldDashboardService.get_world_dashboard_summary(db, w_id)
        assert s["context_package_count"] == 1

    def test_with_style_profile(self, db):
        w_id = _create_world(db)
        StyleProfileService.create_style_profile(db=db, world_id=w_id, name="S")
        s = WorldDashboardService.get_world_dashboard_summary(db, w_id)
        assert s["style_profile_count"] >= 1

    def test_with_plot_anchor(self, db):
        w_id = _create_world(db)
        PlotAnchorService.create_plot_anchor(db=db, world_id=w_id, name="A")
        s = WorldDashboardService.get_world_dashboard_summary(db, w_id)
        assert s["plot_anchor_count"] == 1

    def test_novel_evolution_count(self, db):
        w_id = _create_world(db)
        SimulationService.create_simulation_record(
            db=db, world_id=w_id, question="E", simulation_type="novel_evolution", ai_response="R"
        )
        s = WorldDashboardService.get_world_dashboard_summary(db, w_id)
        assert s["novel_evolution_count"] == 1

    def test_mainline_count(self, db):
        w_id = _create_world(db)
        r = SimulationService.create_simulation_record(
            db=db, world_id=w_id, question="M", simulation_type="novel_evolution", ai_response="R"
        )
        r.status = "adopted"; db.commit()
        s = WorldDashboardService.get_world_dashboard_summary(db, w_id)
        assert s["mainline_evolution_count"] == 1

    def test_candidate_count(self, db):
        w_id = _create_world(db)
        r = SimulationService.create_simulation_record(
            db=db, world_id=w_id, question="C", simulation_type="novel_evolution", ai_response="R"
        )
        r.status = "branched"; db.commit()
        s = WorldDashboardService.get_world_dashboard_summary(db, w_id)
        assert s["candidate_evolution_count"] == 1


class TestWorldRecommendations:
    """Tests for get_world_recommendations."""

    def test_empty_world_suggests_characters(self, db):
        w_id = _create_world(db)
        recs = WorldDashboardService.get_world_recommendations(db, w_id)
        titles = [r["title"] for r in recs]
        assert any("角色" in t for t in titles)
        assert any("势力" in t for t in titles)

    def test_with_package_no_evolution_suggests_evolution(self, db):
        w_id = _create_world(db)
        ContextPackageService.create_context_package(db=db, world_id=w_id, name="P")
        recs = WorldDashboardService.get_world_recommendations(db, w_id)
        titles = [r["title"] for r in recs]
        assert any("全书演化" in t for t in titles)

    def test_with_pending_evolution_suggests_review(self, db):
        w_id = _create_world(db)
        SimulationService.create_simulation_record(
            db=db, world_id=w_id, question="PE", simulation_type="novel_evolution", ai_response="R"
        )
        recs = WorldDashboardService.get_world_recommendations(db, w_id)
        titles = [r["title"] for r in recs]
        assert any("待确认" in t for t in titles)


class TestRecentActivity:
    """Tests for get_world_recent_activity."""

    def test_empty_world(self, db):
        w_id = _create_world(db)
        items = WorldDashboardService.get_world_recent_activity(db, w_id)
        assert len(items) == 0

    def test_with_event(self, db):
        w_id = _create_world(db)
        db.add(HistoricalEvent(world_id=w_id, title="Event1", is_canon=True))
        db.commit()
        items = WorldDashboardService.get_world_recent_activity(db, w_id)
        assert len(items) >= 1


class TestQuickActions:
    """Tests for get_world_quick_actions."""

    def test_returns_actions(self, db):
        w_id = _create_world(db)
        actions = WorldDashboardService.get_world_quick_actions(w_id)
        labels = [a["label"] for a in actions]
        assert "编辑世界" in labels
        assert "AI 推演" in labels
        assert "全书演化" in labels
        assert "创作上下文" in labels
