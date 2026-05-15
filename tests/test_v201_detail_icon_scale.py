"""
v2.0.1 — Detail Page Icon Scale Tests
验证详情页图标尺寸统一规范。
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, init_db
from app.models import World, Character, Faction, Location, WorldRule
import re


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_world():
    """Create a test world with sample data."""
    init_db()
    db = SessionLocal()
    try:
        world = World(name="图标测试世界", world_type="奇幻", description="测试")
        db.add(world)
        db.commit()
        db.refresh(world)
        wid = world.id
        # Create sample data
        db.add(Character(name="角色A", role="战士", world_id=wid))
        db.add(Faction(name="势力A", faction_type="王国", world_id=wid))
        db.add(Location(name="地点A", location_type="城市", world_id=wid))
        db.add(WorldRule(name="规则A", rule_type="魔法", content="测试规则", world_id=wid))
        db.commit()
        return wid
    finally:
        db.close()


class TestV201DetailIconScale:
    """验证详情页使用统一的图标尺寸类。"""

    def test_novel_overview_has_detail_classes(self, client, test_world):
        """小说工程总览页使用统一布局类。"""
        resp = client.get(f"/worlds/{test_world}/novel")
        assert resp.status_code == 200
        html = resp.text
        # Should use dashboard class (overview is dashboard-type)
        assert 'page-dashboard' in html or 'page-novel-overview' in html

    def test_world_detail_no_large_inline_icons(self, client, test_world):
        """世界控制台不出现超大内联图标。"""
        resp = client.get(f"/worlds/{test_world}")
        assert resp.status_code == 200
        html = resp.text
        # No font-size: 64px or larger inline
        assert 'font-size:64px' not in html
        assert 'font-size: 64px' not in html

    def test_no_64px_font_size_anywhere(self, client, test_world):
        """详情页不出现 font-size: 64px。"""
        for route in [
            f"/worlds/{test_world}/novel/drafts",
            f"/worlds/{test_world}/novel/volume-outlines",
            f"/worlds/{test_world}/novel/chapter-outlines",
        ]:
            resp = client.get(route)
            if resp.status_code == 200:
                assert 'font-size:64px' not in resp.text, f"{route} 不应有64px"
                assert 'font-size: 64px' not in resp.text, f"{route} 不应有64px"

    def test_novel_drafts_has_detail_layout(self, client, test_world):
        """正文草稿列表页有合适的布局限制。"""
        resp = client.get(f"/worlds/{test_world}/novel/drafts")
        assert resp.status_code == 200
        html = resp.text
        # Should have max-width constraint
        assert 'max-width' in html.lower() or 'page-dashboard' in html

    def test_empty_state_icon_not_too_large(self, client, test_world):
        """空状态图标不超过48px。"""
        resp = client.get(f"/worlds/{test_world}/novel/drafts")
        assert resp.status_code == 200
        html = resp.text
        # Empty state icons should not have fontSize > 48px
        large_empty = re.findall(r'font-size:\s*([5-9]\d|\d{3,})px', html)
        assert len(large_empty) == 0, f"不应有>=50px图标: {large_empty}"

    def test_detail_pages_exist(self, client, test_world):
        """所有详情页可访问。"""
        routes = [
            f"/worlds/{test_world}",
            f"/worlds/{test_world}/characters",
            f"/worlds/{test_world}/factions",
            f"/worlds/{test_world}/locations",
            f"/worlds/{test_world}/rules",
            f"/worlds/{test_world}/events",
            f"/worlds/{test_world}/records",
            f"/worlds/{test_world}/branches",
            f"/worlds/{test_world}/checks",
            f"/worlds/{test_world}/novel/evolution",
        ]
        for route in routes:
            resp = client.get(route)
            assert resp.status_code == 200, f"{route} 应返回200"

    def test_app_shell_css_has_detail_classes(self, client):
        """app-shell.css 包含详情页图标类。"""
        resp = client.get("/static/css/app-shell.css")
        assert resp.status_code == 200
        css = resp.text
        required = [
            'detail-header',
            'detail-header-icon',
            'detail-title',
            'detail-section',
            'detail-section-icon',
            'meta-icon',
            'action-icon',
            'empty-state-icon',
            'flow-step-icon',
        ]
        for cls_name in required:
            assert f'.{cls_name}' in css or cls_name in css, (
                f"CSS应包含 {cls_name} 类"
            )

    def test_no_uncontrolled_icon_classes(self, client):
        """详情页不出现未受控超大图标类。"""
        resp = client.get("/")
        html = resp.text
        # These classes should not be used for icons
        assert 'icon-large' not in html, "不应使用 icon-large"
        assert 'hero-icon' not in html, "不应使用 hero-icon"

    def test_page_width_not_unlimited_2k(self, client, test_world):
        """详情页在2K宽度下不无限拉伸。"""
        resp = client.get(f"/worlds/{test_world}/novel/evolution")
        assert resp.status_code == 200
        html = resp.text
        # Should have some width constraint (via page class or max-width style)
        assert 'page-novel' in html or 'page-reading' in html or 'page-detail' in html or 'max-width' in html.lower(), (
            "详情页应有宽度约束"
        )
