"""
AI World Engine - Test Sidebar Grouping
Tests for v1.7.8.1 sidebar group folding and expand/collapse.
"""

import re
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read_template(filename: str) -> str:
    path = os.path.join(PROJECT_ROOT, "app", "templates", filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _create_world(client) -> int:
    client.post("/worlds", data={"name": "TestW", "world_type": "Fantasy"}, follow_redirects=False)
    list_resp = client.get("/worlds")
    match = re.search(r'/worlds/(\d+)', list_resp.text)
    if match:
        return int(match.group(1))
    raise RuntimeError("Could not find world ID")


class TestSidebarGroupStructure:
    def test_base_has_sidebar_group(self):
        content = _read_template("base.html")
        assert "sidebar-group" in content
        assert "sidebar-subnav" in content

    def test_base_has_sidebar_arrow(self):
        content = _read_template("base.html")
        assert "sidebar-arrow" in content

    def test_base_has_toggle_function(self):
        content = _read_template("base.html")
        assert "toggleSidebarGroup" in content or "sidebar.js" in content

    def test_sidebar_js_exists(self):
        assert os.path.isfile(os.path.join(PROJECT_ROOT, "app", "static", "js", "sidebar.js"))


class TestSidebarGroupPages:
    def test_home_has_dashboard(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "工作台" in resp.text

    def test_home_has_world_group(self, client):
        resp = client.get("/")
        assert "世界项目" in resp.text
        assert "sidebar-group" in resp.text

    def test_worlds_list_worlds_highlighted(self, client):
        resp = client.get("/worlds")
        assert resp.status_code == 200
        assert 'data-nav="worlds"' in resp.text

    def test_world_detail_has_expanded_group(self, client):
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}")
        assert resp.status_code == 200
        assert "世界项目" in resp.text
        assert "sidebar-sublink" in resp.text

    def test_world_detail_no_none_links(self, client):
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}")
        assert "/None/" not in resp.text
        assert 'href="/worlds/"' not in resp.text  # double-slash in paths

    def test_world_detail_correct_links(self, client):
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}")
        assert f"/worlds/{w_id}/context" in resp.text
        assert f"/worlds/{w_id}/simulation" in resp.text
        assert f"/worlds/{w_id}/novel/evolution" in resp.text
        assert f"/worlds/{w_id}/checks" in resp.text

    def test_home_no_none_links(self, client):
        resp = client.get("/")
        assert "/None/" not in resp.text

    def test_home_disabled_items(self, client):
        # v1.7.8.2: future items still disabled in sidebar-future section
        resp = client.get("/")
        assert "sidebar-future" in resp.text

    def test_data_page_highlighted(self, client):
        resp = client.get("/data")
        assert resp.status_code == 200
        assert 'data-nav="data"' in resp.text

    def test_settings_page_highlighted(self, client):
        resp = client.get("/settings/ai")
        assert resp.status_code == 200
        assert 'data-nav="settings"' in resp.text
