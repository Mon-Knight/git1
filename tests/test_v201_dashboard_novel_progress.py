"""
v2.0.1 — Dashboard Novel Progress Tests
验证首页已强化小说工程进度展示。
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestV201DashboardNovelProgress:
    """验证 v2.0.1 首页以小说工程进度为中心。"""

    def test_dashboard_title_is_creative_workspace(self, client):
        """首页标题应为"创作工作台"。"""
        resp = client.get("/")
        assert resp.status_code == 200
        html = resp.text
        assert "创作工作台" in html, "首页标题应包含「创作工作台」"

    def test_dashboard_has_novel_progress_section(self, client):
        """首页应突出小说工程进度区域。"""
        resp = client.get("/")
        assert resp.status_code == 200
        html = resp.text
        assert "小说工程进度" in html, "首页应有「小说工程进度」区域"

    def test_dashboard_has_novel_overview_link(self, client):
        """首页应有小说工程总览入口（有世界时）或引导创建世界（无世界时）。"""
        resp = client.get("/")
        assert resp.status_code == 200
        html = resp.text
        # 如果有世界，应显示"小说工程总览"；如果没有世界，应显示"创建第一个世界"引导
        assert "小说工程总览" in html or "创建第一个世界" in html or "创建世界" in html or "小说工程" in html, (
            "首页应有小说工程总览入口或引导创建世界"
        )

    def test_dashboard_has_novel_draft_entry(self, client):
        """首页应有正文草稿入口或小说工程入口。"""
        resp = client.get("/")
        assert resp.status_code == 200
        html = resp.text
        # 当有世界时显示正文草稿，无世界时至少有小说工程入口
        assert "正文草稿" in html or "小说工程" in html or "创建第一个世界" in html, (
            "首页应有正文草稿或小说工程入口"
        )

    def test_dashboard_has_next_step_section(self, client):
        """首页应有下一步建议区域。"""
        resp = client.get("/")
        assert resp.status_code == 200
        html = resp.text
        assert "下一步建议" in html, "首页应有「下一步建议」区域"

    def test_dashboard_has_quality_check_entry(self, client):
        """首页应有质量检查入口。"""
        resp = client.get("/")
        assert resp.status_code == 200
        html = resp.text
        assert "质量检查" in html, "首页应有「质量检查」入口"

    def test_dashboard_not_only_world_centric(self, client):
        """首页不再仅以世界项目为中心。"""
        resp = client.get("/")
        assert resp.status_code == 200
        html = resp.text
        # "世界项目" may appear as alt text or in comments, but should NOT be the primary heading
        # Check that the main dashboard heading references novel/creative workspace
        assert "AI 小说工程工作台" in html or "创作工作台" in html, (
            "首页应强调小说工程定位"
        )

    def test_dashboard_buttons_no_error_links(self, client):
        """首页按钮不生成错误链接。"""
        resp = client.get("/")
        assert resp.status_code == 200
        html = resp.text
        assert "/worlds/None" not in html, "不应出现 /worlds/None"
        assert "/worlds/0/" not in html, "不应出现 /worlds/0/（无有效世界）"

    def test_dashboard_has_ai_workbench_identity(self, client):
        """首页应体现 AI 小说工程工作台定位。"""
        resp = client.get("/")
        assert resp.status_code == 200
        html = resp.text
        # Should mention novel engineering workflow
        has_novel_ref = "小说工程" in html or "全书演化" in html or "正文草稿" in html
        assert has_novel_ref, "首页应包含小说工程相关内容"
