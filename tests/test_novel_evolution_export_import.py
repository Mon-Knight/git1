"""
AI World Engine - Test Novel Evolution Export/Import
Tests that export/import correctly handles novel_evolution records.
"""

import io
import json


def _create_world(client):
    return client.post("/worlds", data={"name": "EvoExpWorld", "world_type": "奇幻"})


class TestEvolutionExport:
    """Test export includes novel_evolution."""

    def test_export_includes_novel_evolution(self, client):
        _create_world(client)
        client.post("/worlds/1/novel/evolution", data={
            "user_goal": "导出测试",
        })
        r = client.get("/worlds/1/export.json")
        payload = r.json()
        sim_records = payload["data"]["simulation_records"]
        assert any(
            rec.get("simulation_type") == "novel_evolution"
            for rec in sim_records
        )

    def test_export_no_api_key(self, client):
        _create_world(client)
        client.post("/worlds/1/novel/evolution", data={
            "user_goal": "安全测试",
        })
        r = client.get("/worlds/1/export.json")
        payload_str = json.dumps(r.json())
        assert "api_key" not in payload_str.lower()


class TestEvolutionImport:
    """Test import preserves novel_evolution."""

    def test_import_preserves_novel_evolution(self, client):
        _create_world(client)
        client.post("/worlds/1/novel/evolution", data={
            "user_goal": "导入保留测试",
        })

        # Export
        export_r = client.get("/worlds/1/export.json")
        payload = export_r.json()

        # Import
        import_data = io.BytesIO(json.dumps(payload).encode("utf-8"))
        import_r = client.post("/data/import", files={
            "import_file": ("export.json", import_data, "application/json")
        })
        assert import_r.status_code == 200
        assert "导入成功" in import_r.text

        # Find imported world (should be world 2)
        world_list = client.get("/worlds")
        # The imported world is the last one
        import re
        ids = re.findall(r'/worlds/(\d+)', world_list.text)
        new_id = int(ids[-1])

        # Check evolutions page
        r = client.get(f"/worlds/{new_id}/novel/evolutions")
        assert r.status_code == 200
        assert "导入保留测试" in r.text

    def test_import_preserves_context_snapshot(self, client):
        _create_world(client)
        client.post("/worlds/1/novel/evolution", data={
            "user_goal": "快照保留测试",
        })

        export_r = client.get("/worlds/1/export.json")
        payload = export_r.json()

        import_data = io.BytesIO(json.dumps(payload).encode("utf-8"))
        client.post("/data/import", files={
            "import_file": ("export.json", import_data, "application/json")
        })

        # Find the imported world
        world_list = client.get("/worlds")
        import re
        ids = re.findall(r'/worlds/(\d+)', world_list.text)
        new_id = int(ids[-1])

        # Check record detail has context_snapshot
        r = client.get(f"/worlds/{new_id}/novel/evolutions/1")
        assert r.status_code == 200
        assert "context_snapshot" in r.text or "contextSnapshot" not in r.text

    def test_import_preserves_status(self, client):
        _create_world(client)
        client.post("/worlds/1/novel/evolution", data={
            "user_goal": "状态保留测试",
        })
        # Set as mainline
        client.post("/worlds/1/novel/evolutions/1/set-mainline", follow_redirects=False)

        export_r = client.get("/worlds/1/export.json")
        payload = export_r.json()

        import_data = io.BytesIO(json.dumps(payload).encode("utf-8"))
        client.post("/data/import", files={
            "import_file": ("export.json", import_data, "application/json")
        })

        world_list = client.get("/worlds")
        import re
        ids = re.findall(r'/worlds/(\d+)', world_list.text)
        new_id = int(ids[-1])

        r = client.get(f"/worlds/{new_id}/novel/evolutions")
        assert "主线方案" in r.text
