"""
AI World Engine - v2.4.2 Model Field Compatibility Regression Tests
Ensures old modules don't break when models lack certain fields.
"""

import re


def _create_world(client) -> int:
    client.post("/worlds", data={"name": "CompatWorld", "world_type": "Fantasy"}, follow_redirects=False)
    list_resp = client.get("/worlds")
    match = re.search(r'/worlds/(\d+)', list_resp.text)
    if match:
        return int(match.group(1))
    raise RuntimeError("No world")


class TestCharacterIdentityCompat:
    """Setting Suggestions must not crash when Character has no 'identity' field."""

    def test_list_200_no_identity_error(self, client):
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}/setting-suggestions")
        assert resp.status_code == 200
        assert "object has no attribute 'identity'" not in resp.text
        assert "object has no attribute" not in resp.text

    def test_new_200_no_identity_error(self, client):
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}/setting-suggestions/new")
        assert resp.status_code == 200
        assert "object has no attribute 'identity'" not in resp.text
        assert "object has no attribute" not in resp.text

    def test_prompt_build_does_not_access_identity(self, client):
        """Verify build_setting_suggestion_prompt runs without identity error."""
        from app.database import SessionLocal
        from app.services.setting_suggestion_service import SettingSuggestionService

        w_id = _create_world(client)
        db = SessionLocal()
        try:
            # Should not raise AttributeError
            prompt = SettingSuggestionService.build_setting_suggestion_prompt(
                db, w_id, {"suggestion_type": "character", "world_type": "western_fantasy",
                           "reference_style": "heroic_epic", "generation_count": 2, "user_requirement": ""}
            )
            assert prompt
            assert "暂无角色" in prompt or "name" in prompt.lower()
        finally:
            db.close()

    def test_mock_generate_succeeds(self, client):
        w_id = _create_world(client)
        resp = client.post(
            f"/worlds/{w_id}/setting-suggestions",
            data={"suggestion_type": "character", "world_type": "western_fantasy",
                  "reference_style": "heroic_epic", "generation_count": 2, "user_requirement": ""},
            follow_redirects=False,
        )
        assert resp.status_code == 303

    def test_prompt_contains_character_name(self, client):
        from app.database import SessionLocal
        from app.services.setting_suggestion_service import SettingSuggestionService

        w_id = _create_world(client)
        db = SessionLocal()
        try:
            prompt = SettingSuggestionService.build_setting_suggestion_prompt(
                db, w_id, {"suggestion_type": "character", "world_type": "western_fantasy",
                           "reference_style": "heroic_epic", "generation_count": 2, "user_requirement": ""}
            )
            # Prompt should still reference character fields
            assert "name" in prompt.lower() or "角色" in prompt
        finally:
            db.close()

    def test_no_empty_field_500(self, client):
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}/setting-suggestions/new")
        assert resp.status_code == 200
        assert "Internal Server Error" not in resp.text

    def test_no_worlds_none(self, client):
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}/setting-suggestions")
        assert "/worlds/None" not in resp.text

    def test_no_worlds_slash(self, client):
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}/setting-suggestions")
        assert "/worlds//" not in resp.text


class TestContextAssetsCompat:
    """Creative Assets pages must not 500."""

    def test_context_index_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/context").status_code == 200

    def test_context_styles_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/context/styles").status_code == 200

    def test_context_anchors_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/context/anchors").status_code == 200

    def test_context_packages_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/context/packages").status_code == 200

    def test_context_packages_new_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/context/packages/new").status_code == 200

    def test_context_no_identity_error(self, client):
        w_id = _create_world(client)
        for url in [f"/worlds/{w_id}/context", f"/worlds/{w_id}/context/styles",
                     f"/worlds/{w_id}/context/anchors", f"/worlds/{w_id}/context/packages"]:
            resp = client.get(url)
            assert "object has no attribute 'identity'" not in resp.text
            assert "Internal Server Error" not in resp.text

    def test_context_no_worlds_none(self, client):
        w_id = _create_world(client)
        for url in [f"/worlds/{w_id}/context", f"/worlds/{w_id}/context/styles",
                     f"/worlds/{w_id}/context/anchors", f"/worlds/{w_id}/context/packages"]:
            resp = client.get(url)
            assert "/worlds/None" not in resp.text

    def test_context_no_worlds_slash(self, client):
        w_id = _create_world(client)
        for url in [f"/worlds/{w_id}/context", f"/worlds/{w_id}/context/styles",
                     f"/worlds/{w_id}/context/anchors", f"/worlds/{w_id}/context/packages"]:
            resp = client.get(url)
            assert "/worlds//" not in resp.text
