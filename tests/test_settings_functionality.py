"""
Tests for v1.7.11.3: Settings center functionality.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield


class TestSettingsPage:
    def test_settings_returns_200(self):
        assert client.get("/settings/ai").status_code == 200

    def test_settings_has_display_form(self):
        resp = client.get("/settings/ai")
        assert 'name="sidebar_expanded"' in resp.text
        assert 'name="compact_mode"' in resp.text

    def test_settings_has_desktop_form(self):
        resp = client.get("/settings/ai")
        assert 'name="desktop_width"' in resp.text
        assert 'name="desktop_height"' in resp.text

    def test_settings_has_export_form(self):
        resp = client.get("/settings/ai")
        assert 'name="export_default_dir"' in resp.text

    def test_settings_has_diagnostics(self):
        resp = client.get("/settings/ai")
        assert "copyDiagnostics" in resp.text or "复制诊断" in resp.text

    def test_settings_has_about(self):
        resp = client.get("/settings/ai")
        assert "关于 AI World Engine" in resp.text

    def test_api_key_not_plain_text(self):
        resp = client.get("/settings/ai")
        assert 'type="password"' in resp.text


class TestAppSettingsSave:
    def test_save_sidebar_expanded(self):
        resp = client.post("/settings/app", data={
            "sidebar_expanded": "false",
            "settings_category": "display"
        })
        assert resp.status_code == 200

    def test_save_compact_mode(self):
        resp = client.post("/settings/app", data={
            "compact_mode": "true",
            "settings_category": "display"
        })
        assert resp.status_code == 200

    def test_save_desktop_size_valid(self):
        resp = client.post("/settings/app", data={
            "desktop_width": "1400",
            "desktop_height": "900",
            "settings_category": "desktop"
        })
        assert resp.status_code == 200

    def test_save_desktop_size_invalid_width(self):
        resp = client.post("/settings/app", data={
            "desktop_width": "500",
            "desktop_height": "900",
            "settings_category": "desktop"
        })
        assert resp.status_code == 200
        assert "1024" in resp.text

    def test_save_desktop_size_invalid_height(self):
        resp = client.post("/settings/app", data={
            "desktop_width": "1400",
            "desktop_height": "50",
            "settings_category": "desktop"
        })
        assert resp.status_code == 200
        assert "700" in resp.text

    def test_save_export_dir_valid(self):
        resp = client.post("/settings/app", data={
            "export_default_dir": "C:\\Users\\Test\\Exports",
            "settings_category": "export"
        })
        assert resp.status_code == 200

    def test_save_export_dir_dangerous_rejected(self):
        resp = client.post("/settings/app", data={
            "export_default_dir": "C:\\Windows\\System32",
            "settings_category": "export"
        })
        assert resp.status_code == 200
        assert "不允许" in resp.text
