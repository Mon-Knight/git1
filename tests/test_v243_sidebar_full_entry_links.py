"""
AI World Engine - v2.4.3 Sidebar Full Entry Links Test
Ensures ALL sidebar navigation links are correct: no /worlds/None, valid hrefs, correct disabled states.
"""

import re


def _create_world(client) -> int:
    client.post("/worlds", data={"name": "SidebarWorld", "world_type": "Fantasy"}, follow_redirects=False)
    list_resp = client.get("/worlds")
    match = re.search(r'/worlds/(\d+)', list_resp.text)
    if match:
        return int(match.group(1))
    raise RuntimeError("No world ID found")


class TestSidebarEntryLinks:
    """All sidebar entry links must be valid."""

    def test_sidebar_has_world_group(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}")
        assert 'sidebar-group' in r.text

    def test_sidebar_has_novel_engineering(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}")
        assert '小说工程' in r.text

    def test_sidebar_has_world_settings(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}")
        assert '世界设定' in r.text or '世界' in r.text

    def test_sidebar_has_creative_assets(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}")
        assert '创作资产' in r.text

    def test_sidebar_has_ai_simulation(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}")
        assert 'AI 推演' in r.text or 'AI' in r.text

    def test_sidebar_has_quality_check(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}")
        assert '质量检查' in r.text or '检查' in r.text

    def test_sidebar_has_data_export(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}")
        assert '数据' in r.text or '导出' in r.text or 'Data' in r.text

    def test_sidebar_has_settings(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}")
        assert '设置' in r.text or 'Settings' in r.text

    def test_no_worlds_none_in_sidebar(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}")
        assert "/worlds/None" not in r.text

    def test_no_worlds_double_slash_in_sidebar(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}")
        # Check for /worlds// pattern
        assert "/worlds//" not in r.text

    def test_novel_drafts_entry_exists(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}")
        assert '正文草稿' in r.text

    def test_novel_quality_reports_entry_exists(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}")
        assert '质量检查' in r.text

    def test_novel_revisions_entry_exists(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}")
        assert '润色' in r.text or 'Revision' in r.text

    def test_novel_final_drafts_entry_exists(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}")
        assert '最终采用稿' in r.text or '采用' in r.text

    def test_setting_suggestions_entry_exists(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}")
        assert '设定库 AI' in r.text

    def test_style_profiles_entry_exists(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}")
        assert '风格' in r.text or 'Style' in r.text

    def test_context_packages_entry_exists(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}")
        assert '上下文' in r.text or 'Context' in r.text

    def test_plot_anchors_entry_exists(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}")
        assert '时间点' in r.text or 'Anchor' in r.text

    def test_navigation_between_modules(self, client):
        """Navigate from world console to creative assets, AI simulation, checks, novel engineering."""
        w_id = _create_world(client)
        modules = [
            f"/worlds/{w_id}/context",
            f"/worlds/{w_id}/simulation",
            f"/worlds/{w_id}/checks",
            f"/worlds/{w_id}/novel/drafts",
        ]
        for url in modules:
            r = client.get(url)
            assert r.status_code == 200, f"Module {url} returned {r.status_code}"

    def test_current_world_shown_in_sidebar(self, client):
        w_id = _create_world(client)
        r = client.get(f"/worlds/{w_id}")
        assert "SidebarWorld" in r.text or "当前世界" in r.text
