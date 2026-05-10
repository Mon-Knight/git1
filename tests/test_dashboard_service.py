"""
AI World Engine - Test Dashboard Service
Tests for DashboardService data aggregation functions.
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


from app.services.dashboard_service import DashboardService
from app.services.world_service import WorldService
from app.services.simulation_service import SimulationService
from app.services.style_profile_service import StyleProfileService
from app.services.plot_anchor_service import PlotAnchorService
from app.services.context_package_service import ContextPackageService


def _create_world(db) -> int:
    return WorldService.create_world(db, name="测试世界", world_type="奇幻").id


class TestDashboardSummary:
    """Tests for get_dashboard_summary."""

    def test_empty_database(self, db):
        summary = DashboardService.get_dashboard_summary(db)
        assert summary["world_count"] == 0
        assert summary["pending_simulation_count"] == 0
        assert summary["context_package_count"] == 0
        assert summary["novel_evolution_count"] == 0

    def test_with_world(self, db):
        _create_world(db)
        summary = DashboardService.get_dashboard_summary(db)
        assert summary["world_count"] == 1

    def test_pending_simulation_count(self, db):
        w_id = _create_world(db)
        SimulationService.create_simulation_record(
            db=db, world_id=w_id, question="Test", simulation_type="general", ai_response="R"
        )
        summary = DashboardService.get_dashboard_summary(db)
        assert summary["pending_simulation_count"] == 1

    def test_novel_evolution_count(self, db):
        w_id = _create_world(db)
        SimulationService.create_simulation_record(
            db=db, world_id=w_id, question="NE", simulation_type="novel_evolution", ai_response="R"
        )
        summary = DashboardService.get_dashboard_summary(db)
        assert summary["novel_evolution_count"] == 1

    def test_mainline_count(self, db):
        w_id = _create_world(db)
        rec = SimulationService.create_simulation_record(
            db=db, world_id=w_id, question="M", simulation_type="novel_evolution", ai_response="R"
        )
        rec.status = "adopted"
        db.commit()
        summary = DashboardService.get_dashboard_summary(db)
        assert summary["mainline_evolution_count"] == 1

    def test_context_package_count(self, db):
        w_id = _create_world(db)
        ContextPackageService.create_context_package(db=db, world_id=w_id, name="Pkg")
        summary = DashboardService.get_dashboard_summary(db)
        assert summary["context_package_count"] == 1

    def test_style_profile_count(self, db):
        StyleProfileService.create_style_profile(db=db, world_id=None, name="S")
        summary = DashboardService.get_dashboard_summary(db)
        assert summary["style_profile_count"] == 1


class TestRecentWorlds:
    """Tests for get_recent_worlds."""

    def test_empty(self, db):
        worlds = DashboardService.get_recent_worlds(db)
        assert len(worlds) == 0

    def test_with_world(self, db):
        w_id = _create_world(db)
        worlds = DashboardService.get_recent_worlds(db)
        assert len(worlds) == 1
        assert worlds[0]["name"] == "测试世界"
        assert worlds[0]["character_count"] == 0

    def test_limit(self, db):
        for i in range(7):
            WorldService.create_world(db, name=f"W{i}", world_type="奇幻")
        worlds = DashboardService.get_recent_worlds(db, limit=3)
        assert len(worlds) == 3


class TestPendingItems:
    """Tests for get_pending_items."""

    def test_empty(self, db):
        items = DashboardService.get_pending_items(db)
        assert len(items) == 0

    def test_with_pending(self, db):
        w_id = _create_world(db)
        SimulationService.create_simulation_record(
            db=db, world_id=w_id, question="P", simulation_type="general", ai_response="R"
        )
        items = DashboardService.get_pending_items(db)
        assert len(items) == 1
        assert items[0]["world_name"] == "测试世界"


class TestRecentPackages:
    """Tests for get_recent_context_packages."""

    def test_empty(self, db):
        pkgs = DashboardService.get_recent_context_packages(db)
        assert len(pkgs) == 0

    def test_with_package(self, db):
        w_id = _create_world(db)
        ContextPackageService.create_context_package(db=db, world_id=w_id, name="Pkg")
        pkgs = DashboardService.get_recent_context_packages(db)
        assert len(pkgs) == 1
        assert pkgs[0]["name"] == "Pkg"


class TestRecentEvolutions:
    """Tests for get_recent_novel_evolutions."""

    def test_empty(self, db):
        evos = DashboardService.get_recent_novel_evolutions(db)
        assert len(evos) == 0

    def test_with_evolution(self, db):
        w_id = _create_world(db)
        SimulationService.create_simulation_record(
            db=db, world_id=w_id, question="Evo", simulation_type="novel_evolution", ai_response="R"
        )
        evos = DashboardService.get_recent_novel_evolutions(db)
        assert len(evos) == 1


class TestQuickActions:
    """Tests for get_quick_actions."""

    def test_without_world(self):
        actions = DashboardService.get_quick_actions(None)
        labels = [a["label"] for a in actions]
        assert "新建世界" in labels
        assert "世界列表" in labels
        assert "数据管理" in labels
        assert "AI 设置" in labels

    def test_with_world(self):
        actions = DashboardService.get_quick_actions(1)
        labels = [a["label"] for a in actions]
        assert "创作上下文" in labels
        assert "全书演化推演" in labels
