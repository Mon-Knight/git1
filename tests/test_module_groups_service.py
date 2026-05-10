"""
AI World Engine - Test Module Groups Service
Tests for WorldDashboardService.get_world_module_groups().
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
from app.models import World


def _create_world(db, name="测试世界") -> int:
    world = World(name=name)
    db.add(world)
    db.commit()
    return world.id


class TestModuleGroups:
    """Tests for get_world_module_groups."""

    def test_returns_7_groups(self, db):
        """Should return exactly 7 groups."""
        w_id = _create_world(db)
        groups = WorldDashboardService.get_world_module_groups(db, w_id)
        assert len(groups) == 7, f"Expected 7 groups, got {len(groups)}"

    def test_has_world_library_group(self, db):
        """Group list should include 设定库."""
        w_id = _create_world(db)
        groups = WorldDashboardService.get_world_module_groups(db, w_id)
        keys = [g["key"] for g in groups]
        assert "world_library" in keys
        group = next(g for g in groups if g["key"] == "world_library")
        assert group["title"] == "设定库"

    def test_has_story_history_group(self, db):
        """Group list should include 剧情历史."""
        w_id = _create_world(db)
        groups = WorldDashboardService.get_world_module_groups(db, w_id)
        keys = [g["key"] for g in groups]
        assert "story_history" in keys
        group = next(g for g in groups if g["key"] == "story_history")
        assert group["title"] == "剧情历史"

    def test_has_ai_simulation_group(self, db):
        """Group list should include AI 推演."""
        w_id = _create_world(db)
        groups = WorldDashboardService.get_world_module_groups(db, w_id)
        keys = [g["key"] for g in groups]
        assert "ai_simulation" in keys
        group = next(g for g in groups if g["key"] == "ai_simulation")
        assert group["title"] == "AI 推演"

    def test_has_novel_engineering_group(self, db):
        """Group list should include 小说工程."""
        w_id = _create_world(db)
        groups = WorldDashboardService.get_world_module_groups(db, w_id)
        keys = [g["key"] for g in groups]
        assert "novel_engineering" in keys
        group = next(g for g in groups if g["key"] == "novel_engineering")
        assert group["title"] == "小说工程"

    def test_has_creative_assets_group(self, db):
        """Group list should include 创作资产."""
        w_id = _create_world(db)
        groups = WorldDashboardService.get_world_module_groups(db, w_id)
        keys = [g["key"] for g in groups]
        assert "creative_assets" in keys
        group = next(g for g in groups if g["key"] == "creative_assets")
        assert group["title"] == "创作资产"

    def test_has_checks_group(self, db):
        """Group list should include 检查中心."""
        w_id = _create_world(db)
        groups = WorldDashboardService.get_world_module_groups(db, w_id)
        keys = [g["key"] for g in groups]
        assert "checks" in keys
        group = next(g for g in groups if g["key"] == "checks")
        assert group["title"] == "检查中心"

    def test_has_data_settings_group(self, db):
        """Group list should include 数据与设置."""
        w_id = _create_world(db)
        groups = WorldDashboardService.get_world_module_groups(db, w_id)
        keys = [g["key"] for g in groups]
        assert "data_settings" in keys
        group = next(g for g in groups if g["key"] == "data_settings")
        assert group["title"] == "数据与设置"

    def test_world_library_has_character_faction_location_rule_links(self, db):
        """设定库 should contain links for 角色/势力/地点/规则."""
        w_id = _create_world(db)
        groups = WorldDashboardService.get_world_module_groups(db, w_id)
        group = next(g for g in groups if g["key"] == "world_library")
        labels = [link["label"] for link in group["links"]]
        assert "角色管理" in labels
        assert "势力管理" in labels
        assert "地点管理" in labels
        assert "规则管理" in labels

    def test_novel_engineering_has_evolution_link(self, db):
        """小说工程 should contain 全书演化 link."""
        w_id = _create_world(db)
        groups = WorldDashboardService.get_world_module_groups(db, w_id)
        group = next(g for g in groups if g["key"] == "novel_engineering")
        labels = [link["label"] for link in group["links"]]
        assert "全书演化推演" in labels
        assert "演化方案列表" in labels

    def test_novel_engineering_future_items_are_disabled(self, db):
        """小说工程中 分卷/章节/正文 should be disabled."""
        w_id = _create_world(db)
        groups = WorldDashboardService.get_world_module_groups(db, w_id)
        group = next(g for g in groups if g["key"] == "novel_engineering")
        future_links = [link for link in group["links"] if link["disabled"]]
        future_labels = {link["label"] for link in future_links}
        assert "分卷大纲" in future_labels
        assert "章节大纲" in future_labels
        assert "正文生成" in future_labels
        for link in future_links:
            assert link["url"] == ""

    def test_checks_future_items_are_disabled(self, db):
        """检查中心中 future check items should be disabled."""
        w_id = _create_world(db)
        groups = WorldDashboardService.get_world_module_groups(db, w_id)
        group = next(g for g in groups if g["key"] == "checks")
        future_links = [link for link in group["links"] if link["disabled"]]
        future_labels = {link["label"] for link in future_links}
        assert "时间线冲突检查" in future_labels
        assert "正文一致性检查" in future_labels
        assert "风格一致性检查" in future_labels

    def test_all_world_links_contain_correct_world_id(self, db):
        """All world-scoped links should contain the correct world_id."""
        w_id = _create_world(db)
        groups = WorldDashboardService.get_world_module_groups(db, w_id)
        for group in groups:
            for link in group["links"]:
                if not link["disabled"] and link["url"].startswith("/worlds/"):
                    assert f"/worlds/{w_id}" in link["url"], (
                        f"Link '{link['label']}' URL '{link['url']}' "
                        f"does not contain correct world_id {w_id}"
                    )

    def test_empty_world_returns_groups(self, db):
        """Empty world should still return 7 groups."""
        w_id = _create_world(db, "空世界")
        groups = WorldDashboardService.get_world_module_groups(db, w_id)
        assert len(groups) == 7
        for group in groups:
            assert "key" in group
            assert "title" in group
            assert "description" in group
            assert "links" in group
            assert "stats" in group

    def test_no_cross_world_links(self, db):
        """Links should not reference other world IDs."""
        world1 = World(name="世界1")
        world2 = World(name="世界2")
        db.add_all([world1, world2])
        db.commit()

        groups = WorldDashboardService.get_world_module_groups(db, world1.id)
        for group in groups:
            for link in group["links"]:
                if not link["disabled"] and link["url"].startswith("/worlds/"):
                    assert f"/worlds/{world2.id}" not in link["url"], (
                        f"Link '{link['label']}' references world2 ({world2.id})"
                    )

    def test_each_group_has_anchor(self, db):
        """Each group should have an anchor for in-page navigation."""
        w_id = _create_world(db)
        groups = WorldDashboardService.get_world_module_groups(db, w_id)
        for group in groups:
            assert "anchor" in group
            assert isinstance(group["anchor"], str)
            assert len(group["anchor"]) > 0
