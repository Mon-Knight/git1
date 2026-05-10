"""
AI World Engine - Test Context Services
Tests for StyleProfileService, PlotAnchorService, and ContextPackageService.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
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
from app.services.style_profile_service import StyleProfileService
from app.services.plot_anchor_service import PlotAnchorService
from app.services.context_package_service import ContextPackageService
from app.services.simulation_service import SimulationService


def _create_world(db: Session) -> int:
    world = WorldService.create_world(db, name="测试世界", world_type="奇幻")
    return world.id


def _create_sim_record(db: Session, world_id: int) -> int:
    record = SimulationService.create_simulation_record(
        db=db,
        world_id=world_id,
        question="测试推演问题",
        simulation_type="novel_evolution",
        ai_response="测试AI回复",
    )
    return record.id


class TestStyleProfileService:
    """Tests for StyleProfileService."""

    def test_create_style_profile(self, db: Session):
        w_id = _create_world(db)
        sp = StyleProfileService.create_style_profile(
            db=db, world_id=w_id, name="理性风格", genre="奇幻"
        )
        assert sp.id is not None
        assert sp.name == "理性风格"
        assert sp.genre == "奇幻"
        assert sp.world_id == w_id

    def test_create_global_style_profile(self, db: Session):
        sp = StyleProfileService.create_style_profile(
            db=db, world_id=None, name="全局风格", genre="通用"
        )
        assert sp.world_id is None
        assert sp.name == "全局风格"

    def test_get_style_profile(self, db: Session):
        w_id = _create_world(db)
        sp = StyleProfileService.create_style_profile(db=db, world_id=w_id, name="测试")
        fetched = StyleProfileService.get_style_profile(db, sp.id)
        assert fetched is not None
        assert fetched.name == "测试"

    def test_get_nonexistent_style_profile(self, db: Session):
        sp = StyleProfileService.get_style_profile(db, 999)
        assert sp is None

    def test_list_style_profiles(self, db: Session):
        w_id = _create_world(db)
        StyleProfileService.create_style_profile(db=db, world_id=w_id, name="A")
        StyleProfileService.create_style_profile(db=db, world_id=None, name="B")
        profiles = StyleProfileService.list_style_profiles(db)
        assert len(profiles) == 2

    def test_list_available_for_world(self, db: Session):
        w_id = _create_world(db)
        w2_id = _create_world(db)  # second world
        StyleProfileService.create_style_profile(db=db, world_id=w_id, name="World1Style")
        StyleProfileService.create_style_profile(db=db, world_id=w2_id, name="World2Style")
        StyleProfileService.create_style_profile(db=db, world_id=None, name="GlobalStyle")

        available = StyleProfileService.list_available_style_profiles_for_world(db, w_id)
        # Should get world-specific + global
        names = [s.name for s in available]
        assert "World1Style" in names
        assert "GlobalStyle" in names
        assert "World2Style" not in names

    def test_update_style_profile(self, db: Session):
        w_id = _create_world(db)
        sp = StyleProfileService.create_style_profile(db=db, world_id=w_id, name="Original")
        updated = StyleProfileService.update_style_profile(
            db=db, profile_id=sp.id, name="Changed", genre="科幻"
        )
        assert updated is not None
        assert updated.name == "Changed"
        assert updated.genre == "科幻"

    def test_update_nonexistent(self, db: Session):
        result = StyleProfileService.update_style_profile(db=db, profile_id=999, name="X")
        assert result is None

    def test_delete_style_profile(self, db: Session):
        w_id = _create_world(db)
        sp = StyleProfileService.create_style_profile(db=db, world_id=w_id, name="ToDelete")
        assert StyleProfileService.delete_style_profile(db, sp.id) is True
        assert StyleProfileService.get_style_profile(db, sp.id) is None

    def test_delete_nonexistent(self, db: Session):
        assert StyleProfileService.delete_style_profile(db, 999) is False

    def test_delete_referenced_style_profile(self, db: Session):
        """Deleting a referenced style profile should fail."""
        w_id = _create_world(db)
        sp = StyleProfileService.create_style_profile(db=db, world_id=w_id, name="Referenced")
        sim_id = _create_sim_record(db, w_id)
        ContextPackageService.create_context_package(
            db=db, world_id=w_id, name="Pkg", style_profile_id=sp.id,
            simulation_record_id=sim_id,
        )
        assert StyleProfileService.delete_style_profile(db, sp.id) is False


class TestPlotAnchorService:
    """Tests for PlotAnchorService."""

    def test_create_plot_anchor(self, db: Session):
        w_id = _create_world(db)
        anchor = PlotAnchorService.create_plot_anchor(
            db=db, world_id=w_id, name="第一卷开篇", stage="第一卷"
        )
        assert anchor.id is not None
        assert anchor.name == "第一卷开篇"
        assert anchor.stage == "第一卷"
        assert anchor.world_id == w_id

    def test_list_plot_anchors_by_world_isolation(self, db: Session):
        w1_id = _create_world(db)
        w2_id = _create_world(db)
        PlotAnchorService.create_plot_anchor(db=db, world_id=w1_id, name="W1Anchor")
        PlotAnchorService.create_plot_anchor(db=db, world_id=w2_id, name="W2Anchor")

        w1_anchors = PlotAnchorService.list_plot_anchors_by_world(db, w1_id)
        assert len(w1_anchors) == 1
        assert w1_anchors[0].name == "W1Anchor"

    def test_update_plot_anchor(self, db: Session):
        w_id = _create_world(db)
        anchor = PlotAnchorService.create_plot_anchor(db=db, world_id=w_id, name="Old")
        updated = PlotAnchorService.update_plot_anchor(
            db=db, anchor_id=anchor.id, name="New"
        )
        assert updated is not None
        assert updated.name == "New"

    def test_delete_plot_anchor(self, db: Session):
        w_id = _create_world(db)
        anchor = PlotAnchorService.create_plot_anchor(db=db, world_id=w_id, name="Delete")
        assert PlotAnchorService.delete_plot_anchor(db, anchor.id) is True
        assert PlotAnchorService.get_plot_anchor(db, anchor.id) is None

    def test_delete_referenced_plot_anchor(self, db: Session):
        w_id = _create_world(db)
        anchor = PlotAnchorService.create_plot_anchor(db=db, world_id=w_id, name="Ref")
        sim_id = _create_sim_record(db, w_id)
        ContextPackageService.create_context_package(
            db=db, world_id=w_id, name="Pkg", plot_anchor_id=anchor.id,
            simulation_record_id=sim_id,
        )
        assert PlotAnchorService.delete_plot_anchor(db, anchor.id) is False


class TestContextPackageService:
    """Tests for ContextPackageService."""

    def test_create_context_package(self, db: Session):
        w_id = _create_world(db)
        pkg = ContextPackageService.create_context_package(
            db=db, world_id=w_id, name="测试包", generation_type="章节正文"
        )
        assert pkg.id is not None
        assert pkg.name == "测试包"
        assert pkg.world_id == w_id

    def test_create_with_references(self, db: Session):
        w_id = _create_world(db)
        sim_id = _create_sim_record(db, w_id)
        sp = StyleProfileService.create_style_profile(db=db, world_id=w_id, name="Style")
        anchor = PlotAnchorService.create_plot_anchor(db=db, world_id=w_id, name="Anchor")

        pkg = ContextPackageService.create_context_package(
            db=db, world_id=w_id, name="FullPkg",
            simulation_record_id=sim_id,
            style_profile_id=sp.id,
            plot_anchor_id=anchor.id,
        )
        assert pkg.simulation_record_id == sim_id
        assert pkg.style_profile_id == sp.id
        assert pkg.plot_anchor_id == anchor.id

    def test_create_with_global_style(self, db: Session):
        w_id = _create_world(db)
        sp = StyleProfileService.create_style_profile(db=db, world_id=None, name="Global")
        pkg = ContextPackageService.create_context_package(
            db=db, world_id=w_id, name="GlobalPkg", style_profile_id=sp.id
        )
        assert pkg.style_profile_id == sp.id

    def test_create_with_cross_world_sim_record_fails(self, db: Session):
        w1_id = _create_world(db)
        w2_id = _create_world(db)
        sim_id = _create_sim_record(db, w2_id)
        with pytest.raises(ValueError, match="推演记录不属于当前世界"):
            ContextPackageService.create_context_package(
                db=db, world_id=w1_id, name="Bad", simulation_record_id=sim_id
            )

    def test_create_with_cross_world_plot_anchor_fails(self, db: Session):
        w1_id = _create_world(db)
        w2_id = _create_world(db)
        anchor = PlotAnchorService.create_plot_anchor(db=db, world_id=w2_id, name="W2Anchor")
        with pytest.raises(ValueError, match="剧情时间点不属于当前世界"):
            ContextPackageService.create_context_package(
                db=db, world_id=w1_id, name="Bad", plot_anchor_id=anchor.id
            )

    def test_create_with_nonexistent_sim_record(self, db: Session):
        w_id = _create_world(db)
        with pytest.raises(ValueError, match="推演记录不存在"):
            ContextPackageService.create_context_package(
                db=db, world_id=w_id, name="Bad", simulation_record_id=999
            )

    def test_list_by_world_isolation(self, db: Session):
        w1_id = _create_world(db)
        w2_id = _create_world(db)
        ContextPackageService.create_context_package(db=db, world_id=w1_id, name="W1Pkg")
        ContextPackageService.create_context_package(db=db, world_id=w2_id, name="W2Pkg")

        w1_pkgs = ContextPackageService.list_context_packages_by_world(db, w1_id)
        assert len(w1_pkgs) == 1
        assert w1_pkgs[0].name == "W1Pkg"

    def test_update_context_package(self, db: Session):
        w_id = _create_world(db)
        pkg = ContextPackageService.create_context_package(db=db, world_id=w_id, name="Old")
        updated = ContextPackageService.update_context_package(
            db=db, package_id=pkg.id, name="New", strict_canon=False
        )
        assert updated is not None
        assert updated.name == "New"
        assert updated.strict_canon is False

    def test_delete_context_package(self, db: Session):
        w_id = _create_world(db)
        pkg = ContextPackageService.create_context_package(db=db, world_id=w_id, name="Del")
        assert ContextPackageService.delete_context_package(db, pkg.id) is True
        assert ContextPackageService.get_context_package(db, pkg.id) is None

    def test_list_eligible_sim_records(self, db: Session):
        w_id = _create_world(db)
        _create_sim_record(db, w_id)  # novel_evolution
        SimulationService.create_simulation_record(
            db=db, world_id=w_id, question="Other", simulation_type="general"
        )
        SimulationService.create_simulation_record(
            db=db, world_id=w_id, question="Discarded", simulation_type="novel_evolution"
        )
        # Mark last as discarded
        from app.models import SimulationRecord
        discarded = db.query(SimulationRecord).order_by(SimulationRecord.id.desc()).first()
        discarded.status = "discarded"
        db.commit()

        eligible = ContextPackageService.list_eligible_simulation_records(db, w_id)
        # Should have 2 (not the discarded one)
        assert len(eligible) == 2
        for r in eligible:
            assert r.status != "discarded"

    def test_build_context_package_preview(self, db: Session):
        w_id = _create_world(db)
        sim_id = _create_sim_record(db, w_id)
        sp = StyleProfileService.create_style_profile(db=db, world_id=w_id, name="PreviewStyle")
        anchor = PlotAnchorService.create_plot_anchor(db=db, world_id=w_id, name="PreviewAnchor")

        pkg = ContextPackageService.create_context_package(
            db=db, world_id=w_id, name="PreviewPkg",
            simulation_record_id=sim_id, style_profile_id=sp.id,
            plot_anchor_id=anchor.id,
        )
        preview = ContextPackageService.build_context_package_preview(db, pkg.id)
        assert "error" not in preview
        assert preview["simulation_record"] is not None
        assert preview["style_profile"] is not None
        assert preview["plot_anchor"] is not None
        assert preview["style_profile"]["name"] == "PreviewStyle"

    def test_build_context_for_generation(self, db: Session):
        w_id = _create_world(db)
        sim_id = _create_sim_record(db, w_id)
        sp = StyleProfileService.create_style_profile(db=db, world_id=w_id, name="GenStyle")
        anchor = PlotAnchorService.create_plot_anchor(db=db, world_id=w_id, name="GenAnchor")

        pkg = ContextPackageService.create_context_package(
            db=db, world_id=w_id, name="GenPkg",
            simulation_record_id=sim_id, style_profile_id=sp.id,
            plot_anchor_id=anchor.id,
        )
        ctx = ContextPackageService.build_context_for_generation(db, pkg.id)
        assert "error" not in ctx
        assert ctx["simulation_record_content"] is not None
        assert ctx["style_profile_content"] is not None
        assert ctx["plot_anchor_content"] is not None

    def test_build_preview_empty_package(self, db: Session):
        w_id = _create_world(db)
        pkg = ContextPackageService.create_context_package(db=db, world_id=w_id, name="Empty")
        preview = ContextPackageService.build_context_package_preview(db, pkg.id)
        assert "error" not in preview
        assert preview["simulation_record"] is None
        assert preview["style_profile"] is None
        assert preview["plot_anchor"] is None
