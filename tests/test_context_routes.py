"""
AI World Engine - Test Context Routes
Tests for /worlds/{id}/context/... routes.
"""


def _create_world(client):
    return client.post("/worlds", data={"name": "ContextTestWorld", "world_type": "奇幻"})


class TestContextIndex:
    """Tests for context overview page."""

    def test_context_index_200(self, client):
        _create_world(client)
        r = client.get("/worlds/1/context")
        assert r.status_code == 200
        assert "创作上下文资产库" in r.text

    def test_context_index_404(self, client):
        r = client.get("/worlds/999/context")
        assert r.status_code == 404


class TestStyleRoutes:
    """Tests for style profile routes."""

    def test_styles_list_200(self, client):
        _create_world(client)
        r = client.get("/worlds/1/context/styles")
        assert r.status_code == 200

    def test_styles_new_form_200(self, client):
        _create_world(client)
        r = client.get("/worlds/1/context/styles/new")
        assert r.status_code == 200

    def test_create_style_success(self, client):
        _create_world(client)
        r = client.post("/worlds/1/context/styles/new", data={
            "name": "测试风格", "genre": "奇幻", "pacing": "快速推进"
        }, follow_redirects=False)
        assert r.status_code == 303

    def test_create_style_empty_name(self, client):
        _create_world(client)
        r = client.post("/worlds/1/context/styles/new", data={"name": ""})
        assert r.status_code == 422
        assert "不能为空" in r.text

    def test_edit_style_form_200(self, client):
        _create_world(client)
        client.post("/worlds/1/context/styles/new", data={"name": "EditStyle"})
        r = client.get("/worlds/1/context/styles/1/edit")
        assert r.status_code == 200

    def test_edit_style_form_404(self, client):
        _create_world(client)
        r = client.get("/worlds/1/context/styles/999/edit")
        assert r.status_code == 404

    def test_update_style_redirects(self, client):
        _create_world(client)
        client.post("/worlds/1/context/styles/new", data={"name": "UpdateStyle"})
        r = client.post("/worlds/1/context/styles/1/edit", data={
            "name": "UpdatedStyle", "genre": "科幻"
        }, follow_redirects=False)
        assert r.status_code == 303

    def test_delete_style_redirects(self, client):
        _create_world(client)
        client.post("/worlds/1/context/styles/new", data={"name": "DelStyle"})
        r = client.post("/worlds/1/context/styles/1/delete", follow_redirects=False)
        assert r.status_code == 303

    def test_styles_404_for_nonexistent_world(self, client):
        r = client.get("/worlds/999/context/styles/new")
        assert r.status_code == 404


class TestAnchorRoutes:
    """Tests for plot anchor routes."""

    def test_anchors_list_200(self, client):
        _create_world(client)
        r = client.get("/worlds/1/context/anchors")
        assert r.status_code == 200

    def test_anchors_new_form_200(self, client):
        _create_world(client)
        r = client.get("/worlds/1/context/anchors/new")
        assert r.status_code == 200

    def test_create_anchor_success(self, client):
        _create_world(client)
        r = client.post("/worlds/1/context/anchors/new", data={
            "name": "开篇", "stage": "第一卷"
        }, follow_redirects=False)
        assert r.status_code == 303

    def test_create_anchor_empty_name(self, client):
        _create_world(client)
        r = client.post("/worlds/1/context/anchors/new", data={"name": ""})
        assert r.status_code == 422

    def test_edit_anchor_form_200(self, client):
        _create_world(client)
        client.post("/worlds/1/context/anchors/new", data={"name": "EditAnchor"})
        r = client.get("/worlds/1/context/anchors/1/edit")
        assert r.status_code == 200

    def test_delete_anchor_redirects(self, client):
        _create_world(client)
        client.post("/worlds/1/context/anchors/new", data={"name": "DelAnchor"})
        r = client.post("/worlds/1/context/anchors/1/delete", follow_redirects=False)
        assert r.status_code == 303

    def test_anchors_404_for_nonexistent_world(self, client):
        r = client.get("/worlds/999/context/anchors")
        assert r.status_code == 404


