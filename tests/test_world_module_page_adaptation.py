"""
AI World Engine - Test World Module Page Adaptation
Tests for v1.7.8.2 page adaptation to app shell.
"""

import re


def _create_world(client) -> int:
    client.post("/worlds", data={"name":"TW","world_type":"Fantasy"}, follow_redirects=False)
    list_resp = client.get("/worlds")
    match = re.search(r'/worlds/(\d+)', list_resp.text)
    if match: return int(match.group(1))
    raise RuntimeError("No world")


class TestSimulationPage:
    def test_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/simulation").status_code == 200

    def test_has_app_shell(self, client):
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}/simulation")
        assert "app-shell-body" in resp.text or "app-main-inner" in resp.text

    def test_not_standalone_layout(self, client):
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}/simulation")
        assert '<div class="container">' not in resp.text  # old standalone wrapper


class TestRecordsPage:
    def test_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/records").status_code == 200

    def test_has_app_shell(self, client):
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}/records")
        assert "app-shell-body" in resp.text or "app-main-inner" in resp.text


class TestBranchesPage:
    def test_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/branches").status_code == 200

    def test_has_app_shell(self, client):
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}/branches")
        assert "app-shell-body" in resp.text or "app-main-inner" in resp.text


class TestContextPage:
    def test_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/context").status_code == 200

    def test_has_app_shell(self, client):
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}/context")
        assert "app-shell-body" in resp.text or "app-main-inner" in resp.text

    def test_styles_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/context/styles").status_code == 200

    def test_anchors_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/context/anchors").status_code == 200

    def test_packages_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/context/packages").status_code == 200


class TestChecksPage:
    def test_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/checks").status_code == 200

    def test_has_app_shell(self, client):
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}/checks")
        assert "app-shell-body" in resp.text or "app-main-inner" in resp.text

    def test_conflicts_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/checks/conflicts").status_code == 200

    def test_behavior_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/checks/behavior").status_code == 200
