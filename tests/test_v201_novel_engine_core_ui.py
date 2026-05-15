"""
v2.0.1 — Novel Engineering Core UI Tests
验证小说工程总览页及其子模块入口。
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, init_db
from app.models import World


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_world():
    """Create a test world and return its ID."""
    init_db()
    db = SessionLocal()
    try:
        world = World(name="测试世界_v201", world_type="奇幻", description="测试")
        db.add(world)
        db.commit()
        db.refresh(world)
        return world.id
    finally:
        db.close()


class TestV201NovelEngineCoreUI:
    """验证小说工程总览页功能。"""

    def test_novel_overview_page_accessible(self, client, test_world):
        """小说工程总览页可打开。"""
        resp = client.get(f"/worlds/{test_world}/novel")
        assert resp.status_code == 200, f"小说工程总览应返回200，实际{resp.status_code}"

    def test_novel_overview_contains_world_name(self, client, test_world):
        """小说工程总览包含世界名称。"""
        resp = client.get(f"/worlds/{test_world}/novel")
        assert resp.status_code == 200
        assert "测试世界_v201" in resp.text

    def test_novel_overview_contains_flow(self, client, test_world):
        """小说工程总览包含流程展示。"""
        resp = client.get(f"/worlds/{test_world}/novel")
        assert resp.status_code == 200
        html = resp.text
        assert "世界设定" in html or "小说工程流程" in html, "应包含流程展示"

    def test_novel_overview_contains_evolution_status(self, client, test_world):
        """小说工程总览包含全书演化状态。"""
        resp = client.get(f"/worlds/{test_world}/novel")
        assert resp.status_code == 200
        assert "全书演化" in resp.text, "应包含全书演化"

    def test_novel_overview_contains_volume_outlines(self, client, test_world):
        """小说工程总览包含分卷大纲。"""
        resp = client.get(f"/worlds/{test_world}/novel")
        assert resp.status_code == 200
        assert "分卷大纲" in resp.text, "应包含分卷大纲"

    def test_novel_overview_contains_chapter_outlines(self, client, test_world):
        """小说工程总览包含章节大纲。"""
        resp = client.get(f"/worlds/{test_world}/novel")
        assert resp.status_code == 200
        assert "章节大纲" in resp.text, "应包含章节大纲"

    def test_novel_overview_contains_drafts(self, client, test_world):
        """小说工程总览包含正文草稿。"""
        resp = client.get(f"/worlds/{test_world}/novel")
        assert resp.status_code == 200
        assert "正文草稿" in resp.text, "应包含正文草稿"

    def test_novel_overview_quality_check_future(self, client, test_world):
        """小说工程总览包含质量检查后续开放。"""
        resp = client.get(f"/worlds/{test_world}/novel")
        assert resp.status_code == 200
        html = resp.text
        assert "质量检查" in html, "应包含质量检查"
        assert "后续开放" in html or "v2.1.0" in html or "后续版本" in html, (
            "质量检查应标注为后续开放"
        )

    def test_novel_overview_polish_future(self, client, test_world):
        """小说工程总览包含正文润色后续开放。"""
        resp = client.get(f"/worlds/{test_world}/novel")
        assert resp.status_code == 200
        html = resp.text
        assert "润色" in html, "应包含正文润色"

    def test_novel_overview_export_future(self, client, test_world):
        """小说工程总览包含定稿导出后续开放。"""
        resp = client.get(f"/worlds/{test_world}/novel")
        assert resp.status_code == 200
        html = resp.text
        assert "导出" in html, "应包含定稿导出"

    def test_novel_overview_evolution_link_works(self, client, test_world):
        """全书演化入口可跳转。"""
        resp = client.get(f"/worlds/{test_world}/novel/evolution")
        assert resp.status_code == 200, f"全书演化页应返回200，实际{resp.status_code}"

    def test_novel_overview_volume_outlines_link_works(self, client, test_world):
        """分卷大纲入口可跳转。"""
        resp = client.get(f"/worlds/{test_world}/novel/volume-outlines")
        assert resp.status_code == 200, f"分卷大纲页应返回200，实际{resp.status_code}"

    def test_novel_overview_chapter_outlines_link_works(self, client, test_world):
        """章节大纲入口可跳转。"""
        resp = client.get(f"/worlds/{test_world}/novel/chapter-outlines")
        assert resp.status_code == 200, f"章节大纲页应返回200，实际{resp.status_code}"

    def test_novel_overview_drafts_link_works(self, client, test_world):
        """正文草稿入口可跳转。"""
        resp = client.get(f"/worlds/{test_world}/novel/drafts")
        assert resp.status_code == 200, f"正文草稿页应返回200，实际{resp.status_code}"

    def test_novel_overview_no_404_for_future_items(self, client, test_world):
        """未实现入口不应返回404（因为是禁用态而非链接）。"""
        resp = client.get(f"/worlds/{test_world}/novel")
        assert resp.status_code == 200
        # Future items should NOT be clickable links pointing to non-existent pages
        html = resp.text
        # They should be spans or disabled, not active <a> links to /novel/quality-check etc.
        assert "/novel/quality-check" not in html, "不应生成错误的质量检查链接"
        assert "/novel/polish" not in html, "不应生成错误的润色链接"