class TestPackageRoutes:
    """Tests for context package routes."""

    def _setup_assets(self, client):
        """Create world, sim record, style, anchor. Returns world_id."""
        _create_world(client)
        # Create sim record via novel post
        client.post("/worlds/1/novel", data={
            "main_story_direction": "测试主线方向"
        })
        # Create style
        client.post("/worlds/1/context/styles/new", data={"name": "PkgStyle"})
        # Create anchor
        client.post("/worlds/1/context/anchors/new", data={"name": "PkgAnchor"})

    def test_packages_list_200(self, client):
        _create_world(client)
        r = client.get("/worlds/1/context/packages")
        assert r.status_code == 200

    def test_packages_new_form_200(self, client):
        _create_world(client)
        r = client.get("/worlds/1/context/packages/new")
        assert r.status_code == 200

    def test_create_package_success(self, client):
        self._setup_assets(client)
        r = client.post("/worlds/1/context/packages/new", data={
            "name": "TestPkg",
            "simulation_record_id": "1",
            "style_profile_id": "1",
            "plot_anchor_id": "1",
            "generation_type": "章节正文",
        }, follow_redirects=False)
        assert r.status_code == 303

    def test_create_package_empty_name(self, client):
        self._setup_assets(client)
        r = client.post("/worlds/1/context/packages/new", data={"name": ""})
        assert r.status_code == 422

    def test_package_detail_200(self, client):
        self._setup_assets(client)
        client.post("/worlds/1/context/packages/new", data={
            "name": "DetailPkg",
            "simulation_record_id": "1",
            "style_profile_id": "1",
            "plot_anchor_id": "1",
        })
        r = client.get("/worlds/1/context/packages/1")
        assert r.status_code == 200
        assert "DetailPkg" in r.text

    def test_package_detail_404_cross_world(self, client):
        """Package detail should 404 if accessed from wrong world."""
        _create_world(client)
        _create_world(client)  # world 2
        # Create package in world 1
        client.post("/worlds/1/novel", data={"main_story_direction": "test"})
        client.post("/worlds/1/context/packages/new", data={"name": "W1Pkg"})
        # Try to access from world 2
        r = client.get("/worlds/2/context/packages/1")
        assert r.status_code == 404

    def test_edit_package_form_200(self, client):
        self._setup_assets(client)
        client.post("/worlds/1/context/packages/new", data={
            "name": "EditPkg", "simulation_record_id": "1"
        })
        r = client.get("/worlds/1/context/packages/1/edit")
        assert r.status_code == 200

    def test_update_package_redirects(self, client):
        self._setup_assets(client)
        client.post("/worlds/1/context/packages/new", data={
            "name": "UpdatePkg", "simulation_record_id": "1"
        })
        r = client.post("/worlds/1/context/packages/1/edit", data={
            "name": "UpdatedPkg", "simulation_record_id": "1"
        }, follow_redirects=False)
        assert r.status_code == 303

    def test_delete_package_redirects(self, client):
        self._setup_assets(client)
        client.post("/worlds/1/context/packages/new", data={
            "name": "DelPkg", "simulation_record_id": "1"
        })
        r = client.post("/worlds/1/context/packages/1/delete", follow_redirects=False)
        assert r.status_code == 303

    def test_packages_404_for_nonexistent_world(self, client):
        r = client.get("/worlds/999/context/packages/new")
        assert r.status_code == 404


class TestWorldDetailEntry:
    """Test that world detail page has creative context entry."""

    def test_world_detail_has_context_entry(self, client):
        _create_world(client)
        r = client.get("/worlds/1")
        assert r.status_code == 200
        assert "/context" in r.text
        assert "创作上下文" in r.text


class TestNovelFormIntegration:
    """Test that novel form integrates context package selection."""

    def test_novel_form_has_context_package_dropdown(self, client):
        """v2.0.1: Context package dropdown appears when packages exist."""
        _create_world(client)
        # Create a context package first so the dropdown appears
        client.post("/worlds/1/context/packages/new", data={"name": "TestPkg"})
        r = client.get("/worlds/1/novel/evolution")
        assert r.status_code == 200
        assert "context_package_id" in r.text

    def test_novel_post_with_context_package(self, client):
        _create_world(client)
        # Create sim record
        client.post("/worlds/1/novel", data={"main_story_direction": "first run"})
        # Create context package
        client.post("/worlds/1/context/packages/new", data={"name": "NovelPkg"})
        # Run novel with context package
        r = client.post("/worlds/1/novel", data={
            "main_story_direction": "使用上下文包推演",
            "context_package_id": "1",
        })
        assert r.status_code == 200


class TestCrossWorldIsolation:
    """Test cross-world data isolation in routes."""

    def test_style_not_visible_from_other_world(self, client):
        _create_world(client)
        client.post("/worlds/1/context/styles/new", data={"name": "W1Style"})
        _create_world(client)  # world 2
        r = client.get("/worlds/2/context/styles")
        # No world-specific styles should be visible
        assert "W1Style" not in r.text

    def test_anchor_not_visible_from_other_world(self, client):
        _create_world(client)
        client.post("/worlds/1/context/anchors/new", data={"name": "W1Anchor"})
        _create_world(client)  # world 2
        r = client.get("/worlds/2/context/anchors")
        assert "W1Anchor" not in r.text

    def test_package_not_visible_from_other_world(self, client):
        _create_world(client)
        client.post("/worlds/1/novel", data={"main_story_direction": "test"})
        client.post("/worlds/1/context/packages/new", data={"name": "W1Pkg"})
        _create_world(client)  # world 2
        r = client.get("/worlds/2/context/packages")
        assert "W1Pkg" not in r.text
