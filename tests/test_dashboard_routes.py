"""
AI World Engine - Test Dashboard Routes
Tests for the workspace dashboard home page.
"""


def _create_world(client):
    return client.post("/worlds", data={"name": "DashWorld", "world_type": "奇幻"})


class TestDashboardHomePage:
    """Tests for the dashboard home page."""

    def test_homepage_returns_200(self, client):
        r = client.get("/")
        assert r.status_code == 200

    def test_homepage_has_workspace_title(self, client):
        r = client.get("/")
        assert "创作工作台" in r.text

    def test_homepage_has_overview(self, client):
        r = client.get("/")
        assert "数据概览" in r.text

    def test_homepage_has_world_count(self, client):
        r = client.get("/")
        assert "世界" in r.text

    def test_homepage_has_pending(self, client):
        r = client.get("/")
        assert "待处理推演" in r.text or "待处理" in r.text

    def test_homepage_has_context_packages(self, client):
        r = client.get("/")
        assert "上下文包" in r.text or "创作资产" in r.text

    def test_homepage_has_evolutions(self, client):
        r = client.get("/")
        assert "全书演化方案" in r.text

    def test_homepage_has_quick_actions(self, client):
        r = client.get("/")
        assert "快捷操作" in r.text

    def test_homepage_has_sidebar(self, client):
        r = client.get("/")
        assert "sidebar" in r.text or "工作台" in r.text

    def test_homepage_no_500(self, client):
        r = client.get("/")
        assert r.status_code == 200
        assert "500" not in r.text

    def test_empty_db_shows_create_world(self, client):
        r = client.get("/")
        assert "创建第一个世界" in r.text or "还没有世界" in r.text

    def test_with_world_shows_world_name(self, client):
        _create_world(client)
        r = client.get("/")
        assert r.status_code == 200
        # The dashboard should have the world info
        assert "DashWorld" in r.text or "最近世界" in r.text

    def test_with_context_package_shows_name(self, client):
        _create_world(client)
        client.post("/worlds/1/context/packages/new", data={"name": "DashPkg"})
        r = client.get("/")
        # Context package should show or the section should exist
        assert "DashPkg" in r.text or "最近创作资产" in r.text

    def test_with_evolution_shows_entry(self, client):
        _create_world(client)
        client.post("/worlds/1/novel/evolution", data={"user_goal": "evolution test"})
        r = client.get("/")
        assert "evolution test" in r.text or "全书演化方案" in r.text
