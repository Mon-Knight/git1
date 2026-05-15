"""
v2.0.1 — UI Terms Tests
验证页面术语已统一为作者视角。
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
    """Create a test world."""
    init_db()
    db = SessionLocal()
    try:
        world = World(name="术语测试世界", world_type="奇幻", description="测试")
        db.add(world)
        db.commit()
        db.refresh(world)
        return world.id
    finally:
        db.close()


class TestV201UITerms:
    """验证 v2.0.1 UI 术语调整。"""

    def test_page_shows_world_settings(self, client, test_world):
        """页面中显示"世界设定"。"""
        resp = client.get(f"/worlds/{test_world}")
        assert resp.status_code == 200
        # Check base.html sidebar which is included
        resp2 = client.get("/")
        assert "世界设定" in resp2.text, "页面应显示「世界设定」"

    def test_page_shows_quality_check(self, client):
        """页面中显示"质量检查"。"""
        resp = client.get("/")
        assert resp.status_code == 200
        assert "质量检查" in resp.text, "页面应显示「质量检查」"

    def test_page_shows_data_and_export(self, client):
        """页面中显示"数据与导出"。"""
        resp = client.get("/")
        assert resp.status_code == 200
        assert "数据与导出" in resp.text, "页面应显示「数据与导出」"

    def test_page_shows_context_package_term(self, client, test_world):
        """页面中显示"创作上下文包"（术语对应 context_package）。"""
        resp = client.get(f"/worlds/{test_world}/context")
        assert resp.status_code == 200
        html = resp.text
        # The UI should use "创作上下文包" rather than raw "context_package"
        assert "创作上下文包" in html or "上下文包" in html, (
            "创作资产页面应显示「创作上下文包」"
        )

    def test_page_shows_style_profile_term(self, client, test_world):
        """页面中显示"写作风格方案"（术语对应 style_profile）。"""
        resp = client.get(f"/worlds/{test_world}/context")
        assert resp.status_code == 200
        html = resp.text
        # Sidebar should show "写作风格方案"
        resp2 = client.get("/")
        assert "写作风格方案" in resp2.text or "风格方案" in resp2.text, (
            "侧边栏应显示「写作风格方案」"
        )

    def test_page_shows_plot_anchor_term(self, client, test_world):
        """页面中显示"剧情时间点"（术语对应 plot_anchor）。"""
        resp = client.get(f"/worlds/{test_world}/context")
        assert resp.status_code == 200
        html = resp.text
        resp2 = client.get("/")
        assert "剧情时间点" in resp2.text, "侧边栏应显示「剧情时间点」"

    def test_no_raw_dev_terms_in_nav(self, client):
        """侧边栏不直接暴露过多开发术语。"""
        resp = client.get("/")
        assert resp.status_code == 200
        html = resp.text

        # Dev terms that should NOT appear as visible UI labels
        dev_terms = ["context_package", "plot_anchor", "simulation_record"]
        import re
        for term in dev_terms:
            # Allow in URLs/data attributes, but not as visible text between tags
            visible_pattern = re.findall(f'>{term}<', html)
            assert len(visible_pattern) == 0, (
                f"开发术语 '{term}' 不应作为可见 UI 标签直接暴露"
            )

    def test_simulation_record_shown_as_scheme(self, client, test_world):
        """推演记录在 UI 中展示为「推演方案」或「推演记录」。"""
        resp = client.get(f"/worlds/{test_world}/records")
        assert resp.status_code == 200
        html = resp.text
        # Should use Chinese terminology
        assert "推演" in html, "推演记录页应使用中文术语"
