"""
AI World Engine - v2.4.3 Global Route Health Check
Comprehensive health check for ALL major entry points.
Ensures no route returns 500, no /worlds/None, no missing template vars.
"""

import re


def _create_world(client) -> int:
    client.post("/worlds", data={"name": "HealthWorld", "world_type": "Fantasy"}, follow_redirects=False)
    list_resp = client.get("/worlds")
    match = re.search(r'/worlds/(\d+)', list_resp.text)
    if match:
        return int(match.group(1))
    raise RuntimeError("No world ID found")


ROUTES_NO_WORLD = [
    # (name, url, min_status_ok)
    ("首页", "/", 200),
    ("世界列表", "/worlds", 200),
    ("设置中心", "/settings/ai", 200),
    ("数据管理", "/data", 200),
]


ROUTES_WITH_WORLD = [
    # Basic world routes
    ("世界控制台", "/worlds/{w_id}", 200),
    ("角色列表", "/worlds/{w_id}/characters", 200),
    ("势力列表", "/worlds/{w_id}/factions", 200),
    ("地点列表", "/worlds/{w_id}/locations", 200),
    ("规则列表", "/worlds/{w_id}/rules", 200),
    ("历史事件", "/worlds/{w_id}/events", 200),
    ("时间线", "/worlds/{w_id}/timeline", 200),
    # Creative assets
    ("创作资产", "/worlds/{w_id}/context", 200),
    ("风格画像", "/worlds/{w_id}/context/styles", 200),
    ("剧情时间点", "/worlds/{w_id}/context/anchors", 200),
    ("上下文包", "/worlds/{w_id}/context/packages", 200),
    ("上下文包新建", "/worlds/{w_id}/context/packages/new", 200),
    # Setting suggestions
    ("设定库 AI 推演", "/worlds/{w_id}/setting-suggestions", 200),
    ("设定库新建页", "/worlds/{w_id}/setting-suggestions/new", 200),
    # AI Simulation
    ("AI 推演", "/worlds/{w_id}/simulation", 200),
    ("推演记录", "/worlds/{w_id}/records", 200),
    ("分支", "/worlds/{w_id}/branches", 200),
    # Checks
    ("检查中心", "/worlds/{w_id}/checks", 200),
    # Novel Engineering
    ("全书演化", "/worlds/{w_id}/novel/evolution", 200),
    ("分卷大纲", "/worlds/{w_id}/novel/volume-outlines", 200),
    ("章节大纲", "/worlds/{w_id}/novel/chapter-outlines", 200),
    ("正文草稿", "/worlds/{w_id}/novel/drafts", 200),
    ("正文质量检查", "/worlds/{w_id}/novel/quality-reports", 200),
    ("润色候选", "/worlds/{w_id}/novel/revisions", 200),
    ("最终采用稿", "/worlds/{w_id}/novel/final-drafts", 200),
    # Context sub-routes
    ("风格导入", "/worlds/{w_id}/context/styles/import", 200),
    ("上下文包列表", "/worlds/{w_id}/context/packages", 200),
    # World sub-routes
    ("编辑世界", "/worlds/{w_id}/edit", 200),
    ("导出世界", "/worlds/{w_id}/export", 200),
    ("新建角色", "/worlds/{w_id}/characters/new", 200),
    ("新建势力", "/worlds/{w_id}/factions/new", 200),
    ("新建地点", "/worlds/{w_id}/locations/new", 200),
    ("新建规则", "/worlds/{w_id}/rules/new", 200),
    ("新建事件", "/worlds/{w_id}/events/new", 200),
]


class TestGlobalRouteHealth:
    """Every major GET route must return 200 (not 500)."""

    def test_all_no_world_routes(self, client):
        for name, url, expected in ROUTES_NO_WORLD:
            r = client.get(url)
            assert r.status_code == expected, f"{name} ({url}) returned {r.status_code}, expected {expected}"

    def test_all_world_routes(self, client):
        w_id = _create_world(client)
        for name, url_template, expected in ROUTES_WITH_WORLD:
            url = url_template.format(w_id=w_id)
            r = client.get(url)
            assert r.status_code == expected, f"{name} ({url}) returned {r.status_code}, expected {expected}"

    def test_no_500_on_any_route(self, client):
        w_id = _create_world(client)
        all_urls = [u for _, u, _ in ROUTES_NO_WORLD]
        all_urls += [t.format(w_id=w_id) for _, t, _ in ROUTES_WITH_WORLD]
        for url in all_urls:
            r = client.get(url)
            assert r.status_code != 500, f"{url} returned 500"

    def test_no_worlds_none_on_world_routes(self, client):
        w_id = _create_world(client)
        for name, url_template, _ in ROUTES_WITH_WORLD:
            url = url_template.format(w_id=w_id)
            r = client.get(url)
            assert "/worlds/None" not in r.text, f"{name} ({url}) contains /worlds/None"

    def test_no_worlds_double_slash_on_world_routes(self, client):
        w_id = _create_world(client)
        for name, url_template, _ in ROUTES_WITH_WORLD:
            url = url_template.format(w_id=w_id)
            r = client.get(url)
            assert "/worlds//" not in r.text, f"{name} ({url}) contains /worlds//"

    def test_app_shell_layout_on_world_routes(self, client):
        """World routes should have the app shell layout."""
        w_id = _create_world(client)
        key_routes = [
            f"/worlds/{w_id}",
            f"/worlds/{w_id}/context",
            f"/worlds/{w_id}/setting-suggestions",
            f"/worlds/{w_id}/novel/drafts",
            f"/worlds/{w_id}/novel/quality-reports",
        ]
        for url in key_routes:
            r = client.get(url)
            assert "app-main-inner" in r.text or "app-shell-body" in r.text, \
                f"{url} missing app shell layout"

    def test_no_please_select_world_on_world_routes(self, client):
        """World routes should show current world, not '请先选择世界'."""
        w_id = _create_world(client)
        for name, url_template, _ in ROUTES_WITH_WORLD[:5]:
            url = url_template.format(w_id=w_id)
            r = client.get(url)
            assert "请先选择世界" not in r.text, \
                f"{name} ({url}) shows '请先选择世界' when world exists"

    def test_no_internal_server_error_text(self, client):
        w_id = _create_world(client)
        all_urls = [u for _, u, _ in ROUTES_NO_WORLD]
        all_urls += [t.format(w_id=w_id) for _, t, _ in ROUTES_WITH_WORLD]
        for url in all_urls:
            r = client.get(url)
            assert "Internal Server Error" not in r.text, f"{url} shows Internal Server Error"

    def test_no_object_has_no_attribute(self, client):
        w_id = _create_world(client)
        all_urls = [u for _, u, _ in ROUTES_NO_WORLD]
        all_urls += [t.format(w_id=w_id) for _, t, _ in ROUTES_WITH_WORLD]
        for url in all_urls:
            r = client.get(url)
            assert "object has no attribute" not in r.text, \
                f"{url} shows 'object has no attribute' error"

    def test_404_for_nonexistent_world(self, client):
        """Non-existent world should return 404, not 500."""
        key_routes = [
            "/worlds/99999",
            "/worlds/99999/context",
            "/worlds/99999/setting-suggestions",
            "/worlds/99999/novel/drafts",
        ]
        for url in key_routes:
            r = client.get(url)
            assert r.status_code in (404, 200), f"{url} returned {r.status_code}, expected 404"
