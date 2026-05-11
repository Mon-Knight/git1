"""
AI World Engine - Test Export Routes
Tests for export center and desktop save routes.
"""

import re


def _create_world(client) -> int:
    client.post(
        "/worlds",
        data={"name": "TestWorld", "world_type": "Fantasy"},
        follow_redirects=False,
    )
    list_resp = client.get("/worlds")
    match = re.search(r'/worlds/(\d+)', list_resp.text)
    if match:
        return int(match.group(1))
    raise RuntimeError("Could not find world ID")


class TestExportCenterPage:
    def test_export_center_returns_200(self, client):
        resp = client.get("/data/export")
        assert resp.status_code == 200

    def test_export_center_contains_title(self, client):
        resp = client.get("/data/export")
        assert "导出中心" in resp.text

    def test_export_center_has_world_export(self, client):
        resp = client.get("/data/export")
        assert "导出当前世界" in resp.text

    def test_export_center_has_backup(self, client):
        resp = client.get("/data/export")
        assert "全量备份" in resp.text


class TestOldExportRoutes:
    def test_old_world_export_json_200(self, client):
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}/export.json")
        assert resp.status_code == 200

    def test_old_world_export_no_api_key(self, client):
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}/export.json")
        text = resp.text
        assert "api_key" not in text.lower()

    def test_nonexistent_world_returns_404(self, client):
        resp = client.get("/worlds/99999/export.json")
        assert resp.status_code == 404


class TestDesktopSaveRoutes:
    def test_save_world_no_desktop_mode_returns_403(self, client):
        w_id = _create_world(client)
        resp = client.post(
            f"/worlds/{w_id}/export.json",
            data={"save_path": "C:/test.json"},
        )
        assert resp.status_code == 403

    def test_save_backup_no_desktop_mode_returns_403(self, client):
        resp = client.post(
            "/data/export/backup",
            data={"save_path": "C:/test.json"},
        )
        assert resp.status_code == 403
