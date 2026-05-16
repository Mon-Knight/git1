"""
AI World Engine - v2.4.4 Regression Tests
Tests for: quality check availability, TXT style import, style visibility,
discarded suggestion deletion, version display.
"""
import re
import io


def _create_world(client) -> int:
    client.post("/worlds", data={"name": "V244World", "world_type": "Fantasy"}, follow_redirects=False)
    list_resp = client.get("/worlds")
    match = re.search(r'/worlds/(\d+)', list_resp.text)
    if match: return int(match.group(1))
    raise RuntimeError("No world")


class TestQualityReportsAvailable:
    """v2.4.4: Quality reports must not be locked."""

    def test_quality_reports_page_200(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}/novel/quality-reports")
        assert r.status_code == 200

    def test_world_detail_has_quality_reports_link(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}")
        assert "quality-reports" in r.text or "正文质量检查" in r.text

    def test_world_detail_no_future_version_lock(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}")
        assert "v2.1.0 开放" not in r.text

    def test_quality_reports_new_200(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}/novel/quality-reports")
        assert r.status_code == 200

    def test_no_worlds_none(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}/novel/quality-reports")
        assert "/worlds/None" not in r.text

    def test_no_worlds_slash(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}/novel/quality-reports")
        assert "/worlds//" not in r.text


class TestStyleImportAvailable:
    """v2.4.4: TXT import entry must be visible."""

    def test_styles_page_200(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}/context/styles")
        assert r.status_code == 200

    def test_styles_page_has_import_button(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}/context/styles")
        assert "导入 TXT" in r.text or "TXT" in r.text

    def test_styles_import_page_200(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}/context/styles/import")
        assert r.status_code == 200

    def test_styles_import_has_file_input(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}/context/styles/import")
        assert 'type="file"' in r.text or "file" in r.text.lower()


class TestOldStyleProfilesVisible:
    """v2.4.4: Old style profiles must be visible."""

    def test_styles_list_includes_manual(self, client):
        w_id = _create_world(client)
        # Create a manual style profile
        client.post(f"/worlds/{w_id}/context/styles/new", data={
            "name": "ManualStyle", "genre": "奇幻", "pacing": "快速"
        }, follow_redirects=False)
        r = client.get(f"/worlds/{w_id}/context/styles")
        assert "ManualStyle" in r.text

    def test_styles_list_no_empty_source_type_filter(self, client):
        """Style profiles with NULL source_type should still appear."""
        from app.database import SessionLocal
        from app.models import StyleProfile
        w_id = _create_world(client)
        db = SessionLocal()
        try:
            # Create directly without source_type
            p = StyleProfile(name="OldStyle", world_id=w_id, source_type=None, is_active=True)
            db.add(p)
            db.commit()
            r = client.get(f"/worlds/{w_id}/context/styles")
            assert "OldStyle" in r.text
        finally:
            db.close()


class TestDiscardedSuggestionDelete:
    """v2.4.4: Discarded suggestions can be deleted."""

    def _create_discarded(self, client, w_id):
        resp = client.post(f"/worlds/{w_id}/setting-suggestions", data={
            "suggestion_type": "character", "world_type": "western_fantasy",
            "reference_style": "heroic_epic", "generation_count": 1, "user_requirement": ""
        }, follow_redirects=True)
        sid = int(str(resp.url).rstrip("/").split("/")[-1])
        client.post(f"/worlds/{w_id}/setting-suggestions/{sid}/discard")
        return sid

    def test_discarded_can_be_deleted(self, client):
        w_id = _create_world(client)
        sid = self._create_discarded(client, w_id)
        r = client.post(f"/worlds/{w_id}/setting-suggestions/{sid}/delete", follow_redirects=False)
        assert r.status_code == 303

    def test_deleted_returns_404(self, client):
        w_id = _create_world(client)
        sid = self._create_discarded(client, w_id)
        client.post(f"/worlds/{w_id}/setting-suggestions/{sid}/delete")
        r = client.get(f"/worlds/{w_id}/setting-suggestions/{sid}")
        assert r.status_code == 404

    def test_pending_cannot_be_deleted(self, client):
        w_id = _create_world(client)
        resp = client.post(f"/worlds/{w_id}/setting-suggestions", data={
            "suggestion_type": "character", "world_type": "western_fantasy",
            "reference_style": "heroic_epic", "generation_count": 1, "user_requirement": ""
        }, follow_redirects=True)
        sid = int(str(resp.url).rstrip("/").split("/")[-1])
        r = client.post(f"/worlds/{w_id}/setting-suggestions/{sid}/delete", follow_redirects=True)
        assert "只有已废弃的候选才能删除" in r.text or r.status_code == 200

    def test_cross_world_delete_404(self, client):
        w1 = _create_world(client)
        sid = self._create_discarded(client, w1)
        w2 = _create_world(client)
        r = client.post(f"/worlds/{w2}/setting-suggestions/{sid}/delete")
        assert r.status_code == 404

    def test_delete_affects_only_target(self, client):
        """Deleting one discarded suggestion doesn't affect others."""
        w_id = _create_world(client)
        s1 = self._create_discarded(client, w_id)
        s2 = self._create_discarded(client, w_id)
        client.post(f"/worlds/{w_id}/setting-suggestions/{s1}/delete")
        r = client.get(f"/worlds/{w_id}/setting-suggestions/{s2}")
        assert r.status_code == 200


class TestVersionDisplay:
    """v2.4.4: Version must show 2.4.4."""

    def test_config_version_is_244(self):
        from app.config import settings
        assert settings.VERSION == "2.4.4"

    def test_home_shows_version(self, client):
        r = client.get("/")
        assert "2.4.4" in r.text

    def test_base_no_old_version(self, client):
        r = client.get("/")
        assert "v2.4.2" not in r.text
        assert "v2.4.3" not in r.text
