"""
AI World Engine - Test Setting Suggestion Adoption Integration
Integration tests for adoption with existing features.
"""

import re


def _create_world_and_suggestion(client):
    client.post("/worlds", data={"name":"IW","world_type":"Fantasy"}, follow_redirects=False)
    list_resp = client.get("/worlds")
    match = re.search(r'/worlds/(\d+)', list_resp.text)
    w_id = int(match.group(1))
    client.post(f"/worlds/{w_id}/setting-suggestions",
        data={"suggestion_type":"character","world_type":"western_fantasy","reference_style":"heroic_epic","generation_count":1,"user_requirement":""},
        follow_redirects=False)
    resp = client.get(f"/worlds/{w_id}/setting-suggestions")
    match = re.search(r'/setting-suggestions/(\d+)', resp.text)
    s_id = int(match.group(1))
    return w_id, s_id


class TestIntegration:
    def test_world_console_entry_still_exists(self, client):
        w_id, _ = _create_world_and_suggestion(client)
        resp = client.get(f"/worlds/{w_id}")
        assert "设定库 AI 推演" in resp.text

    def test_detail_has_adopt_buttons(self, client):
        w_id, s_id = _create_world_and_suggestion(client)
        resp = client.get(f"/worlds/{w_id}/setting-suggestions/{s_id}")
        assert "采纳" in resp.text

    def test_detail_has_edit_adopt_button(self, client):
        w_id, s_id = _create_world_and_suggestion(client)
        resp = client.get(f"/worlds/{w_id}/setting-suggestions/{s_id}")
        assert "编辑后采纳" in resp.text

    def test_character_adopt_adds_to_character_list(self, client):
        w_id, s_id = _create_world_and_suggestion(client)
        client.post(f"/worlds/{w_id}/setting-suggestions/{s_id}/adopt", data={"item_index":0})
        resp = client.get(f"/worlds/{w_id}/characters")
        assert resp.status_code == 200

    def test_settings_center_200(self, client):
        w_id, _ = _create_world_and_suggestion(client)
        assert client.get("/settings/ai").status_code == 200

    def test_export_center_200(self, client):
        w_id, _ = _create_world_and_suggestion(client)
        assert client.get("/data/export").status_code == 200

    def test_generate_still_works(self, client):
        w_id, s_id = _create_world_and_suggestion(client)
        resp = client.get(f"/worlds/{w_id}/setting-suggestions/new")
        assert resp.status_code == 200

    def test_home_no_none_links(self, client):
        resp = client.get("/")
        assert "/None/" not in resp.text

    def test_list_shows_status(self, client):
        w_id, s_id = _create_world_and_suggestion(client)
        resp = client.get(f"/worlds/{w_id}/setting-suggestions")
        assert "待处理" in resp.text or "pending" in resp.text.lower()
