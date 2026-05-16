"""
v2.6.0: NovelVolumeExport model + service + routes + integration tests.
"""
import re
import os
import json


def _create_world(client) -> int:
    client.post("/worlds", data={"name": "VEWorld", "world_type": "Fantasy"}, follow_redirects=False)
    match = re.search(r'/worlds/(\d+)', client.get("/worlds").text)
    if match: return int(match.group(1))
    raise RuntimeError("No world")


class TestVolumeExportModel:
    def test_create(self, db):
        from app.models import NovelVolumeExport
        r = NovelVolumeExport(world_id=1, export_format="txt", file_name="test.txt", title="Vol1")
        db.add(r); db.commit()
        assert r.id is not None
        assert r.file_name == "test.txt"

    def test_json_stored(self, db):
        from app.models import NovelVolumeExport
        r = NovelVolumeExport(world_id=1, source_summary_json=json.dumps([{"id":1}], ensure_ascii=False))
        db.add(r); db.commit()
        assert "id" in r.source_summary_json

    def test_cross_world(self, db):
        from app.models import NovelVolumeExport
        r1 = NovelVolumeExport(world_id=1, title="W1")
        r2 = NovelVolumeExport(world_id=2, title="W2")
        db.add_all([r1, r2]); db.commit()
        from sqlalchemy import func
        assert db.query(func.count(NovelVolumeExport.id)).filter(NovelVolumeExport.world_id == 1).scalar() >= 1


class TestVolumeExportService:
    def test_export_directory_created(self):
        from app.services.novel_volume_export_service import NovelVolumeExportService
        d = NovelVolumeExportService.get_export_directory()
        assert os.path.isdir(d)

    def test_safe_filename(self):
        from app.services.novel_volume_export_service import NovelVolumeExportService
        assert NovelVolumeExportService.safe_filename("a:b?c") == "a_b_c"

    def test_build_context_no_world(self, db):
        from app.services.novel_volume_export_service import NovelVolumeExportService
        ctx = NovelVolumeExportService.build_volume_manuscript_context(db, 99999, 1)
        assert ctx["ok"] == False

    def test_list_exports_empty(self, db):
        from app.services.novel_volume_export_service import NovelVolumeExportService
        assert len(NovelVolumeExportService.list_volume_exports(db, 1)) == 0

    def test_get_nonexistent_export(self, db):
        from app.services.novel_volume_export_service import NovelVolumeExportService
        assert NovelVolumeExportService.get_volume_export(db, 1, 99999) is None


class TestVolumeExportRoutes:
    def test_list_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/novel/volume-manuscripts").status_code == 200

    def test_exports_list_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/novel/exports").status_code == 200

    def test_world_404(self, client):
        assert client.get("/worlds/99999/novel/volume-manuscripts").status_code == 404

    def test_extends_base(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}/novel/volume-manuscripts")
        assert "app-main-inner" in r.text or "app-shell-body" in r.text

    def test_no_worlds_none(self, client):
        w_id = _create_world(client)
        for url in [f"/worlds/{w_id}/novel/volume-manuscripts", f"/worlds/{w_id}/novel/exports"]:
            assert "/worlds/None" not in client.get(url).text

    def test_no_worlds_slash(self, client):
        w_id = _create_world(client)
        for url in [f"/worlds/{w_id}/novel/volume-manuscripts", f"/worlds/{w_id}/novel/exports"]:
            assert "/worlds//" not in client.get(url).text

    def test_regression_continuity_still_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/novel/continuity").status_code == 200

    def test_regression_drafts_still_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/novel/drafts").status_code == 200

    def test_regression_styles_still_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/context/styles").status_code == 200

    def test_regression_setting_suggestions_still_200(self, client):
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/setting-suggestions").status_code == 200

    def test_world_detail_has_volume_management_entry(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}")
        assert "卷内正文管理" in r.text or "volume-manuscripts" in r.text
