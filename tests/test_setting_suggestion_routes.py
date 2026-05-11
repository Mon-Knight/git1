"""
AI World Engine - Test Setting Suggestion Routes
Tests for setting_suggestions routes.
"""

import re


def _create_world(client) -> int:
    client.post("/worlds", data={"name":"TW","world_type":"Fantasy"}, follow_redirects=False)
    list_resp = client.get("/worlds")
    match = re.search(r'/worlds/(\d+)', list_resp.text)
    if match: return int(match.group(1))
    raise RuntimeError("No world")


class TestListPage:
    def test_list_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/setting-suggestions").status_code == 200

    def test_list_has_title(self, client):
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}/setting-suggestions")
        assert "设定库 AI 推演" in resp.text

    def test_list_has_app_shell(self, client):
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}/setting-suggestions")
        assert "app-main-inner" in resp.text or "app-shell-body" in resp.text

    def test_world_404(self, client):
        assert client.get("/worlds/99999/setting-suggestions").status_code == 404


class TestNewPage:
    def test_new_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/setting-suggestions/new").status_code == 200

    def test_new_has_form_fields(self, client):
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}/setting-suggestions/new")
        assert "suggestion_type" in resp.text
        assert "world_type" in resp.text
        assert "reference_style" in resp.text
        assert "generation_count" in resp.text


class TestCreateSuggestion:
    def test_post_creates_and_redirects(self, client):
        w_id = _create_world(client)
        resp = client.post(
            f"/worlds/{w_id}/setting-suggestions",
            data={"suggestion_type": "character", "world_type": "western_fantasy",
                  "reference_style": "heroic_epic", "generation_count": 3, "user_requirement": ""},
            follow_redirects=False,
        )
        assert resp.status_code == 303

    def test_post_redirects_to_detail(self, client):
        w_id = _create_world(client)
        resp = client.post(
            f"/worlds/{w_id}/setting-suggestions",
            data={"suggestion_type": "character", "world_type": "western_fantasy",
                  "reference_style": "heroic_epic", "generation_count": 3, "user_requirement": ""},
            follow_redirects=True,
        )
        assert resp.status_code == 200
        assert "候选详情" in resp.text or "候选" in resp.text


class TestDetailPage:
    def test_detail_200(self, client):
        w_id = _create_world(client)
        resp = client.post(f"/worlds/{w_id}/setting-suggestions",
            data={"suggestion_type":"character","world_type":"western_fantasy","reference_style":"heroic_epic","generation_count":2,"user_requirement":""},
            follow_redirects=True)
        assert resp.status_code == 200

    def test_detail_shows_v1_7_10_hint(self, client):
        w_id = _create_world(client)
        resp = client.post(f"/worlds/{w_id}/setting-suggestions",
            data={"suggestion_type":"character","world_type":"western_fantasy","reference_style":"heroic_epic","generation_count":2,"user_requirement":""},
            follow_redirects=True)
        assert "v1.8.0" in resp.text

    def test_detail_has_app_shell(self, client):
        w_id = _create_world(client)
        resp = client.post(f"/worlds/{w_id}/setting-suggestions",
            data={"suggestion_type":"character","world_type":"western_fantasy","reference_style":"heroic_epic","generation_count":2,"user_requirement":""},
            follow_redirects=True)
        assert "app-main-inner" in resp.text or "app-shell-body" in resp.text

    def test_nonexistent_suggestion_404(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/setting-suggestions/99999").status_code == 404
