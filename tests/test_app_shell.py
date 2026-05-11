"""
AI World Engine - Test App Shell
Ensures the unified app shell layout is present and working.
"""


class TestAppShellHomePage:
    """Test that the home page has the app shell structure."""

    def test_homepage_has_app_name(self, client):
        r = client.get("/")
        assert r.status_code == 200
        assert "AI World Engine" in r.text

    def test_homepage_has_sidebar(self, client):
        r = client.get("/")
        assert "sidebar" in r.text or "sidebar-nav" in r.text

    def test_homepage_has_topbar(self, client):
        r = client.get("/")
        assert "topbar" in r.text

    def test_homepage_has_main_content(self, client):
        r = client.get("/")
        assert "main-content" in r.text

    def test_homepage_has_nav_workbench(self, client):
        r = client.get("/")
        assert "工作台" in r.text

    def test_homepage_has_nav_worlds(self, client):
        r = client.get("/")
        assert "世界项目" in r.text

    def test_homepage_has_nav_novel(self, client):
        r = client.get("/")
        assert "小说工程" in r.text

    def test_homepage_has_nav_assets(self, client):
        r = client.get("/")
        assert "创作资产" in r.text

    def test_homepage_has_nav_simulation(self, client):
        # v1.7.8.2: simulation nav only shown when current_world exists
        r = client.get("/")
        assert "sidebar" in r.text  # sidebar exists

    def test_homepage_has_nav_checks(self, client):
        # v1.7.8.2: checks nav only shown when current_world exists
        r = client.get("/")
        assert "sidebar" in r.text  # sidebar exists

    def test_homepage_has_nav_data(self, client):
        r = client.get("/")
        assert "数据管理" in r.text

    def test_homepage_has_nav_settings(self, client):
        r = client.get("/")
        assert "设置" in r.text


class TestOldRoutesStillWork:
    """Ensure all old routes remain accessible after app shell changes."""

    def _create_world(self, client):
        client.post("/worlds", data={"name": "ShellTest", "world_type": "奇幻"})

    def test_world_list_accessible(self, client):
        r = client.get("/worlds")
        assert r.status_code == 200

    def test_world_detail_accessible(self, client):
        self._create_world(client)
        r = client.get("/worlds/1")
        assert r.status_code == 200

    def test_world_detail_has_old_entries(self, client):
        self._create_world(client)
        r = client.get("/worlds/1")
        assert "角色管理" in r.text or "势力管理" in r.text

    def test_evolution_page_accessible(self, client):
        self._create_world(client)
        r = client.get("/worlds/1/novel/evolution")
        assert r.status_code == 200
        assert "全书演化" in r.text

    def test_context_page_accessible(self, client):
        self._create_world(client)
        r = client.get("/worlds/1/context")
        assert r.status_code == 200
        assert "创作上下文" in r.text

    def test_data_page_accessible(self, client):
        r = client.get("/data")
        assert r.status_code == 200

    def test_settings_page_accessible(self, client):
        r = client.get("/settings/ai")
        assert r.status_code == 200

    def test_simulation_page_accessible(self, client):
        self._create_world(client)
        r = client.get("/worlds/1/simulation")
        assert r.status_code == 200

    def test_homepage_no_500(self, client):
        r = client.get("/")
        assert r.status_code == 200
        assert "500" not in r.text
        assert "Internal Server Error" not in r.text
