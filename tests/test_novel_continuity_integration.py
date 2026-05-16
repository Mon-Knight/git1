"""
v2.5.0: NovelContinuity integration + UI adaptation tests.
"""
import re


def _create_world(client) -> int:
    client.post("/worlds", data={"name": "IntWorld", "world_type": "Fantasy"}, follow_redirects=False)
    match = re.search(r'/worlds/(\d+)', client.get("/worlds").text)
    if match: return int(match.group(1))
    raise RuntimeError("No world")


class TestContinuityIntegration:
    def test_world_detail_has_continuity_entry(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}")
        assert "连续性检查" in r.text or "continuity" in r.text.lower()

    def test_novel_engineering_has_continuity_link(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}")
        assert "/novel/continuity" in r.text

    def test_list_uses_app_layout(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}/novel/continuity")
        assert "app-main-inner" in r.text or "app-shell-body" in r.text

    def test_new_uses_page_form(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}/novel/continuity/new")
        assert "form" in r.text.lower() or "Form" in r.text

    def test_detail_shows_status_tag(self, client):
        w_id = _create_world(client)
        resp = client.post(f"/worlds/{w_id}/novel/continuity", data={
            "range_type": "recent", "recent_count": 1
        }, follow_redirects=True)
        assert "候选" in resp.text or "报告" in resp.text

    def test_regression_drafts_still_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/novel/drafts").status_code == 200

    def test_regression_quality_still_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/novel/quality-reports").status_code == 200

    def test_regression_revisions_still_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/novel/revisions").status_code == 200

    def test_regression_final_drafts_still_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/novel/final-drafts").status_code == 200

    def test_regression_styles_still_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/context/styles").status_code == 200

    def test_regression_setting_suggestions_still_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/setting-suggestions").status_code == 200
