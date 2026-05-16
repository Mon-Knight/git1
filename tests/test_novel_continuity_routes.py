"""
v2.5.0: NovelContinuity routes tests.
"""
import re


def _create_world(client) -> int:
    client.post("/worlds", data={"name": "CTWorld", "world_type": "Fantasy"}, follow_redirects=False)
    match = re.search(r'/worlds/(\d+)', client.get("/worlds").text)
    if match: return int(match.group(1))
    raise RuntimeError("No world")


class TestContinuityRoutes:
    def test_list_200(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}/novel/continuity")
        assert r.status_code == 200

    def test_new_200(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}/novel/continuity/new")
        assert r.status_code == 200

    def test_new_has_range_select(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}/novel/continuity/new")
        assert "range_type" in r.text

    def test_post_creates_and_redirects(self, client):
        w_id = _create_world(client)
        r = client.post(f"/worlds/{w_id}/novel/continuity", data={
            "range_type": "recent", "recent_count": 3, "user_requirement": ""
        }, follow_redirects=False)
        assert r.status_code == 303

    def test_detail_200(self, client):
        w_id = _create_world(client)
        r = client.post(f"/worlds/{w_id}/novel/continuity", data={
            "range_type": "recent", "recent_count": 2
        }, follow_redirects=True)
        assert r.status_code == 200
        assert "连续性" in r.text or "报告" in r.text

    def test_detail_shows_score(self, client):
        w_id = _create_world(client)
        r = client.post(f"/worlds/{w_id}/novel/continuity", data={
            "range_type": "recent", "recent_count": 2
        }, follow_redirects=True)
        assert "82" in r.text

    def test_set_current(self, client):
        w_id = _create_world(client)
        resp = client.post(f"/worlds/{w_id}/novel/continuity", data={
            "range_type": "recent", "recent_count": 2
        }, follow_redirects=True)
        rid = int(str(resp.url).rstrip("/").split("/")[-1])
        r = client.post(f"/worlds/{w_id}/novel/continuity/{rid}/set-current", follow_redirects=False)
        assert r.status_code == 303

    def test_discard(self, client):
        w_id = _create_world(client)
        resp = client.post(f"/worlds/{w_id}/novel/continuity", data={
            "range_type": "recent", "recent_count": 2
        }, follow_redirects=True)
        rid = int(str(resp.url).rstrip("/").split("/")[-1])
        r = client.post(f"/worlds/{w_id}/novel/continuity/{rid}/discard", follow_redirects=False)
        assert r.status_code == 303

    def test_world_404(self, client):
        r = client.get("/worlds/99999/novel/continuity")
        assert r.status_code == 404

    def test_report_404(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}/novel/continuity/99999")
        assert r.status_code == 404

    def test_cross_world_404(self, client):
        w1 = _create_world(client)
        resp = client.post(f"/worlds/{w1}/novel/continuity", data={
            "range_type": "recent", "recent_count": 1
        }, follow_redirects=True)
        rid = int(str(resp.url).rstrip("/").split("/")[-1])
        w2 = _create_world(client)
        r = client.get(f"/worlds/{w2}/novel/continuity/{rid}")
        assert r.status_code == 404

    def test_extends_base(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}/novel/continuity")
        assert "app-main-inner" in r.text or "app-shell-body" in r.text

    def test_no_worlds_none(self, client):
        w_id = _create_world(client)
        for url in [f"/worlds/{w_id}/novel/continuity", f"/worlds/{w_id}/novel/continuity/new"]:
            assert "/worlds/None" not in client.get(url).text

    def test_no_worlds_slash(self, client):
        w_id = _create_world(client)
        for url in [f"/worlds/{w_id}/novel/continuity", f"/worlds/{w_id}/novel/continuity/new"]:
            assert "/worlds//" not in client.get(url).text

    def test_list_empty_state(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}/novel/continuity")
        assert "暂无" in r.text or "没有" in r.text.lower() or "empty" in r.text.lower()
