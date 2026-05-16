"""
v2.0.1 — UI Navigation Structure Tests
验证左侧导航结构已调整为小说工程核心化。
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestV201NavigationStructure:
    """验证 v2.0.1 左侧导航结构调整。"""

    def test_nav_contains_novel_engineering(self, client):
        """左侧导航包含"小说工程"。"""
        resp = client.get("/")
        assert resp.status_code == 200
        html = resp.text
        assert "小说工程" in html, "左侧导航应包含「小说工程」"

    def test_nav_contains_world_settings(self, client):
        """左侧导航包含"世界设定"。"""
        resp = client.get("/")
        assert resp.status_code == 200
        html = resp.text
        assert "世界设定" in html, "左侧导航应包含「世界设定」"

    def test_nav_contains_creative_assets(self, client):
        """左侧导航包含"创作资产"。"""
        resp = client.get("/")
        assert resp.status_code == 200
        html = resp.text
        assert "创作资产" in html, "左侧导航应包含「创作资产」"

    def test_nav_contains_ai_simulation(self, client):
        """左侧导航包含"AI 推演"。"""
        resp = client.get("/")
        assert resp.status_code == 200
        html = resp.text
        assert "AI 推演" in html, "左侧导航应包含「AI 推演」"

    def test_nav_contains_quality_check(self, client):
        """左侧导航包含"质量检查"。"""
        resp = client.get("/")
        assert resp.status_code == 200
        html = resp.text
        assert "质量检查" in html, "左侧导航应包含「质量检查」"

    def test_nav_contains_data_export(self, client):
        """左侧导航包含"数据与导出"。"""
        resp = client.get("/")
        assert resp.status_code == 200
        html = resp.text
        assert "数据与导出" in html, "左侧导航应包含「数据与导出」"

    def test_nav_contains_settings(self, client):
        """左侧导航包含"设置"。"""
        resp = client.get("/")
        assert resp.status_code == 200
        html = resp.text
        assert "设置" in html, "左侧导航应包含「设置」"

    def test_nav_order_novel_before_world_settings(self, client):
        """小说工程应排在世界设定之前。"""
        resp = client.get("/")
        assert resp.status_code == 200
        html = resp.text
        novel_pos = html.find("小说工程")
        world_pos = html.find("世界设定")
        assert novel_pos > 0, "页面应包含「小说工程」"
        assert world_pos > 0, "页面应包含「世界设定」"
        assert novel_pos < world_pos, (
            f"小说工程(position={novel_pos})应在世界设定(position={world_pos})之前"
        )

    def test_no_worlds_none_in_nav(self, client):
        """不生成 /worlds/None 链接。"""
        resp = client.get("/")
        assert resp.status_code == 200
        html = resp.text
        assert "/worlds/None" not in html, "不应出现 /worlds/None"

    def test_no_double_slash_in_nav(self, client):
        """不生成 /worlds// 链接。"""
        resp = client.get("/")
        assert resp.status_code == 200
        html = resp.text
        # Check for href containing /worlds// but NOT /worlds/{id}/
        import re
        double_slash = re.findall(r'href="[^"]*/worlds//', html)
        assert len(double_slash) == 0, f"不应出现 /worlds// 链接: {double_slash}"

    def test_nav_has_sidebar_groups(self, client):
        """v2.0.1 应有多组 sidebar-group。"""
        resp = client.get("/")
        assert resp.status_code == 200
        html = resp.text
        # Should have multiple sidebar-group elements
        import re
        groups = re.findall(r'sidebar-group', html)
        assert len(groups) >= 4, f"应有至少4个sidebar-group，但只有{len(groups)}个"

    def test_old_world_project_not_primary(self, client):
        """旧"世界项目"不应作为核心主入口优先于小说工程。"""
        resp = client.get("/")
        assert resp.status_code == 200
        html = resp.text
        # "世界项目" may still appear in comments or attributes, but shouldn't be a primary nav label
        # Check that sidebar link text doesn't show "世界项目" as a top-level label
        # (it may appear in templates as a comment, which is fine)
        import re
        # Check sidebar-link text for "世界项目"
        sidebar_pattern = re.findall(r'sidebar-link[^>]*>([^<]*世界项目[^<]*)<', html)
        assert len(sidebar_pattern) == 0, (
            f"「世界项目」不应再作为顶层导航标签: {sidebar_pattern}"
        )

    def test_app_version_in_html(self, client):
        """HTML 中应显示 2.1.0 版本号。"""
        resp = client.get("/")
        assert resp.status_code == 200
        html = resp.text
        assert "2.4.2" in html, "页面应包含版本号 2.4.1"
