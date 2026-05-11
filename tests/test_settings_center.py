"""
AI World Engine - Test Settings Center
Tests for v1.7.9.1 settings center with 7 categories.
"""


class TestSettingsCenterPage:
    """Tests for the settings center page."""

    def test_page_returns_200(self, client):
        assert client.get("/settings/ai").status_code == 200

    def test_page_has_settings_center_title(self, client):
        resp = client.get("/settings/ai")
        assert "设置中心" in resp.text

    def test_page_has_app_shell(self, client):
        resp = client.get("/settings/ai")
        assert "app-main-inner" in resp.text or "app-shell-body" in resp.text

    def test_page_has_ai_model_section(self, client):
        resp = client.get("/settings/ai")
        assert "AI 模型设置" in resp.text

    def test_page_has_desktop_section(self, client):
        resp = client.get("/settings/ai")
        assert "桌面端设置" in resp.text

    def test_page_has_display_section(self, client):
        resp = client.get("/settings/ai")
        assert "界面显示" in resp.text

    def test_page_has_storage_section(self, client):
        resp = client.get("/settings/ai")
        assert "数据与存储" in resp.text

    def test_page_has_export_section(self, client):
        resp = client.get("/settings/ai")
        assert "导出设置" in resp.text

    def test_page_has_diagnostics_section(self, client):
        resp = client.get("/settings/ai")
        assert "日志与诊断" in resp.text

    def test_page_has_about_section(self, client):
        resp = client.get("/settings/ai")
        assert "关于软件" in resp.text

    def test_page_has_api_base_url_field(self, client):
        resp = client.get("/settings/ai")
        assert "ai_base_url" in resp.text or "Base URL" in resp.text

    def test_page_has_api_key_field(self, client):
        resp = client.get("/settings/ai")
        assert "ai_api_key" in resp.text or "API Key" in resp.text

    def test_page_has_model_field(self, client):
        resp = client.get("/settings/ai")
        assert "ai_model" in resp.text or "Model" in resp.text

    def test_page_has_mock_mode(self, client):
        resp = client.get("/settings/ai")
        assert "Mock" in resp.text

    def test_page_has_version(self, client):
        resp = client.get("/settings/ai")
        assert "v1.7.9.1" in resp.text

    def test_page_has_future_version_hint(self, client):
        resp = client.get("/settings/ai")
        assert "后续版本开放" in resp.text or "后续开放" in resp.text

    def test_page_no_plain_api_key(self, client):
        """API Key should be in password field, not plain text visible."""
        resp = client.get("/settings/ai")
        assert 'type="password"' in resp.text

    def test_page_settings_nav_highlighted(self, client):
        resp = client.get("/settings/ai")
        assert 'data-nav="settings"' in resp.text

    def test_page_no_none_links(self, client):
        resp = client.get("/settings/ai")
        assert "/None/" not in resp.text

    def test_page_has_export_center_link(self, client):
        resp = client.get("/settings/ai")
        assert "/data/export" in resp.text

    def test_page_has_data_link(self, client):
        resp = client.get("/settings/ai")
        assert "/data" in resp.text

    def test_page_save_form_exists(self, client):
        resp = client.get("/settings/ai")
        assert 'action="/settings/ai"' in resp.text
        assert 'method="post"' in resp.text
