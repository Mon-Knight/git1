"""
AI World Engine - Test Sidebar Semantics
Tests for v1.7.8.2 sidebar semantic fixes.
"""

import re


def _create_world(client) -> int:
    client.post("/worlds", data={"name":"Test","world_type":"Fantasy"}, follow_redirects=False)
    list_resp = client.get("/worlds")
    match = re.search(r'/worlds/(\d+)', list_resp.text)
    if match: return int(match.group(1))
    raise RuntimeError("No world found")


class TestSidebarSemantics:
    def test_home_200(self, client):
        assert client.get("/").status_code == 200

    def test_home_has_world_group(self, client):
        resp = client.get("/")
        assert "世界项目" in resp.text

    def test_home_no_current_world_console(self, client):
        resp = client.get("/")
        assert "当前世界控制台" not in resp.text

    def test_home_no_setting_library_sidebar(self, client):
        resp = client.get("/")
        assert "设定库</a>" not in resp.text.replace(" ","")

    def test_home_no_story_history_sidebar(self, client):
        resp = client.get("/")
        assert "剧情历史</a>" not in resp.text.replace(" ","")

    def test_home_no_none_links(self, client):
        resp = client.get("/")
        assert "/None/" not in resp.text

    def test_world_detail_shows_current_world_label(self, client):
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}")
        assert "当前世界" in resp.text
        assert "Test" in resp.text

    def test_world_detail_has_console_link(self, client):
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}")
        assert "世界控制台" in resp.text

    def test_world_detail_has_simulation_link(self, client):
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}")
        assert f"/worlds/{w_id}/simulation" in resp.text

    def test_world_detail_has_context_link(self, client):
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}")
        assert f"/worlds/{w_id}/context" in resp.text

    def test_world_detail_has_novel_link(self, client):
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}")
        assert f"/worlds/{w_id}/novel/evolution" in resp.text

    def test_world_detail_has_checks_link(self, client):
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}")
        assert f"/worlds/{w_id}/checks" in resp.text

    def test_data_page_highlighted(self, client):
        resp = client.get("/data")
        assert resp.status_code == 200
        assert 'data-nav="data"' in resp.text

    def test_settings_page_highlighted(self, client):
        resp = client.get("/settings/ai")
        assert resp.status_code == 200
        assert 'data-nav="settings"' in resp.text
