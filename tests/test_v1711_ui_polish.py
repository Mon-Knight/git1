"""
AI World Engine - Test v1.7.11 UI Polish
Tests for sidebar recent world, homepage layout, and 2K CSS.
"""

import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read(path: str) -> str:
    with open(os.path.join(PROJECT_ROOT, path), "r", encoding="utf-8") as f:
        return f.read()


class TestSidebarRecentWorld:
    def test_base_has_recent_world(self):
        content = _read("app/templates/base.html")
        assert "recent_world_id" in content

    def test_base_has_new_world_link(self):
        content = _read("app/templates/base.html")
        assert "新建世界" in content

    def test_homepage_passes_recent_world_id(self):
        content = _read("app/routes/pages.py")
        assert "recent_world_id" in content

    def test_home_200(self, client):
        assert client.get("/").status_code == 200

    def test_worlds_list_200(self, client):
        assert client.get("/worlds").status_code == 200

    def test_sidebar_has_world_group(self, client):
        resp = client.get("/")
        assert "世界项目" in resp.text

    def test_home_no_none_links(self, client):
        resp = client.get("/")
        assert "/None/" not in resp.text


class TestDashboard2K:
    def test_dashboard_css_has_2k_rules(self):
        content = _read("app/static/css/dashboard.css")
        assert "min-width: 1920px" in content

    def test_app_shell_css_has_2k_rules(self):
        content = _read("app/static/css/app-shell.css")
        assert "min-width: 1920px" in content

    def test_dashboard_max_width(self):
        content = _read("app/static/css/dashboard.css")
        assert "max-width: 1440px" in content

    def test_overview_grid_responsive(self):
        content = _read("app/static/css/dashboard.css")
        assert "auto-fill" in content


class TestSettingsCenter:
    def test_settings_200(self, client):
        assert client.get("/settings/ai").status_code == 200

    def test_settings_has_center_title(self, client):
        resp = client.get("/settings/ai")
        assert "设置中心" in resp.text

    def test_settings_has_ai_section(self, client):
        resp = client.get("/settings/ai")
        assert "AI 模型设置" in resp.text

    def test_settings_has_desktop_section(self, client):
        resp = client.get("/settings/ai")
        assert "桌面窗口" in resp.text


class TestExistingFeatures:
    def test_export_center_200(self, client):
        assert client.get("/data/export").status_code == 200

    def test_data_200(self, client):
        assert client.get("/data").status_code == 200

    def test_version_in_homepage(self, client):
        resp = client.get("/")
        assert "v1.7.11.2" in resp.text
