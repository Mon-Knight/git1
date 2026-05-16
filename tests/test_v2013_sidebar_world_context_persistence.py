"""
v2.0.1.3 — Sidebar World Context Persistence Tests
验证左侧导航跨模块 current_world 不丢失、链接正确生成、无坏链接。
Uses conftest.py shared test database (no custom override).
"""

import re
import pytest
from app.database import SessionLocal
from app.services.world_service import WorldService


def _get_html(client, path):
    return client.get(path).text


def _has_text(html, text):
    return text in html


def _has_no_text(html, text):
    return text not in html


def _has_link(html, href):
    return f'href="{href}"' in html or f"href='{href}'" in html


def _create_test_world() -> int:
    """Create a test world and return its ID."""
    db = SessionLocal()
    try:
        world = WorldService.create_world(
            db,
            name="蓝星",
            world_type="科幻",
            description="测试世界",
            current_era="纪元1",
            tone="冒险",
        )
        db.commit()
        return world.id
    finally:
        db.close()


class TestWorldContextPersistence:
    """v2.0.1.3: Sidebar current_world persistence across module pages."""

    def test_world_detail_has_current_world(self, client):
        """世界详情页应包含 current_world 信息在侧边栏中."""
        world_id = _create_test_world()
        html = _get_html(client, f"/worlds/{world_id}")
        assert _has_text(html, "蓝星"), "世界详情页应显示世界名称"
        assert _has_link(html, f"/worlds/{world_id}/context"), \
            "世界详情页侧边栏应包含创作资产链接"
        assert _has_link(html, f"/worlds/{world_id}/simulation"), \
            "世界详情页侧边栏应包含 AI 推演链接"
        assert _has_link(html, f"/worlds/{world_id}/checks"), \
            "世界详情页侧边栏应包含质量检查链接"

    def test_context_page_no_select_world_hint(self, client):
        """创作资产页面不应显示'请先选择世界'."""
        world_id = _create_test_world()
        html = _get_html(client, f"/worlds/{world_id}/context")
        assert _has_no_text(html, "请先选择世界以管理创作资产"), \
            "创作资产页面不应显示'请先选择世界以管理创作资产'"

    def test_context_page_has_cross_module_links(self, client):
        """创作资产页面侧边栏应包含其他模块链接."""
        world_id = _create_test_world()
        html = _get_html(client, f"/worlds/{world_id}/context")
        assert _has_link(html, f"/worlds/{world_id}/simulation"), \
            "创作资产页面应包含 AI 推演链接"
        assert _has_link(html, f"/worlds/{world_id}/checks"), \
            "创作资产页面应包含质量检查链接"
        assert _has_link(html, f"/worlds/{world_id}/novel/evolution"), \
            "创作资产页面应包含小说工程链接"

    def test_simulation_page_no_select_world_hint(self, client):
        """AI 推演页面不应显示'请先选择世界'."""
        world_id = _create_test_world()
        html = _get_html(client, f"/worlds/{world_id}/simulation")
        assert _has_no_text(html, "请先选择世界以进行 AI 推演"), \
            "AI 推演页面不应显示'请先选择世界以进行 AI 推演'"

    def test_simulation_page_has_cross_module_links(self, client):
        """AI 推演页面侧边栏应包含其他模块链接."""
        world_id = _create_test_world()
        html = _get_html(client, f"/worlds/{world_id}/simulation")
        assert _has_link(html, f"/worlds/{world_id}/context"), \
            "AI 推演页面应包含创作资产链接"
        assert _has_link(html, f"/worlds/{world_id}/checks"), \
            "AI 推演页面应包含质量检查链接"

    def test_checks_page_no_select_world_hint(self, client):
        """质量检查页面不应显示'请先选择世界'."""
        world_id = _create_test_world()
        html = _get_html(client, f"/worlds/{world_id}/checks")
        assert _has_no_text(html, "请先选择世界以进行质量检查"), \
            "质量检查页面不应显示'请先选择世界以进行质量检查'"

    def test_checks_page_has_cross_module_links(self, client):
        """质量检查页面侧边栏应包含其他模块链接."""
        world_id = _create_test_world()
        html = _get_html(client, f"/worlds/{world_id}/checks")
        assert _has_link(html, f"/worlds/{world_id}/context"), \
            "质量检查页面应包含创作资产链接"
        assert _has_link(html, f"/worlds/{world_id}/simulation"), \
            "质量检查页面应包含 AI 推演链接"

    def test_novel_drafts_page_no_select_world_hint(self, client):
        """小说草稿页面不应显示'请先选择世界'."""
        world_id = _create_test_world()
        html = _get_html(client, f"/worlds/{world_id}/novel/drafts")
        assert _has_no_text(html, "请先选择世界以使用小说工程"), \
            "小说草稿页面不应显示'请先选择世界以使用小说工程'"


