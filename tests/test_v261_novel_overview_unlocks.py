"""
v2.6.2: Test that novel engineering overview has all completed modules unlocked.
"""
import re


def _create_world(client) -> int:
    client.post("/worlds", data={"name": "UnlockW", "world_type": "Fantasy"}, follow_redirects=False)
    match = re.search(r'/worlds/(\d+)', client.get("/worlds").text)
    if match: return int(match.group(1))
    raise RuntimeError("No world")


class TestNovelOverviewUnlocks:
    """All completed v2.x features must be clickable in the novel engineering overview."""

    def test_quality_reports_not_locked(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}")
        assert "quality-reports" in r.text

    def test_quality_reports_link_correct(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}")
        assert f"/worlds/{w_id}/novel/quality-reports" in r.text

    def test_revisions_not_locked(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}")
        assert "/novel/revisions" in r.text

    def test_final_drafts_not_locked(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}")
        assert "/novel/final-drafts" in r.text

    def test_continuity_not_locked(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}")
        assert "/novel/continuity" in r.text

    def test_volume_manuscripts_not_locked(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}")
        assert "/novel/volume-manuscripts" in r.text

    def test_no_v210_open_hint(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}")
        assert "v2.1.0 开放" not in r.text

    def test_future_items_still_disabled(self, client):
        """Only truly future items should be disabled."""
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}")
        assert "整卷生成" in r.text or "整书导出" in r.text

    def test_no_worlds_none(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}")
        assert "/worlds/None" not in r.text


class TestNovelOverviewRouteTargets:
    """All linked routes must return 200."""

    def test_quality_reports_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/novel/quality-reports").status_code == 200

    def test_revisions_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/novel/revisions").status_code == 200

    def test_final_drafts_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/novel/final-drafts").status_code == 200

    def test_continuity_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/novel/continuity").status_code == 200

    def test_volume_manuscripts_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/novel/volume-manuscripts").status_code == 200

    def test_drafts_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/novel/drafts").status_code == 200

    def test_current_world_not_lost(self, client):
        w_id = _create_world(client)
        for url in [f"/worlds/{w_id}/novel/quality-reports", f"/worlds/{w_id}/novel/revisions",
                     f"/worlds/{w_id}/novel/final-drafts", f"/worlds/{w_id}/novel/continuity"]:
            r = client.get(url)
            assert "请先选择世界" not in r.text
