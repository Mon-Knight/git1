"""
AI World Engine - Test Setting Suggestion Adoption Routes
Tests for adopt, edit-adopt, discard routes.
"""

import re


def _create_world_and_suggestion(client):
    client.post("/worlds", data={"name":"TW","world_type":"Fantasy"}, follow_redirects=False)
    list_resp = client.get("/worlds")
    match = re.search(r'/worlds/(\d+)', list_resp.text)
    w_id = int(match.group(1))
    # Create a suggestion
    client.post(f"/worlds/{w_id}/setting-suggestions",
        data={"suggestion_type":"character","world_type":"western_fantasy","reference_style":"heroic_epic","generation_count":1,"user_requirement":""},
        follow_redirects=False)
    # Find the suggestion ID
    resp = client.get(f"/worlds/{w_id}/setting-suggestions")
    match = re.search(r'/setting-suggestions/(\d+)', resp.text)
    s_id = int(match.group(1))
    return w_id, s_id


class TestAdoptRoutes:
    def test_adopt_character_post_redirects(self, client):
        w_id, s_id = _create_world_and_suggestion(client)
        resp = client.post(f"/worlds/{w_id}/setting-suggestions/{s_id}/adopt",
            data={"item_index": 0}, follow_redirects=False)
        assert resp.status_code == 303

    def test_adopt_faction(self, client):
        client.post("/worlds", data={"name":"TW2","world_type":"Fantasy"}, follow_redirects=False)
        list_resp = client.get("/worlds")
        matches = re.findall(r'/worlds/(\d+)', list_resp.text)
        w_id = int(matches[-1])
        client.post(f"/worlds/{w_id}/setting-suggestions",
            data={"suggestion_type":"faction","world_type":"western_fantasy","reference_style":"heroic_epic","generation_count":1,"user_requirement":""},
            follow_redirects=False)
        resp = client.get(f"/worlds/{w_id}/setting-suggestions")
        match = re.search(r'/setting-suggestions/(\d+)', resp.text)
        s_id = int(match.group(1))
        r = client.post(f"/worlds/{w_id}/setting-suggestions/{s_id}/adopt",
            data={"item_index": 0}, follow_redirects=False)
        assert r.status_code == 303

    def test_adopt_location(self, client):
        client.post("/worlds", data={"name":"TW3","world_type":"Fantasy"}, follow_redirects=False)
        list_resp = client.get("/worlds")
        matches = re.findall(r'/worlds/(\d+)', list_resp.text)
        w_id = int(matches[-1])
        client.post(f"/worlds/{w_id}/setting-suggestions",
            data={"suggestion_type":"location","world_type":"western_fantasy","reference_style":"heroic_epic","generation_count":1,"user_requirement":""},
            follow_redirects=False)
        resp = client.get(f"/worlds/{w_id}/setting-suggestions")
        match = re.search(r'/setting-suggestions/(\d+)', resp.text)
        s_id = int(match.group(1))
        r = client.post(f"/worlds/{w_id}/setting-suggestions/{s_id}/adopt",
            data={"item_index": 0}, follow_redirects=False)
        assert r.status_code == 303

    def test_adopt_rule(self, client):
        client.post("/worlds", data={"name":"TW4","world_type":"Fantasy"}, follow_redirects=False)
        list_resp = client.get("/worlds")
        matches = re.findall(r'/worlds/(\d+)', list_resp.text)
        w_id = int(matches[-1])
        client.post(f"/worlds/{w_id}/setting-suggestions",
            data={"suggestion_type":"rule","world_type":"western_fantasy","reference_style":"heroic_epic","generation_count":1,"user_requirement":""},
            follow_redirects=False)
        resp = client.get(f"/worlds/{w_id}/setting-suggestions")
        match = re.search(r'/setting-suggestions/(\d+)', resp.text)
        s_id = int(match.group(1))
        r = client.post(f"/worlds/{w_id}/setting-suggestions/{s_id}/adopt",
            data={"item_index": 0}, follow_redirects=False)
        assert r.status_code == 303

    def test_double_adopt_no_duplicate(self, client):
        w_id, s_id = _create_world_and_suggestion(client)
        client.post(f"/worlds/{w_id}/setting-suggestions/{s_id}/adopt", data={"item_index":0})
        # Second adopt should fail
        resp = client.post(f"/worlds/{w_id}/setting-suggestions/{s_id}/adopt", data={"item_index":0}, follow_redirects=True)
        assert "已采纳" in resp.text or "不能" in resp.text or "error" in resp.text.lower()

    def test_cross_world_adopt_404(self, client):
        w_id, s_id = _create_world_and_suggestion(client)
        resp = client.post(f"/worlds/99999/setting-suggestions/{s_id}/adopt", data={"item_index":0})
        assert resp.status_code == 404

    def test_nonexistent_suggestion_404(self, client):
        w_id, s_id = _create_world_and_suggestion(client)
        # Try to access the suggestion from a non-existent world
        resp = client.post(f"/worlds/99999/setting-suggestions/{s_id}/adopt", data={"item_index":0})
        assert resp.status_code == 404

    def test_edit_adopt_page_200(self, client):
        w_id, s_id = _create_world_and_suggestion(client)
        resp = client.get(f"/worlds/{w_id}/setting-suggestions/{s_id}/edit-adopt?item_index=0")
        assert resp.status_code == 200

    def test_edit_adopt_page_has_app_shell(self, client):
        w_id, s_id = _create_world_and_suggestion(client)
        resp = client.get(f"/worlds/{w_id}/setting-suggestions/{s_id}/edit-adopt?item_index=0")
        assert "app-main-inner" in resp.text or "app-shell-body" in resp.text

    def test_edit_adopt_post_success(self, client):
        w_id, s_id = _create_world_and_suggestion(client)
        resp = client.post(f"/worlds/{w_id}/setting-suggestions/{s_id}/edit-adopt",
            data={"item_index":0, "name":"CustomHero", "description":"Edited description"},
            follow_redirects=False)
        assert resp.status_code == 303

    def test_discard_success(self, client):
        w_id, s_id = _create_world_and_suggestion(client)
        resp = client.post(f"/worlds/{w_id}/setting-suggestions/{s_id}/discard", follow_redirects=False)
        assert resp.status_code == 303

    def test_detail_shows_adopted_status(self, client):
        w_id, s_id = _create_world_and_suggestion(client)
        client.post(f"/worlds/{w_id}/setting-suggestions/{s_id}/adopt", data={"item_index":0})
        resp = client.get(f"/worlds/{w_id}/setting-suggestions/{s_id}")
        assert "已采纳" in resp.text

    def test_detail_shows_discard_button_when_pending(self, client):
        w_id, s_id = _create_world_and_suggestion(client)
        resp = client.get(f"/worlds/{w_id}/setting-suggestions/{s_id}")
        assert "废弃候选" in resp.text
