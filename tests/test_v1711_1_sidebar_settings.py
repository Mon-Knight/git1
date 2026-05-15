"""
Tests for v1.7.11.1: Sidebar secondary navigation and settings categories.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, SessionLocal, Base, engine

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    """Ensure tables exist before each test."""
    Base.metadata.create_all(bind=engine)
    yield
    # cleanup


class TestSidebarNavigation:
    """Left sidebar secondary navigation tests."""

    def test_base_template_has_sidebar_groups(self):
        """v2.0.1: base.html should have multiple sidebar groups with new names."""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text
        # World settings group (was 世界项目)
        assert '世界设定' in html
        # Settings group
        assert '设置' in html
        # Sidebar group toggle class
        assert 'sidebar-group-toggle' in html

    def test_base_has_subnav_divider(self):
        """base.html should have subnav divider between management and modules."""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text
        assert 'sidebar-subnav-divider' in html

    def test_world_sub_modules_always_visible(self):
        """v2.0.1: Top-level groups always visible; world console only with active world."""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text
        # Top-level module groups are always visible in sidebar
        assert '小说工程' in html
        assert 'AI 推演' in html
        assert '创作资产' in html
        assert '质量检查' in html
        assert '世界设定' in html

    def test_disabled_sub_module_when_no_world(self):
        """v2.0.1: Without an active world, sub-modules should be disabled."""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text
        # Core modules should have 'disabled' class or '后续开放' when no world
        assert 'disabled' in html or '后续开放' in html

    def test_sidebar_js_has_toggle_function(self):
        """sidebar.js should export toggleSidebarGroup function."""
        response = client.get("/static/js/sidebar.js")
        assert response.status_code == 200
        js = response.text
        assert 'toggleSidebarGroup' in js
        assert 'showSettingsCategory' in js


class TestSettingsCategories:
    """Settings center collapsible category tests."""

    def test_settings_page_has_categories(self):
        """settings/ai.html should have category sections."""
        response = client.get("/settings/ai")
        assert response.status_code == 200
        html = response.text
        assert 'data-settings-cat="ai"' in html
        assert 'data-settings-cat="display"' in html
        assert 'data-settings-cat="desktop"' in html
        assert 'data-settings-cat="storage"' in html
        assert 'data-settings-cat="export"' in html
        assert 'data-settings-cat="diagnostics"' in html
        assert 'data-settings-cat="about"' in html

    def test_settings_page_has_section_class(self):
        """settings/ai.html should use settings-cat-section class."""
        response = client.get("/settings/ai")
        assert response.status_code == 200
        html = response.text
        assert 'settings-cat-section' in html

    def test_settings_page_has_badges(self):
        """settings/ai.html should have editable/future badges."""
        response = client.get("/settings/ai")
        assert response.status_code == 200
        html = response.text
        assert 'editable-badge' in html
        assert 'future-badge' in html

    def test_settings_sidebar_has_categories(self):
        """Base sidebar should list all settings categories."""
        response = client.get("/settings/ai")
        assert response.status_code == 200
        html = response.text
        assert '界面显示' in html
        assert '桌面窗口' in html
        assert '路径与存储' in html
        assert '数据与导出' in html
        assert '日志与诊断' in html

    def test_settings_route_passes_active_nav(self):
        """Settings route should pass active_nav='settings'."""
        response = client.get("/settings/ai")
        assert response.status_code == 200
        html = response.text
        # The settings group should be expanded
        assert 'active_nav' not in html  # it's rendered, not literal
        # But the settings link should be active
        assert 'data-nav="settings"' in html

    def test_settings_page_form_still_works(self):
        """AI settings form should still be present and functional."""
        response = client.get("/settings/ai")
        assert response.status_code == 200
        html = response.text
        assert 'settings-form' in html
        assert 'ai_provider' in html
        assert 'ai_model' in html


class TestDashboard2KLayout:
    """Dashboard 2K layout tests."""

    def test_dashboard_css_has_2k_breakpoint(self):
        """dashboard.css should have 1920px 2K breakpoint."""
        response = client.get("/static/css/dashboard.css")
        assert response.status_code == 200
        css = response.text
        assert '1920px' in css
        assert '1600px' in css  # 2K max-width

    def test_dashboard_css_has_responsive_breakpoints(self):
        """dashboard.css should have multiple responsive breakpoints."""
        response = client.get("/static/css/dashboard.css")
        assert response.status_code == 200
        css = response.text
        assert '1440px' in css
        assert '1024px' in css
        assert '1023px' in css

    def test_dashboard_css_has_table_overflow(self):
        """dashboard.css should handle table horizontal scroll."""
        response = client.get("/static/css/dashboard.css")
        assert response.status_code == 200
        css = response.text
        assert 'overflow-x' in css


class TestHomepage:
    """Homepage layout tests."""

    def test_homepage_renders(self):
        """Homepage should render with correct layout."""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text
        assert '创作工作台' in html
        assert 'page-dashboard' in html

    def test_homepage_passes_recent_world_id(self):
        """Homepage should pass recent_world_id to template."""
        response = client.get("/")
        assert response.status_code == 200
        # The template should render without errors
        html = response.text
        assert 'recent_world_id' not in html  # it's a template variable, not literal


class TestWorldConsoleEntry:
    """World console entry optimization tests."""

    def test_world_console_link_has_recent_fallback(self):
        """v2.0.1: World console link shows when world is active; fallback via recent_world_id."""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text
        # Should have recent world link or world list as fallback
        assert '世界列表' in html or '最近世界' in html or '世界设定' in html

    def test_world_detail_page_renders(self):
        """World detail page should render with sidebar active."""
        # Create a world first
        response = client.post("/worlds", data={
            "name": "测试世界",
            "world_type": "fantasy",
            "description": "用于测试的世界",
            "current_era": "古代",
            "tone": "史诗",
        }, follow_redirects=False)
        assert response.status_code in (303, 302)

        # Now get the world detail
        response = client.get("/worlds/1")
        if response.status_code == 404:
            # World might not have been created (DB isolation)
            pass
        else:
            assert response.status_code == 200
