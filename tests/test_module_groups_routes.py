"""
AI World Engine - Test Module Groups Routes
Tests for module groups display on world detail page.
"""

import pytest
from app.models import World


def _create_world(client) -> int:
    """Create a test world via the API and return its ID."""
    response = client.post(
        "/worlds",
        data={
            "name": "测试世界",
            "world_type": "奇幻",
            "description": "测试",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    # Get world ID from redirect
    # The redirect goes to /worlds, so just get the first world
    worlds_resp = client.get("/worlds")
    # Create another approach: get it from a redirect or health
    # Simpler: just find from list page content
    import re
    # Navigate to world list and find the world link
    list_resp = client.get("/worlds")
    match = re.search(r'/worlds/(\d+)', list_resp.text)
    if match:
        return int(match.group(1))
    raise RuntimeError("Could not find world ID from list page")


class TestModuleGroupsRoutes:
    """Tests for module groups display on world detail page."""

    def test_world_detail_returns_200(self, client):
        """GET /worlds/{id} returns 200."""
        w_id = _create_world(client)
        response = client.get(f"/worlds/{w_id}")
        assert response.status_code == 200

    def test_page_contains_module_group_nav(self, client):
        """Page should contain 功能分组导航."""
        w_id = _create_world(client)
        response = client.get(f"/worlds/{w_id}")
        assert "功能分组导航" in response.text

    def test_page_contains_world_library(self, client):
        """Page should contain 设定库."""
        w_id = _create_world(client)
        response = client.get(f"/worlds/{w_id}")
        assert "设定库" in response.text

    def test_page_contains_story_history(self, client):
        """Page should contain 剧情历史."""
        w_id = _create_world(client)
        response = client.get(f"/worlds/{w_id}")
        assert "剧情历史" in response.text

    def test_page_contains_ai_simulation(self, client):
        """Page should contain AI 推演."""
        w_id = _create_world(client)
        response = client.get(f"/worlds/{w_id}")
        assert "AI 推演" in response.text

    def test_page_contains_novel_engineering(self, client):
        """Page should contain 小说工程."""
        w_id = _create_world(client)
        response = client.get(f"/worlds/{w_id}")
        assert "小说工程" in response.text

    def test_page_contains_creative_assets(self, client):
        """Page should contain 创作资产."""
        w_id = _create_world(client)
        response = client.get(f"/worlds/{w_id}")
        assert "创作资产" in response.text

    def test_page_contains_checks(self, client):
        """Page should contain 检查中心."""
        w_id = _create_world(client)
        response = client.get(f"/worlds/{w_id}")
        assert "检查中心" in response.text

    def test_page_contains_data_settings(self, client):
        """Page should contain 数据与设置."""
        w_id = _create_world(client)
        response = client.get(f"/worlds/{w_id}")
        assert "数据与设置" in response.text

    def test_page_contains_subnav(self, client):
        """Page should contain dashboard-subnav for secondary navigation."""
        w_id = _create_world(client)
        response = client.get(f"/worlds/{w_id}")
        assert "dashboard-subnav" in response.text

    def test_page_contains_character_entry(self, client):
        """Page should contain 角色管理 entry."""
        w_id = _create_world(client)
        response = client.get(f"/worlds/{w_id}")
        assert "角色管理" in response.text

    def test_page_contains_faction_entry(self, client):
        """Page should contain 势力管理 entry."""
        w_id = _create_world(client)
        response = client.get(f"/worlds/{w_id}")
        assert "势力管理" in response.text

    def test_page_contains_location_entry(self, client):
        """Page should contain 地点管理 entry."""
        w_id = _create_world(client)
        response = client.get(f"/worlds/{w_id}")
        assert "地点管理" in response.text

    def test_page_contains_rule_entry(self, client):
        """Page should contain 规则管理 entry."""
        w_id = _create_world(client)
        response = client.get(f"/worlds/{w_id}")
        assert "规则管理" in response.text

    def test_page_contains_historical_events_entry(self, client):
        """Page should contain 历史事件 entry."""
        w_id = _create_world(client)
        response = client.get(f"/worlds/{w_id}")
        assert "历史事件" in response.text

    def test_page_contains_timeline_entry(self, client):
        """Page should contain 时间线 entry."""
        w_id = _create_world(client)
        response = client.get(f"/worlds/{w_id}")
        assert "时间线" in response.text

    def test_page_contains_simulation_entry(self, client):
        """Page should contain AI 推演 entry."""
        w_id = _create_world(client)
        response = client.get(f"/worlds/{w_id}")
        assert "开始 AI 推演" in response.text

    def test_page_contains_records_entry(self, client):
        """Page should contain 推演记录 entry."""
        w_id = _create_world(client)
        response = client.get(f"/worlds/{w_id}")
        assert "推演记录" in response.text

    def test_page_contains_branches_entry(self, client):
        """Page should contain 分支记录 entry."""
        w_id = _create_world(client)
        response = client.get(f"/worlds/{w_id}")
        assert "分支记录" in response.text

    def test_page_contains_evolution_entry(self, client):
        """Page should contain 全书演化 entry."""
        w_id = _create_world(client)
        response = client.get(f"/worlds/{w_id}")
        assert "全书演化推演" in response.text

    def test_page_contains_context_entry(self, client):
        """Page should contain 创作上下文 entry."""
        w_id = _create_world(client)
        response = client.get(f"/worlds/{w_id}")
        assert "创作上下文" in response.text

    def test_page_contains_checks_entry(self, client):
        """Page should contain check center entry."""
        w_id = _create_world(client)
        response = client.get(f"/worlds/{w_id}")
        assert "设定矛盾检查" in response.text

    def test_page_shows_future_version_hint(self, client):
        """Page should contain 后续版本开放."""
        w_id = _create_world(client)
        response = client.get(f"/worlds/{w_id}")
        assert "后续版本开放" in response.text

    def test_nonexistent_world_returns_404(self, client):
        """Non-existent world_id should return 404."""
        response = client.get("/worlds/99999")
        assert response.status_code == 404

    def test_page_still_contains_app_shell(self, client):
        """Page should still contain the app shell (base.html elements)."""
        w_id = _create_world(client)
        response = client.get(f"/worlds/{w_id}")
        assert "app-shell" in response.text or "site-header" in response.text

    def test_old_routes_still_accessible(self, client):
        """All old routes should still be accessible."""
        w_id = _create_world(client)

        old_routes = [
            f"/worlds/{w_id}",
            f"/worlds/{w_id}/edit",
            f"/worlds/{w_id}/characters",
            f"/worlds/{w_id}/factions",
            f"/worlds/{w_id}/locations",
            f"/worlds/{w_id}/rules",
            f"/worlds/{w_id}/events",
            f"/worlds/{w_id}/timeline",
            f"/worlds/{w_id}/simulation",
            f"/worlds/{w_id}/records",
            f"/worlds/{w_id}/branches",
            f"/worlds/{w_id}/checks",
            f"/worlds/{w_id}/checks/conflicts",
            f"/worlds/{w_id}/checks/behavior",
            f"/worlds/{w_id}/context",
        ]

        for route in old_routes:
            response = client.get(route)
            assert response.status_code == 200, (
                f"Route {route} returned {response.status_code}"
            )
