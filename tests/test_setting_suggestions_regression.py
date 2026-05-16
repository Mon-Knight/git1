"""
AI World Engine - v2.4.1 Setting Suggestions Regression Tests
Ensures the "设定库 AI 推演" module works after database migration fix.
"""

import re


def _create_world(client) -> int:
    """Helper: create a world and return its ID."""
    client.post("/worlds", data={"name": "RegressionWorld", "world_type": "Fantasy"}, follow_redirects=False)
    list_resp = client.get("/worlds")
    match = re.search(r'/worlds/(\d+)', list_resp.text)
    if match:
        return int(match.group(1))
    raise RuntimeError("No world ID found in world list")


class TestSettingSuggestionsRegression:
    """Regression tests for setting suggestions after v2.4.1 fix."""

    # ── Entry Point ──

    def test_world_console_has_setting_suggestion_entry(self, client):
        """世界控制台包含'设定库 AI 推演'入口."""
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}")
        assert resp.status_code == 200
        assert "设定库 AI 推演" in resp.text

    def test_entry_link_not_empty(self, client):
        """入口链接不为空."""
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}")
        assert f'/worlds/{w_id}/setting-suggestions' in resp.text

    def test_entry_link_no_worlds_none(self, client):
        """入口链接不包含 /worlds/None."""
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}")
        assert "/worlds/None" not in resp.text

    def test_entry_link_no_worlds_slash(self, client):
        """入口链接不包含 /worlds//."""
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}")
        assert "/worlds//setting-suggestions" not in resp.text

    # ── List Page ──

    def test_list_page_200(self, client):
        """GET 设定库 AI 推演首页返回 200."""
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}/setting-suggestions")
        assert resp.status_code == 200

    def test_list_page_has_title(self, client):
        """页面包含'设定库 AI 推演'."""
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}/setting-suggestions")
        assert "设定库 AI 推演" in resp.text

    def test_list_page_extends_base(self, client):
        """页面继承 base.html."""
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}/setting-suggestions")
        assert "app-main-inner" in resp.text or "app-shell-body" in resp.text

    def test_list_page_has_current_world(self, client):
        """页面传入 current_world 后左侧不显示'请先选择世界'."""
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}/setting-suggestions")
        assert "请先选择世界" not in resp.text

    def test_list_page_empty_state(self, client):
        """无候选设定时显示空状态."""
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}/setting-suggestions")
        assert "暂无候选记录" in resp.text

    # ── New Page ──

    def test_new_page_200(self, client):
        """新建候选页面返回 200."""
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}/setting-suggestions/new")
        assert resp.status_code == 200

    def test_new_page_has_form(self, client):
        """新建候选页面包含表单."""
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}/setting-suggestions/new")
        assert "suggestion_type" in resp.text

    # ── Create (POST) ──

    def test_post_create_redirects(self, client):
        """Mock 生成候选设定返回重定向."""
        w_id = _create_world(client)
        resp = client.post(
            f"/worlds/{w_id}/setting-suggestions",
            data={
                "suggestion_type": "character",
                "world_type": "western_fantasy",
                "reference_style": "heroic_epic",
                "generation_count": 2,
                "user_requirement": "",
            },
            follow_redirects=False,
        )
        assert resp.status_code == 303
        assert f"/worlds/{w_id}/setting-suggestions/" in resp.headers.get("location", "")

    # ── Detail Page ──

    def test_detail_page_200(self, client):
        """候选详情页返回 200."""
        w_id = _create_world(client)
        resp = client.post(
            f"/worlds/{w_id}/setting-suggestions",
            data={"suggestion_type": "character", "world_type": "western_fantasy",
                  "reference_style": "heroic_epic", "generation_count": 2, "user_requirement": ""},
            follow_redirects=True,
        )
        assert resp.status_code == 200
        assert "候选详情" in resp.text or "详情" in resp.text

    # ── Error Cases ──

    def test_nonexistent_world_404(self, client):
        """不存在 world_id 返回 404."""
        resp = client.get("/worlds/99999/setting-suggestions")
        assert resp.status_code == 404

    def test_nonexistent_suggestion_404(self, client):
        """不存在 candidate_id 返回 404."""
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}/setting-suggestions/99999")
        assert resp.status_code == 404

    def test_cross_world_suggestion_404(self, client):
        """跨世界访问候选详情返回 404."""
        w1 = _create_world(client)
        # Create a suggestion in world 1
        client.post(
            f"/worlds/{w1}/setting-suggestions",
            data={"suggestion_type": "character", "world_type": "western_fantasy",
                  "reference_style": "heroic_epic", "generation_count": 1, "user_requirement": ""},
            follow_redirects=False,
        )
        w2 = _create_world(client)
        # Access world1's suggestion from world2
        resp = client.get(f"/worlds/{w2}/setting-suggestions/1")
        assert resp.status_code == 404

    def test_no_worlds_none_in_page(self, client):
        """页面不生成 /worlds/None."""
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}/setting-suggestions")
        assert "/worlds/None" not in resp.text

    def test_no_worlds_slash_in_page(self, client):
        """页面不生成 /worlds//."""
        w_id = _create_world(client)
        resp = client.get(f"/worlds/{w_id}/setting-suggestions")
        assert "/worlds//" not in resp.text


class TestRegressionOtherModulesUnaffected:
    """Ensure the setting_suggestions fix does not break other modules."""

    def _create_world(self, client):
        return _create_world(client)

    def test_world_detail_still_200(self, client):
        """世界详情页仍返回 200."""
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}").status_code == 200

    def test_novel_draft_still_200(self, client):
        """正文草稿功能仍返回 200."""
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/novel/drafts").status_code == 200

    def test_quality_report_still_200(self, client):
        """正文质量检查功能仍返回 200."""
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/novel/quality-reports").status_code == 200

    def test_revision_still_200(self, client):
        """润色候选功能仍返回 200."""
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/novel/revisions").status_code == 200

    def test_version_still_200(self, client):
        """版本管理功能仍返回 200."""
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/novel/final-drafts").status_code == 200

    def test_final_draft_still_200(self, client):
        """最终采用稿功能仍返回 200."""
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/novel/final-drafts").status_code == 200

    def test_style_profile_still_200(self, client):
        """风格画像功能仍返回 200."""
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/context/styles").status_code == 200

    def test_context_index_still_200(self, client):
        """创作上下文页仍返回 200."""
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/context").status_code == 200

    def test_simulation_still_200(self, client):
        """AI 推演页仍返回 200."""
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/simulation").status_code == 200

    def test_checks_still_200(self, client):
        """检查中心页仍返回 200."""
        w_id = _create_world(client)
        assert client.get(f"/worlds/{w_id}/checks").status_code == 200

    def test_settings_still_200(self, client):
        """设置页仍返回 200."""
        assert client.get("/settings/ai").status_code == 200
