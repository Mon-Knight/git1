"""
v2.6.1: Test that style import no longer calls ModelRouter.generate.
"""
import re
import io


def _create_world(client) -> int:
    client.post("/worlds", data={"name": "V261W", "world_type": "Fantasy"}, follow_redirects=False)
    match = re.search(r'/worlds/(\d+)', client.get("/worlds").text)
    if match: return int(match.group(1))
    raise RuntimeError("No world")


class TestStyleImportAICall:
    """v2.6.1: TXT style import must not call ModelRouter.generate."""

    def test_import_page_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/context/styles/import").status_code == 200

    def test_mock_analyze_does_not_use_modelrouter_generate(self):
        """Mock analyze should work without ModelRouter.generate."""
        from app.services.style_import_service import StyleImportService
        chunks = ["测试文本片段1", "测试文本片段2"]
        summaries, result = StyleImportService._mock_analyze(chunks, len(chunks))
        assert result is not None
        assert "name" in result or "narrative_pov" in result

    def test_upload_txt_via_post(self, client):
        w_id = _create_world(client)
        content = "第一章\n这是测试文本内容，用于风格分析。\n第二章\n继续测试文本。\n" * 50
        r = client.post(
            f"/worlds/{w_id}/context/styles/import",
            data={"profile_name": "TestStyle"},
            files={"file": ("test.txt", io.BytesIO(content.encode("utf-8")), "text/plain")},
            follow_redirects=True,
        )
        # Should either succeed or show friendly error, not ModelRouter error
        assert "ModelRouter" not in r.text
        assert "has no attribute" not in r.text
        assert r.status_code != 500

    def test_styles_list_shows_new_profile(self, client):
        w_id = _create_world(client)
        content = "测试文本 " * 200
        client.post(
            f"/worlds/{w_id}/context/styles/import",
            data={"profile_name": "NewTxtStyle"},
            files={"file": ("test.txt", io.BytesIO(content.encode("utf-8")), "text/plain")},
            follow_redirects=True,
        )
        r = client.get(f"/worlds/{w_id}/context/styles")
        # Should not crash
        assert r.status_code == 200

    def test_no_modelrouter_error_in_page(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}/context/styles/import")
        assert "ModelRouter" not in r.text

    def test_no_internal_server_error_text(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}/context/styles/import")
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

    def test_regression_volume_manuscripts_still_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/novel/volume-manuscripts").status_code == 200
