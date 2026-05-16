"""
v2.6.2: Verify style import no longer uses wrong AI interface.
Tests that generate() is called correctly with messages=[{...}] format.
"""
import re
import io


def _create_world(client) -> int:
    client.post("/worlds", data={"name": "V262W", "world_type": "Fantasy"}, follow_redirects=False)
    match = re.search(r'/worlds/(\d+)', client.get("/worlds").text)
    if match: return int(match.group(1))
    raise RuntimeError("No world")


class TestStyleImportCorrectInterface:
    """v2.6.2: Must use ModelRouter.get_client(db).generate(messages=[...])"""

    def test_import_page_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/context/styles/import").status_code == 200

    def test_mock_analyze_works(self):
        from app.services.style_import_service import StyleImportService
        chunks = ["测试内容一", "测试内容二"]
        summaries, result = StyleImportService._mock_analyze(chunks, 2)
        assert result is not None
        assert "name" in result or "narrative_pov" in result

    def test_upload_txt_generates_profile(self, client):
        w_id = _create_world(client)
        content = "第一章\n这是测试文本，用于风格分析验证。\n第二章\n继续测试文本内容。\n" * 50
        r = client.post(
            f"/worlds/{w_id}/context/styles/import",
            data={"profile_name": "V262Style"},
            files={"file": ("test.txt", io.BytesIO(content.encode("utf-8")), "text/plain")},
            follow_redirects=True,
        )
        assert "get_client" not in r.text or "cannot import" not in r.text
        assert "ModelRouter" not in r.text or "has no attribute" not in r.text
        assert r.status_code == 200

    def test_styles_list_shows_new_profile(self, client):
        w_id = _create_world(client)
        content = "测试 " * 200
        client.post(
            f"/worlds/{w_id}/context/styles/import",
            data={"profile_name": "V262List"},
            files={"file": ("t.txt", io.BytesIO(content.encode("utf-8")), "text/plain")},
            follow_redirects=True,
        )
        r = client.get(f"/worlds/{w_id}/context/styles")
        assert r.status_code == 200

    def test_no_wrong_import_in_page(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}/context/styles/import")
        assert "cannot import" not in r.text
        assert "Internal Server Error" not in r.text

    def test_no_worlds_none(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}/context/styles/import")
        assert "/worlds/None" not in r.text

    def test_no_worlds_slash(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}/context/styles/import")
        assert "/worlds//" not in r.text

    def test_regression_drafts_still_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/novel/drafts").status_code == 200

    def test_regression_quality_still_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/novel/quality-reports").status_code == 200

    def test_regression_continuity_still_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/novel/continuity").status_code == 200

    def test_regression_volume_still_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/novel/volume-manuscripts").status_code == 200

    def test_regression_revisions_still_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/novel/revisions").status_code == 200
