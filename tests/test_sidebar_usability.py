"""
AI World Engine - Test Sidebar Usability
Tests for v1.7.7.1 sidebar active state, safe links, and visual states.
"""

import os
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read_template(filename: str) -> str:
    path = os.path.join(PROJECT_ROOT, "app", "templates", filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _read_static(filename: str) -> str:
    path = os.path.join(PROJECT_ROOT, "app", "static", "css", filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _create_world(client) -> int:
    client.post(
        "/worlds",
        data={"name": "测试世界", "world_type": "奇幻"},
        follow_redirects=False,
    )
    list_resp = client.get("/worlds")
    match = re.search(r'/worlds/(\d+)', list_resp.text)
    if match:
        return int(match.group(1))
    raise RuntimeError("Could not find world ID")


class TestSidebarStructure:
    """Tests that sidebar HTML structure is correct."""

    def test_sidebar_exists_in_base(self):
        content = _read_template("base.html")
        assert 'class="sidebar"' in content, "base.html missing sidebar"

    def test_sidebar_has_data_nav_attributes(self):
        content = _read_template("base.html")
        assert 'data-nav="dashboard"' in content, "Missing data-nav=dashboard"
        assert 'data-nav="worlds"' in content, "Missing data-nav=worlds"
        assert 'data-nav="novel"' in content, "Missing data-nav=novel"
        assert 'data-nav="assets"' in content, "Missing data-nav=assets"
        assert 'data-nav="simulation"' in content, "Missing data-nav=simulation"
        assert 'data-nav="checks"' in content, "Missing data-nav=checks"
        assert 'data-nav="data"' in content, "Missing data-nav=data"
        assert 'data-nav="settings"' in content, "Missing data-nav=settings"

    def test_sidebar_has_auto_detect_script(self):
        content = _read_template("base.html")
        assert "Auto-detect active sidebar" in content, "Missing auto-detect script"

    def test_sidebar_no_none_links(self):
        content = _read_template("base.html")
        assert "/None/" not in content, "base.html contains /None/ links"

    def test_sidebar_has_disabled_class(self):
        content = _read_template("base.html")
        assert "disabled" in content, "Missing disabled class on sidebar links"

    def test_sidebar_future_items_exist(self):
        content = _read_template("base.html")
        assert "后续版本开放" in content, "Missing future version label"
        assert "分卷大纲" in content, "Missing 分卷大纲 in future items"
        assert "章节大纲" in content, "Missing 章节大纲 in future items"
        assert "正文生成" in content, "Missing 正文生成 in future items"


class TestSidebarCSS:
    """Tests that sidebar CSS has required states."""

    def test_sidebar_active_style_exists(self):
        content = _read_static("app-shell.css")
        assert ".sidebar-link.active" in content, "Missing .sidebar-link.active"

    def test_sidebar_hover_style_exists(self):
        content = _read_static("app-shell.css")
        assert ".sidebar-link:hover" in content, "Missing .sidebar-link:hover"

    def test_sidebar_disabled_style_exists(self):
        content = _read_static("app-shell.css")
        assert ".sidebar-link.disabled" in content, "Missing .sidebar-link.disabled"

    def test_sidebar_width_is_240px(self):
        content = _read_static("app-shell.css")
        assert "width: 240px" in content, "Sidebar width not 240px"

    def test_small_window_sidebar_hidden(self):
        content = _read_static("app-shell.css")
        assert "translateX(-240px)" in content, "Missing sidebar hide transform"


class TestSidebarOnBasePages:
    """Tests sidebar on pages that extend base.html."""

    def test_home_has_sidebar(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert 'data-nav="dashboard"' in resp.text

    def test_worlds_list_has_sidebar(self, client):
        resp = client.get("/worlds")
        assert resp.status_code == 200
        assert 'data-nav="worlds"' in resp.text

    def test_world_detail_has_sidebar(self, client):
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}")
        assert resp.status_code == 200
        assert 'data-nav="worlds"' in resp.text

    def test_novel_evolution_has_sidebar(self, client):
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}/novel/evolution")
        assert resp.status_code == 200
        assert 'data-nav="novel"' in resp.text

    def test_home_no_none_links(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "/None/" not in resp.text

    def test_home_has_disabled_links(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "disabled" in resp.text


class TestStandalonePagesAccessible:
    """Standalone pages (not extending base.html) should still return 200."""

    def test_simulation_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/simulation").status_code == 200

    def test_context_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/context").status_code == 200

    def test_checks_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/checks").status_code == 200

    def test_data_200(self, client):
        assert client.get("/data").status_code == 200

    def test_settings_200(self, client):
        assert client.get("/settings/ai").status_code == 200
