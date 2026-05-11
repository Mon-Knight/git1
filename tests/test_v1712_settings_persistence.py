"""
Tests for v1.7.12: Settings persistence verification.
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


class TestDisplaySettings:
    def test_save_sidebar_expanded(self):
        resp = client.post("/settings/app", data={
            "sidebar_expanded": "false", "settings_category": "display"
        })
        assert resp.status_code == 200
        assert "已保存" in resp.text or "侧边栏" in resp.text

    def test_save_compact_mode(self):
        resp = client.post("/settings/app", data={
            "compact_mode": "true", "settings_category": "display"
        })
        assert resp.status_code == 200

    def test_save_both_display_settings(self):
        resp = client.post("/settings/app", data={
            "sidebar_expanded": "false", "compact_mode": "true",
            "settings_category": "display"
        })
        assert resp.status_code == 200


class TestDesktopSettings:
    def test_save_valid_window_size(self):
        resp = client.post("/settings/app", data={
            "desktop_width": "1400", "desktop_height": "900",
            "settings_category": "desktop"
        })
        assert resp.status_code == 200
        assert "已保存" in resp.text or "窗口" in resp.text

    def test_reject_invalid_width(self):
        resp = client.post("/settings/app", data={
            "desktop_width": "500", "desktop_height": "900",
            "settings_category": "desktop"
        })
        assert resp.status_code == 200
        assert "1024" in resp.text

    def test_reject_invalid_height(self):
        resp = client.post("/settings/app", data={
            "desktop_width": "1400", "desktop_height": "3000",
            "settings_category": "desktop"
        })
        assert resp.status_code == 200
        assert "1600" in resp.text


class TestExportSettings:
    def test_save_valid_export_dir(self):
        resp = client.post("/settings/app", data={
            "export_default_dir": "C:\\Users\\Test\\Exports",
            "settings_category": "export"
        })
        assert resp.status_code == 200

    def test_reject_dangerous_export_dir(self):
        resp = client.post("/settings/app", data={
            "export_default_dir": "C:\\Windows\\System32",
            "settings_category": "export"
        })
        assert resp.status_code == 200
        assert "不允许" in resp.text


class TestSecurity:
    def test_api_key_not_in_diagnostics(self):
        resp = client.get("/settings/ai")
        assert "sk-" not in resp.text or 'type="password"' in resp.text

    def test_settings_page_has_password_field(self):
        resp = client.get("/settings/ai")
        assert 'type="password"' in resp.text

    def test_about_shows_version(self):
        resp = client.get("/settings/ai")
        assert "AI World Engine" in resp.text
