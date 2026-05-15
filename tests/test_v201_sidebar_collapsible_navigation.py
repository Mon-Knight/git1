"""
v2.0.1 — Sidebar Collapsible Navigation Tests
验证左侧导航折叠、可点击状态与显示逻辑优化。
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, init_db
from app.models import World
import re


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_world():
    """Create a test world and return its ID."""
    init_db()
    db = SessionLocal()
    try:
        world = World(name="导航测试世界", world_type="奇幻", description="测试")
        db.add(world)
        db.commit()
        db.refresh(world)
        return world.id
    finally:
        db.close()


class TestV201SidebarTopLevelGroups:
    """验证左侧导航包含 8 个一级分组。"""

    def test_sidebar_has_8_groups(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        html = resp.text
        expected = ['工作台', '小说工程', '世界设定', '创作资产',
                    'AI 推演', '质量检查', '数据与导出', '设置']
        for term in expected:
            assert term in html, f"导航应包含「{term}」"

    def test_novel_engineering_not_disabled(self, client):
        """小说工程一级分组不是灰色禁用态。"""
        resp = client.get("/")
        html = resp.text
        # Group toggle should NOT have 'disabled' class
        novel_matches = re.findall(
            r'data-nav="novel"[^>]*class="([^"]*)"', html
        )
        for cls in novel_matches:
            assert 'disabled' not in cls, f"小说工程不应有disabled类: {cls}"

    def test_world_settings_not_disabled(self, client):
        """世界设定一级分组不是灰色禁用态。"""
        resp = client.get("/")
        html = resp.text
        matches = re.findall(r'data-nav="worlds"[^>]*class="([^"]*)"', html)
        for cls in matches:
            assert 'disabled' not in cls, f"世界设定不应有disabled类: {cls}"

    def test_creative_assets_not_disabled(self, client):
        """创作资产一级分组不是灰色禁用态。"""
        resp = client.get("/")
        html = resp.text
        matches = re.findall(r'data-nav="assets"[^>]*class="([^"]*)"', html)
        for cls in matches:
            assert 'disabled' not in cls, f"创作资产不应有disabled类: {cls}"

    def test_ai_simulation_not_disabled(self, client):
        """AI 推演一级分组不是灰色禁用态。"""
        resp = client.get("/")
        html = resp.text
        matches = re.findall(r'data-nav="simulation"[^>]*class="([^"]*)"', html)
        for cls in matches:
            assert 'disabled' not in cls, f"AI推演不应有disabled类: {cls}"

    def test_quality_check_not_disabled(self, client):
        """质量检查一级分组不是灰色禁用态。"""
        resp = client.get("/")
        html = resp.text
        matches = re.findall(r'data-nav="checks"[^>]*class="([^"]*)"', html)
        for cls in matches:
            assert 'disabled' not in cls, f"质量检查不应有disabled类: {cls}"

    def test_data_export_not_disabled(self, client):
        """数据与导出一级分组不是灰色禁用态。"""
        resp = client.get("/")
        html = resp.text
        matches = re.findall(r'data-nav="data"[^>]*class="([^"]*)"', html)
        for cls in matches:
            assert 'disabled' not in cls, f"数据与导出不应有disabled类: {cls}"

    def test_settings_not_disabled(self, client):
        """设置一级分组不是灰色禁用态。"""
        resp = client.get("/")
        html = resp.text
        matches = re.findall(r'data-nav="settings"[^>]*class="([^"]*)"', html)
        for cls in matches:
            assert 'disabled' not in cls, f"设置不应有disabled类: {cls}"


class TestV201SidebarActiveState:
    """验证当前页面所属分组有 active 状态。"""

    def test_dashboard_active(self, client):
        resp = client.get("/")
        assert 'data-nav="dashboard"' in resp.text
        assert 'active' in resp.text

    def test_worlds_page_active(self, client):
        resp = client.get("/worlds")
        assert 'data-nav="worlds"' in resp.text


class TestV201SidebarWithWorld:
    """验证有当前世界时二级入口正确。"""

    def test_novel_sub_items_generated(self, client, test_world):
        resp = client.get(f"/worlds/{test_world}/novel")
        assert resp.status_code == 200
        html = resp.text
        for item in ['工程总览', '全书演化', '分卷大纲', '章节大纲', '正文草稿']:
            assert item in html, f"小说工程子项应包含「{item}」"

    def test_world_settings_sub_items_generated(self, client, test_world):
        resp = client.get(f"/worlds/{test_world}")
        assert resp.status_code == 200
        html = resp.text
        for item in ['角色', '势力', '地点', '规则']:
            assert item in html, f"世界设定子项应包含「{item}」"


class TestV201SidebarNoWorld:
    """验证无当前世界时不生成坏链接。"""

    def test_no_none_links(self, client):
        resp = client.get("/")
        assert "/None/" not in resp.text

    def test_no_double_slash_links(self, client):
        resp = client.get("/")
        assert 'href="/worlds//"' not in resp.text

    def test_coming_soon_items_no_404(self, client):
        """未实现功能不生成404链接。"""
        resp = client.get("/")
        html = resp.text
        # coming-soon items should be spans, not links
        coming_soon_links = re.findall(
            r'coming-soon[^>]*href=', html
        )
        assert len(coming_soon_links) == 0, (
            f"coming-soon 项不应有 href: {coming_soon_links}"
        )

    def test_world_guidance_shown(self, client):
        """无当前世界时显示选择世界提示。"""
        resp = client.get("/")
        html = resp.text
        assert '选择世界' in html or '请先选择' in html or '请先创建' in html, (
            "无世界时应显示引导信息"
        )


class TestV201SidebarAria:
    """验证 ARIA 可访问性属性。"""

    def test_aria_expanded_exists(self, client):
        resp = client.get("/")
        assert 'aria-expanded' in resp.text

    def test_aria_controls_exists(self, client):
        resp = client.get("/")
        assert 'aria-controls' in resp.text

    def test_aria_disabled_exists(self, client):
        resp = client.get("/")
        assert 'aria-disabled' in resp.text


class TestV201SidebarOldRoutes:
    """验证旧路由仍可访问。"""

    def test_checks_route(self, client, test_world):
        resp = client.get(f"/worlds/{test_world}/checks")
        assert resp.status_code == 200

    def test_settings_route(self, client):
        resp = client.get("/settings/ai")
        assert resp.status_code == 200

    def test_data_route(self, client):
        resp = client.get("/data")
        assert resp.status_code == 200
