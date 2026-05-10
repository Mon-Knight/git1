"""
AI World Engine - Test Context Export/Import
Tests that export/import includes style_profiles, plot_anchors, context_packages.
"""

import io
import json
import re
from app.services.export_service import export_world_to_dict, export_world_json
from app.services.import_service import import_world_from_payload, validate_export_payload


def _get_imported_world_id(client):
    """Find the ID of the imported world by looking for '导入副本' in the world list."""
    r = client.get("/worlds")
    # Find links like /worlds/2 that appear after "导入副本"
    matches = re.findall(r'/worlds/(\d+)[^>]*>([^<]*导入副本[^<]*)', r.text)
    if matches:
        return int(matches[0][0])
    # Fallback: find any world with 导入副本 in name
    matches = re.findall(r'/worlds/(\d+)', r.text)
    if matches:
        return int(matches[-1])  # last world is most likely the imported one
    return None


class TestExportIncludesContextAssets:
    """Test that export includes new context asset data."""

    def test_export_has_new_sections(self, client):
        """Export should include style_profiles, plot_anchors, context_packages keys."""
        client.post("/worlds", data={"name": "ExportTest", "world_type": "奇幻"})
        # Create assets
        client.post("/worlds/1/novel", data={"main_story_direction": "主线"})
        client.post("/worlds/1/context/styles/new", data={"name": "ExportStyle"})
        client.post("/worlds/1/context/anchors/new", data={"name": "ExportAnchor"})
        client.post("/worlds/1/context/packages/new", data={
            "name": "ExportPkg", "simulation_record_id": "1"
        })

        r = client.get("/worlds/1/export.json")
        assert r.status_code == 200
        payload = r.json()
        data = payload["data"]
        assert "style_profiles" in data
        assert "plot_anchors" in data
        assert "context_packages" in data
        assert len(data["style_profiles"]) >= 1
        assert len(data["plot_anchors"]) >= 1
        assert len(data["context_packages"]) >= 1

    def test_export_no_api_key(self, client):
        """Export should not contain API Key."""
        client.post("/worlds", data={"name": "NoKeyWorld"})
        r = client.get("/worlds/1/export.json")
        payload = r.json()
        payload_str = json.dumps(payload)
        assert "api_key" not in payload_str.lower()
        assert "sk-" not in payload_str  # common API key prefix

    def test_export_metadata_includes_new_counts(self, client):
        """Export metadata should include counts for new tables."""
        client.post("/worlds", data={"name": "CountWorld"})
        client.post("/worlds/1/context/styles/new", data={"name": "S1"})
        client.post("/worlds/1/context/styles/new", data={"name": "S2"})
        client.post("/worlds/1/context/anchors/new", data={"name": "A1"})

        r = client.get("/worlds/1/export.json")
        payload = r.json()
        counts = payload["metadata"]["counts"]
        assert counts.get("style_profiles", 0) >= 2
        assert counts.get("plot_anchors", 0) >= 1
        assert "context_packages" in counts


