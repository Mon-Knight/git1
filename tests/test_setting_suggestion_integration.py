"""
AI World Engine - Test Setting Suggestion Integration
Integration tests for setting suggestions with world console, sidebar, and existing features.
"""

import re


def _create_world(client) -> int:
    client.post("/worlds", data={"name":"IW","world_type":"Fantasy"}, follow_redirects=False)
    list_resp = client.get("/worlds")
    match = re.search(r'/worlds/(\d+)', list_resp.text)
    if match: return int(match.group(1))
    raise RuntimeError("No world")


class TestWorldConsole:
    def test_world_console_has_setting_suggestion_entry(self, client):
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}")
        assert "设定库 AI 推演" in resp.text

    def test_home_no_setting_suggestion_link(self, client):
        resp = client.get("/")
        assert "/None/setting-suggestions" not in resp.text


class TestExistingFeaturesUnaffected:
    def test_export_center_200(self, client):
        assert client.get("/data/export").status_code == 200

    def test_data_200(self, client):
        assert client.get("/data").status_code == 200

    def test_settings_200(self, client):
        assert client.get("/settings/ai").status_code == 200

    def test_simulation_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/simulation").status_code == 200

    def test_context_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/context").status_code == 200

    def test_checks_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/checks").status_code == 200
