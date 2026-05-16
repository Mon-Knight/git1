"""
AI World Engine - v2.4.2 Global Route Health Check
Ensures all major entry points return 200 (not 500).
"""

import re


def _create_world(client) -> int:
    client.post("/worlds", data={"name": "HealthWorld", "world_type": "Fantasy"}, follow_redirects=False)
    list_resp = client.get("/worlds")
    match = re.search(r'/worlds/(\d+)', list_resp.text)
    if match:
        return int(match.group(1))
    raise RuntimeError("No world")


class TestGlobalRouteHealth:
    """All major routes must return 200 or safe redirect."""

    def test_home_200(self, client):
        r = client.get("/")
        assert r.status_code == 200

    def test_worlds_list_200(self, client):
        r = client.get("/worlds")
        assert r.status_code == 200

    def test_world_detail_200(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}")
        assert r.status_code == 200

    def test_context_200(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}/context")
        assert r.status_code == 200

    def test_context_styles_200(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}/context/styles")
        assert r.status_code == 200

    def test_context_anchors_200(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}/context/anchors")
        assert r.status_code == 200

    def test_context_packages_200(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}/context/packages")
        assert r.status_code == 200

    def test_setting_suggestions_200(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}/setting-suggestions")
        assert r.status_code == 200

    def test_setting_suggestions_new_200(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}/setting-suggestions/new")
        assert r.status_code == 200

    def test_simulation_200(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}/simulation")
        assert r.status_code == 200

    def test_checks_200(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}/checks")
        assert r.status_code == 200

    def test_novel_drafts_200(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}/novel/drafts")
        assert r.status_code == 200

    def test_novel_quality_reports_200(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}/novel/quality-reports")
        assert r.status_code == 200

    def test_novel_revisions_200(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}/novel/revisions")
        assert r.status_code == 200

    def test_novel_final_drafts_200(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}/novel/final-drafts")
        assert r.status_code == 200

    def test_settings_ai_200(self, client):
        r = client.get("/settings/ai")
        assert r.status_code == 200

    def test_data_200(self, client):
        r = client.get("/data")
        assert r.status_code == 200

    def test_no_500_on_main_routes(self, client):
        """No major route should return 500."""
        w_id = _create_world(client)
        urls = [
            "/",
            "/worlds",
            f"/worlds/{w_id}",
            f"/worlds/{w_id}/context",
            f"/worlds/{w_id}/context/styles",
            f"/worlds/{w_id}/context/anchors",
            f"/worlds/{w_id}/context/packages",
            f"/worlds/{w_id}/setting-suggestions",
            f"/worlds/{w_id}/setting-suggestions/new",
            f"/worlds/{w_id}/simulation",
            f"/worlds/{w_id}/checks",
            f"/worlds/{w_id}/novel/drafts",
            f"/worlds/{w_id}/novel/quality-reports",
            f"/worlds/{w_id}/novel/revisions",
            f"/worlds/{w_id}/novel/final-drafts",
            "/settings/ai",
            "/data",
        ]
        for url in urls:
            r = client.get(url)
            assert r.status_code != 500, f"{url} returned 500"
