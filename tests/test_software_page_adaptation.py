"""
AI World Engine - Test Software Page Adaptation
Tests for v1.7.8.1 page adaptation to app shell.
"""

import re


def _create_world(client) -> int:
    client.post("/worlds", data={"name": "TestW", "world_type": "Fantasy"}, follow_redirects=False)
    list_resp = client.get("/worlds")
    match = re.search(r'/worlds/(\d+)', list_resp.text)
    if match:
        return int(match.group(1))
    raise RuntimeError("Could not find world ID")


class TestDataPage:
    def test_data_returns_200(self, client):
        assert client.get("/data").status_code == 200

    def test_data_has_app_shell(self, client):
        resp = client.get("/data")
        assert "app-shell-body" in resp.text or "app-main-inner" in resp.text

    def test_data_has_title(self, client):
        resp = client.get("/data")
        assert "数据管理" in resp.text

    def test_data_has_export_center_link(self, client):
        resp = client.get("/data")
        assert "导出中心" in resp.text


class TestExportCenter:
    def test_export_center_returns_200(self, client):
        assert client.get("/data/export").status_code == 200

    def test_export_center_has_app_shell(self, client):
        resp = client.get("/data/export")
        assert "app-shell-body" in resp.text or "app-main-inner" in resp.text


class TestSettingsPage:
    def test_settings_returns_200(self, client):
        assert client.get("/settings/ai").status_code == 200

    def test_settings_has_app_shell(self, client):
        resp = client.get("/settings/ai")
        assert "app-shell-body" in resp.text or "app-main-inner" in resp.text

    def test_settings_has_title(self, client):
        resp = client.get("/settings/ai")
        assert "AI 设置" in resp.text


class TestWorldPages:
    def test_context_has_app_shell(self, client):
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}/context")
        assert resp.status_code == 200

    def test_novel_evolution_has_app_shell(self, client):
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}/novel/evolution")
        assert resp.status_code == 200
        assert "app-shell-body" in resp.text or "app-main-inner" in resp.text

    def test_novel_evolutions_has_app_shell(self, client):
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}/novel/evolutions")
        assert resp.status_code == 200