class TestNoBrokenLinks:
    """v2.0.1.3: 确保不生成 /worlds/None 或 /worlds// 坏链接."""

    def test_no_none_world_id(self, client):
        """任何页面不应生成 /worlds/None."""
        for path in ["/", "/worlds"]:
            html = _get_html(client, path)
            assert '"/worlds/None"' not in html, f"{path} 不应包含 /worlds/None"
            assert "'/worlds/None'" not in html, f"{path} 不应包含 /worlds/None"

    def test_no_double_slash_world_id(self, client):
        """任何页面不应生成 /worlds//."""
        for path in ["/", "/worlds"]:
            html = _get_html(client, path)
            assert '"/worlds//"' not in html, f"{path} 不应包含 /worlds//"

    def test_active_has_href(self, client):
        """active 项应保留 href."""
        world_id = _create_test_world()
        html = _get_html(client, f"/worlds/{world_id}")
        match = re.search(
            r'<a[^>]*class="[^"]*active[^"]*"[^>]*>',
            html
        )
        assert match, "应存在 active 链接"
        tag = match.group(0)
        assert 'href=' in tag, "active 项应保留 href"

    def test_active_no_aria_disabled(self, client):
        """active 项不应包含 aria-disabled."""
        world_id = _create_test_world()
        html = _get_html(client, f"/worlds/{world_id}")
        match = re.search(
            r'<a[^>]*class="[^"]*active[^"]*"[^>]*>',
            html
        )
        assert match, "应存在 active 链接"
        tag = match.group(0)
        assert 'aria-disabled="true"' not in tag, "active 项不应包含 aria-disabled"

    def test_disabled_has_aria_disabled(self, client):
        """禁用项应包含 aria-disabled."""
        html = _get_html(client, "/")
        assert 'aria-disabled="true"' in html, "应存在 aria-disabled 项"


class TestCrossModuleNavigation:
    """v2.0.1.3: 跨模块导航测试."""

    def test_context_to_simulation_link_exists(self, client):
        """创作资产页面包含跳转到 AI 推演的链接."""
        world_id = _create_test_world()
        html = _get_html(client, f"/worlds/{world_id}/context")
        assert _has_link(html, f"/worlds/{world_id}/simulation"), \
            "创作资产→AI推演链接应存在"

    def test_simulation_to_checks_link_exists(self, client):
        """AI 推演页面包含跳转到质量检查的链接."""
        world_id = _create_test_world()
        html = _get_html(client, f"/worlds/{world_id}/simulation")
        assert _has_link(html, f"/worlds/{world_id}/checks"), \
            "AI推演→质量检查链接应存在"

    def test_checks_to_context_link_exists(self, client):
        """质量检查页面包含跳转到创作资产的链接."""
        world_id = _create_test_world()
        html = _get_html(client, f"/worlds/{world_id}/checks")
        assert _has_link(html, f"/worlds/{world_id}/context"), \
            "质量检查→创作资产链接应存在"


class TestModuleMainLinksClickable:
    """v2.0.1.3: 分组主链接在 current_world 存在时均可点击."""

    def test_assets_main_link_clickable(self, client):
        """创作资产主链接可点击."""
        world_id = _create_test_world()
        html = _get_html(client, f"/worlds/{world_id}")
        assert _has_link(html, f"/worlds/{world_id}/context"), \
            "创作资产主链接应 /worlds/{id}/context"

    def test_simulation_main_link_clickable(self, client):
        """AI 推演主链接可点击."""
        world_id = _create_test_world()
        html = _get_html(client, f"/worlds/{world_id}")
        assert _has_link(html, f"/worlds/{world_id}/simulation"), \
            "AI 推演主链接应 /worlds/{id}/simulation"

    def test_checks_main_link_clickable(self, client):
        """质量检查主链接可点击."""
        world_id = _create_test_world()
        html = _get_html(client, f"/worlds/{world_id}")
        assert _has_link(html, f"/worlds/{world_id}/checks"), \
            "质量检查主链接应 /worlds/{id}/checks"


class TestNoWorldState:
    """v2.0.1.3: 无 current_world 时模块应禁用且显示引导."""

    def test_no_world_context_shows_select_hint(self, client):
        """无世界时显示引导."""
        html = _get_html(client, "/worlds")
        assert _has_text(html, "请先选择世界") or _has_text(html, "选择世界"), \
            "无世界时应显示选择世界引导"

    def test_no_world_no_broken_module_links(self, client):
        """无世界时模块主链接应指向 /worlds 而非坏链接."""
        html = _get_html(client, "/worlds")
        assert _has_link(html, "/worlds"), \
            "无世界时模块主链接应指向 /worlds"
