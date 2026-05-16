"""
v2.2.0 — Sidebar Clickable State Tests
验证左侧导航高亮可点击、分组主链接与折叠按钮分离、禁用态正确。
"""

import re
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def _find_tag(html: str, pattern: str, label: str) -> str:
    match = re.search(pattern, html)
    assert match, f"未找到 {label}"
    return match.group(1)


def _read_css() -> str:
    with open("app/static/css/app-shell.css", "r", encoding="utf-8") as f:
        return f.read()


class TestSidebarClickableStates:
    def test_dashboard_active_is_anchor(self, client):
        html = client.get("/").text
        tag = _find_tag(
            html,
            r'(<a[^>]*data-nav="dashboard"[^>]*>)',
            "工作台主链接",
        )
        assert tag.startswith("<a"), "工作台 active 应为 a 标签"

    def test_dashboard_active_has_href(self, client):
        html = client.get("/").text
        tag = _find_tag(
            html,
            r'(<a[^>]*data-nav="dashboard"[^>]*>)',
            "工作台主链接",
        )
        assert 'href="/"' in tag, "工作台 active 应保留 href=/"

    def test_active_not_disabled_class(self, client):
        html = client.get("/").text
        tag = _find_tag(
            html,
            r'(<a[^>]*data-nav="dashboard"[^>]*>)',
            "工作台主链接",
        )
        class_match = re.search(r'class="([^"]*)"', tag)
        cls = class_match.group(1) if class_match else ""
        assert "disabled" not in cls, "active 项不应包含 disabled class"

    def test_active_not_aria_disabled(self, client):
        html = client.get("/").text
        tag = _find_tag(
            html,
            r'(<a[^>]*data-nav="dashboard"[^>]*>)',
            "工作台主链接",
        )
        assert 'aria-disabled="true"' not in tag, "active 项不应有 aria-disabled"

    def test_active_not_pointer_events_none(self):
        css = _read_css()
        assert re.search(r'\.sidebar-link\.active[^}]*pointer-events\s*:\s*none', css) is None
        assert re.search(r'\.sidebar-group-main-link\.active[^}]*pointer-events\s*:\s*none', css) is None

    def test_novel_group_main_link_exists(self, client):
        html = client.get("/").text
        assert re.search(r'<a[^>]*class="[^"]*sidebar-group-main-link[^"]*"[^>]*data-nav="novel"', html)

    def test_novel_group_toggle_exists(self, client):
        html = client.get("/").text
        assert re.search(r'<button[^>]*class="[^"]*sidebar-group-toggle[^"]*"[^>]*data-nav="novel"', html)

    def test_novel_main_link_and_toggle_separate(self, client):
        html = client.get("/").text
        link_tag = _find_tag(
            html,
            r'(<a[^>]*class="[^"]*sidebar-group-main-link[^"]*"[^>]*data-nav="novel"[^>]*>)',
            "小说工程主链接",
        )
        toggle_tag = _find_tag(
            html,
            r'(<button[^>]*class="[^"]*sidebar-group-toggle[^"]*"[^>]*data-nav="novel"[^>]*>)',
            "小说工程折叠按钮",
        )
        assert link_tag != toggle_tag, "主链接与折叠按钮必须是不同元素"

    def test_world_group_main_link_exists(self, client):
        html = client.get("/").text
        assert re.search(r'<a[^>]*class="[^"]*sidebar-group-main-link[^"]*"[^>]*data-nav="worlds"', html)

    def test_assets_group_main_link_exists(self, client):
        html = client.get("/").text
        assert re.search(r'<a[^>]*class="[^"]*sidebar-group-main-link[^"]*"[^>]*data-nav="assets"', html)

    def test_simulation_group_main_link_exists(self, client):
        html = client.get("/").text
        assert re.search(r'<a[^>]*class="[^"]*sidebar-group-main-link[^"]*"[^>]*data-nav="simulation"', html)

    def test_checks_group_main_link_exists(self, client):
        html = client.get("/").text
        assert re.search(r'<a[^>]*class="[^"]*sidebar-group-main-link[^"]*"[^>]*data-nav="checks"', html)

    def test_data_main_link_exists(self, client):
        html = client.get("/").text
        assert re.search(r'<a[^>]*data-nav="data"[^>]*>', html)

    def test_settings_group_main_link_exists(self, client):
        html = client.get("/").text
        assert re.search(r'<a[^>]*class="[^"]*sidebar-group-main-link[^"]*"[^>]*data-nav="settings"', html)

    def test_no_worlds_none_links(self, client):
        html = client.get("/").text
        assert "/worlds/None" not in html

    def test_no_double_slash_world_links(self, client):
        html = client.get("/").text
        assert 'href="/worlds//"' not in html

    def test_no_world_shows_choose_world(self, client):
        html = client.get("/").text
        assert "选择世界" in html

    def test_coming_soon_has_aria_disabled(self, client):
        html = client.get("/").text
        for tag in re.findall(r'<[^>]*coming-soon[^>]*>', html):
            assert 'aria-disabled="true"' in tag

    def test_coming_soon_has_no_href(self, client):
        html = client.get("/").text
        assert re.search(r'coming-soon[^>]*href=', html) is None

    def test_current_page_has_aria_current(self, client):
        html = client.get("/").text
        tag = _find_tag(
            html,
            r'(<a[^>]*data-nav="dashboard"[^>]*>)',
            "工作台主链接",
        )
        assert 'aria-current="page"' in tag

    def test_group_toggle_has_aria_expanded(self, client):
        html = client.get("/").text
        tag = _find_tag(
            html,
            r'(<button[^>]*class="[^"]*sidebar-group-toggle[^"]*"[^>]*data-nav="novel"[^>]*>)',
            "小说工程折叠按钮",
        )
        assert "aria-expanded" in tag

    def test_group_toggle_has_aria_controls(self, client):
        html = client.get("/").text
        tag = _find_tag(
            html,
            r'(<button[^>]*class="[^"]*sidebar-group-toggle[^"]*"[^>]*data-nav="novel"[^>]*>)',
            "小说工程折叠按钮",
        )
        assert "aria-controls" in tag
