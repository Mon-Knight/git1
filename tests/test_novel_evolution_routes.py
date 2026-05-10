"""
AI World Engine - Test Novel Evolution Routes
Tests for /worlds/{id}/novel/evolution and related routes.
"""


def _create_world(client):
    return client.post("/worlds", data={"name": "EvoTestWorld", "world_type": "奇幻"})


def _setup_context_package(client):
    """Create world, sim record, style, anchor, and context package."""
    _create_world(client)
    client.post("/worlds/1/novel", data={"main_story_direction": "setup"})
    client.post("/worlds/1/context/styles/new", data={"name": "EvoStyle"})
    client.post("/worlds/1/context/anchors/new", data={"name": "EvoAnchor"})
    client.post("/worlds/1/context/packages/new", data={
        "name": "EvoPkg", "simulation_record_id": "1",
        "style_profile_id": "1", "plot_anchor_id": "1",
    })


class TestEvolutionFormRoutes:
    """Tests for evolution form page."""

    def test_evolution_form_200(self, client):
        _create_world(client)
        r = client.get("/worlds/1/novel/evolution")
        assert r.status_code == 200
        assert "全书演化推演" in r.text

    def test_evolution_form_404(self, client):
        r = client.get("/worlds/999/novel/evolution")
        assert r.status_code == 404

    def test_evolution_form_with_context_package(self, client):
        _setup_context_package(client)
        r = client.get("/worlds/1/novel/evolution?context_package_id=1")
        assert r.status_code == 200
        assert "EvoPkg" in r.text

    def test_evolution_form_cross_world_package_404(self, client):
        _create_world(client)
        _create_world(client)  # world 2
        client.post("/worlds/2/novel", data={"main_story_direction": "w2"})
        client.post("/worlds/2/context/packages/new", data={"name": "W2Pkg"})
        # Try to use world 2's package from world 1
        r = client.get("/worlds/1/novel/evolution?context_package_id=1")
        assert r.status_code == 404

    def test_evolution_form_no_packages_shows_hint(self, client):
        _create_world(client)
        r = client.get("/worlds/1/novel/evolution")
        assert "尚未创建创作上下文包" in r.text or "不使用上下文包" in r.text


class TestEvolutionPostRoutes:
    """Tests for evolution POST."""

    def test_post_without_package(self, client):
        _create_world(client)
        r = client.post("/worlds/1/novel/evolution", data={
            "user_goal": "基于当前世界生成全书路线",
        })
        assert r.status_code == 200
        assert "全书演化方案" in r.text

    def test_post_with_package(self, client):
        _setup_context_package(client)
        r = client.post("/worlds/1/novel/evolution", data={
            "context_package_id": "1",
            "user_goal": "使用上下文包生成全书路线",
        })
        assert r.status_code == 200
        assert "全书演化方案" in r.text

    def test_post_empty_goal(self, client):
        _create_world(client)
        r = client.post("/worlds/1/novel/evolution", data={"user_goal": ""})
        assert r.status_code == 422
        assert "不能为空" in r.text

    def test_post_saves_record(self, client):
        _create_world(client)
        client.post("/worlds/1/novel/evolution", data={
            "user_goal": "保存记录测试",
        })
        r = client.get("/worlds/1/records")
        assert "全书演化推演" in r.text

    def test_post_does_not_auto_adopt(self, client):
        _create_world(client)
        client.post("/worlds/1/novel/evolution", data={
            "user_goal": "不自动采纳测试",
        })
        r = client.get("/worlds/1/novel/evolutions")
        assert "待确认" in r.text

    def test_post_mock_ai_has_structure(self, client):
        _create_world(client)
        r = client.post("/worlds/1/novel/evolution", data={
            "user_goal": "结构化测试",
        })
        assert "## 一、小说定位" in r.text or "小说定位" in r.text


class TestEvolutionListRoutes:
    """Tests for evolutions list page."""

    def test_evolutions_list_200(self, client):
        _create_world(client)
        r = client.get("/worlds/1/novel/evolutions")
        assert r.status_code == 200
        assert "全书演化方案" in r.text

    def test_evolutions_list_404(self, client):
        r = client.get("/worlds/999/novel/evolutions")
        assert r.status_code == 404

    def test_evolutions_list_shows_record(self, client):
        _create_world(client)
        client.post("/worlds/1/novel/evolution", data={
            "user_goal": "列表测试目标",
        })
        r = client.get("/worlds/1/novel/evolutions")
        assert "列表测试目标" in r.text


class TestEvolutionDetailRoutes:
    """Tests for evolution detail page."""

    def test_detail_200(self, client):
        _create_world(client)
        client.post("/worlds/1/novel/evolution", data={
            "user_goal": "详情测试",
        })
        r = client.get("/worlds/1/novel/evolutions/1")
        assert r.status_code == 200
        assert "详情测试" in r.text

    def test_detail_404(self, client):
        _create_world(client)
        r = client.get("/worlds/1/novel/evolutions/999")
        assert r.status_code == 404

    def test_detail_cross_world_404(self, client):
        _create_world(client)
        client.post("/worlds/1/novel/evolution", data={"user_goal": "w1"})
        _create_world(client)  # world 2
        r = client.get("/worlds/2/novel/evolutions/1")
        assert r.status_code == 404


class TestEvolutionStatusRoutes:
    """Tests for set-mainline, set-candidate, discard."""

    def _create_evo(self, client):
        _create_world(client)
        client.post("/worlds/1/novel/evolution", data={"user_goal": "状态测试"})

    def test_set_mainline(self, client):
        self._create_evo(client)
        r = client.post("/worlds/1/novel/evolutions/1/set-mainline", follow_redirects=False)
        assert r.status_code == 303

    def test_set_candidate(self, client):
        self._create_evo(client)
        r = client.post("/worlds/1/novel/evolutions/1/set-candidate", follow_redirects=False)
        assert r.status_code == 303

    def test_discard(self, client):
        self._create_evo(client)
        r = client.post("/worlds/1/novel/evolutions/1/discard", follow_redirects=False)
        assert r.status_code == 303

    def test_status_404_for_non_evolution(self, client):
        _create_world(client)
        # Create a normal simulation record
        client.post("/worlds/1/simulation", data={
            "question": "普通推演", "simulation_type": "general"
        })
        r = client.post("/worlds/1/novel/evolutions/1/set-mainline", follow_redirects=False)
        assert r.status_code == 404

    def test_status_cross_world_404(self, client):
        self._create_evo(client)
        _create_world(client)  # world 2
        r = client.post("/worlds/2/novel/evolutions/1/set-mainline", follow_redirects=False)
        assert r.status_code == 404


class TestWorldDetailEntry:
    """Test world detail page entries."""

    def test_world_detail_has_evolution_entries(self, client):
        _create_world(client)
        r = client.get("/worlds/1")
        assert "/novel/evolution" in r.text
        assert "/novel/evolutions" in r.text
        assert "全书演化推演" in r.text


class TestContextPackageDetailEntry:
    """Test context package detail has evolution link."""

    def test_package_detail_has_evolution_link(self, client):
        _setup_context_package(client)
        r = client.get("/worlds/1/context/packages/1")
        assert "/novel/evolution?context_package_id=1" in r.text
