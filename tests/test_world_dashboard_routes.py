"""
AI World Engine - Test World Dashboard Routes
Tests for /worlds/{id} world console.
"""


def _create_world(client):
    return client.post("/worlds", data={"name": "WorldConsole", "world_type": "奇幻"})


class TestWorldConsoleRoutes:
    """Tests for the world console page."""

    def test_world_detail_200(self, client):
        _create_world(client)
        r = client.get("/worlds/1")
        assert r.status_code == 200

    def test_world_detail_has_console_title(self, client):
        _create_world(client)
        r = client.get("/worlds/1")
        assert "世界控制台" in r.text

    def test_world_detail_has_name(self, client):
        _create_world(client)
        r = client.get("/worlds/1")
        assert "WorldConsole" in r.text

    def test_world_detail_has_overview(self, client):
        _create_world(client)
        r = client.get("/worlds/1")
        assert "世界数据概览" in r.text

    def test_world_detail_has_progress(self, client):
        _create_world(client)
        r = client.get("/worlds/1")
        assert "创作进度" in r.text

    def test_world_detail_has_novel_status(self, client):
        _create_world(client)
        r = client.get("/worlds/1")
        assert "小说工程状态" in r.text

    def test_world_detail_has_asset_status(self, client):
        _create_world(client)
        r = client.get("/worlds/1")
        assert "创作资产状态" in r.text

    def test_world_detail_has_recent_activity(self, client):
        _create_world(client)
        r = client.get("/worlds/1")
        assert "最近动态" in r.text

    def test_world_detail_has_recommendations(self, client):
        _create_world(client)
        r = client.get("/worlds/1")
        assert "推荐下一步" in r.text

    def test_world_detail_has_quick_actions(self, client):
        _create_world(client)
        r = client.get("/worlds/1")
        assert "快捷操作" in r.text

    def test_world_detail_has_characters_entry(self, client):
        _create_world(client)
        r = client.get("/worlds/1")
        assert "角色管理" in r.text

    def test_world_detail_has_factions_entry(self, client):
        _create_world(client)
        r = client.get("/worlds/1")
        assert "势力管理" in r.text

    def test_world_detail_has_locations_entry(self, client):
        _create_world(client)
        r = client.get("/worlds/1")
        assert "地点管理" in r.text

    def test_world_detail_has_rules_entry(self, client):
        _create_world(client)
        r = client.get("/worlds/1")
        assert "规则管理" in r.text

    def test_world_detail_has_events_entry(self, client):
        _create_world(client)
        r = client.get("/worlds/1")
        assert "历史事件" in r.text

    def test_world_detail_has_timeline_entry(self, client):
        _create_world(client)
        r = client.get("/worlds/1")
        assert "时间线" in r.text

    def test_world_detail_has_simulation_entry(self, client):
        _create_world(client)
        r = client.get("/worlds/1")
        assert "AI 推演" in r.text

    def test_world_detail_has_records_entry(self, client):
        _create_world(client)
        r = client.get("/worlds/1")
        assert "推演记录" in r.text

    def test_world_detail_has_branches_entry(self, client):
        _create_world(client)
        r = client.get("/worlds/1")
        assert "分支记录" in r.text

    def test_world_detail_has_checks_entry(self, client):
        _create_world(client)
        r = client.get("/worlds/1")
        assert "检查中心" in r.text

    def test_world_detail_has_context_entry(self, client):
        _create_world(client)
        r = client.get("/worlds/1")
        assert "创作上下文" in r.text

    def test_world_detail_has_novel_entry(self, client):
        _create_world(client)
        r = client.get("/worlds/1")
        assert "全书演化" in r.text

    def test_world_detail_404(self, client):
        r = client.get("/worlds/999")
        assert r.status_code == 404

    def test_world_detail_has_shell(self, client):
        _create_world(client)
        r = client.get("/worlds/1")
        assert "sidebar" in r.text or "sidebar-nav" in r.text