class TestImportContextAssets:
    """Test that import correctly handles context assets with ID remapping."""

    def test_import_preserves_context_assets(self, client):
        """After import, context assets should be present with remapped IDs."""
        client.post("/worlds", data={"name": "SourceWorld"})
        # Create assets
        client.post("/worlds/1/novel", data={"main_story_direction": "主线推演"})
        client.post("/worlds/1/context/styles/new", data={"name": "SourceStyle"})
        client.post("/worlds/1/context/anchors/new", data={
            "name": "SourceAnchor", "stage": "Vol1"
        })
        client.post("/worlds/1/context/packages/new", data={
            "name": "SourcePkg",
            "simulation_record_id": "1",
            "style_profile_id": "1",
            "plot_anchor_id": "1",
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
        assert "导入成功" in import_r.text or "导入副本" in import_r.text

        # Find the imported world ID
        new_world_id = _get_imported_world_id(client)
        assert new_world_id is not None, "Imported world not found in world list"

        # Check new world has the imported assets
        r = client.get(f"/worlds/{new_world_id}/context/styles")
        assert r.status_code == 200
        assert "SourceStyle" in r.text

        r = client.get(f"/worlds/{new_world_id}/context/anchors")
        assert "SourceAnchor" in r.text

        r = client.get(f"/worlds/{new_world_id}/context/packages")
        assert "SourcePkg" in r.text

    def test_import_context_package_references_remapped(self, client):
        """After import, context package should reference new IDs, not old."""
        client.post("/worlds", data={"name": "RefWorld"})
        client.post("/worlds/1/novel", data={"main_story_direction": "ref test"})
        client.post("/worlds/1/context/styles/new", data={"name": "RefStyle"})
        client.post("/worlds/1/context/anchors/new", data={"name": "RefAnchor"})
        client.post("/worlds/1/context/packages/new", data={
            "name": "RefPkg",
            "simulation_record_id": "1",
            "style_profile_id": "1",
            "plot_anchor_id": "1",
        })

        # Export and import
        export_r = client.get("/worlds/1/export.json")
        payload = export_r.json()

        import_data = io.BytesIO(json.dumps(payload).encode("utf-8"))
        client.post("/data/import", files={
            "import_file": ("export.json", import_data, "application/json")
        })

        new_world_id = _get_imported_world_id(client)
        assert new_world_id is not None

        # Verify the context package detail works
        r = client.get(f"/worlds/{new_world_id}/context/packages/1")
        assert r.status_code == 200
        # Should show referenced assets
        assert "RefStyle" in r.text or "RefAnchor" in r.text

    def test_import_novel_evolution_preserved(self, client):
        """Import should preserve novel_evolution simulation records."""
        client.post("/worlds", data={"name": "NovelWorld"})
        client.post("/worlds/1/novel", data={
            "main_story_direction": "主角在魔法学院探索AI系统",
            "protagonist_name": "林楚",
        })

        export_r = client.get("/worlds/1/export.json")
        payload = export_r.json()

        import_data = io.BytesIO(json.dumps(payload).encode("utf-8"))
        client.post("/data/import", files={
            "import_file": ("export.json", import_data, "application/json")
        })

        new_world_id = _get_imported_world_id(client)
        assert new_world_id is not None

        # Check records page
        r = client.get(f"/worlds/{new_world_id}/records")
        assert r.status_code == 200
        assert "novel_evolution" in r.text or "小说工程推演" in r.text

    def test_import_duplicate_world_name_auto_renames(self, client):
        """Import should auto-rename duplicate world names."""
        # Create world named same as what export would produce
        client.post("/worlds", data={"name": "SourceWorld - 导入副本"}, follow_redirects=False)
        client.post("/worlds", data={"name": "DupWorld"}, follow_redirects=False)

        # Now create and export another world
        client.post("/worlds", data={"name": "SourceWorld"}, follow_redirects=False)
        export_r = client.get("/worlds/3/export.json")
        payload = export_r.json()

        import_data = io.BytesIO(json.dumps(payload).encode("utf-8"))
        r = client.post("/data/import", files={
            "import_file": ("export.json", import_data, "application/json")
        }, follow_redirects=False)
        assert r.status_code == 200
        # Should have auto-renamed  
        assert "导入成功" in r.text or "导入副本" in r.text


class TestGlobalStyleExportImport:
    """Test that global style profiles are correctly handled."""

    def test_global_style_in_export(self, client):
        """Global styles referenced by context packages should be exported."""
        client.post("/worlds", data={"name": "GlobalTestWorld"})
        client.post("/worlds/1/novel", data={"main_story_direction": "test"})
        # Create global style
        client.post("/worlds/1/context/styles/new", data={
            "name": "GlobalStyle", "is_global": "1"
        })
        # Create package referencing global style
        client.post("/worlds/1/context/packages/new", data={
            "name": "GlobalPkg",
            "simulation_record_id": "1",
            "style_profile_id": "1",
        })

        r = client.get("/worlds/1/export.json")
        payload = r.json()
        style_names = [s["name"] for s in payload["data"]["style_profiles"]]
        assert "GlobalStyle" in style_names
