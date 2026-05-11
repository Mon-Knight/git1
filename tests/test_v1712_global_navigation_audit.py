"""
Tests for v1.7.12: Global navigation audit.
Verifies all main entry points are accessible and proper.
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


class TestMainEntries:
    def test_homepage_200(self):
        assert client.get("/").status_code == 200

    def test_worlds_list_200(self):
        assert client.get("/worlds").status_code == 200

    def test_new_world_200(self):
        assert client.get("/worlds/new").status_code == 200

    def test_data_management_200(self):
        assert client.get("/data").status_code == 200

    def test_settings_200(self):
        assert client.get("/settings/ai").status_code == 200

    def test_export_center_200(self):
        assert client.get("/data/export").status_code == 200


class TestNoWorldModuleDisabled:
    def test_no_none_world_id_homepage(self):
        resp = client.get("/")
        assert "/worlds/None" not in resp.text
        assert "/worlds//" not in resp.text

    def test_no_none_world_id_worlds(self):
        resp = client.get("/worlds")
        assert "/worlds/None" not in resp.text
        assert "/worlds//" not in resp.text

    def test_no_none_world_id_new(self):
        resp = client.get("/worlds/new")
        assert "/worlds/None" not in resp.text
        assert "/worlds//" not in resp.text

    def test_sidebar_modules_exist(self):
        resp = client.get("/")
        assert "世界控制台" in resp.text
        assert "AI 推演" in resp.text
        assert "创作资产" in resp.text
        assert "小说工程" in resp.text
        assert "检查中心" in resp.text

    def test_settings_nav_exists(self):
        resp = client.get("/")
        assert "设置" in resp.text
        assert "数据管理" in resp.text


class TestActiveNavHighlight:
    def test_dashboard_active(self):
        resp = client.get("/")
        assert 'data-nav="dashboard"' in resp.text

    def test_worlds_active(self):
        resp = client.get("/worlds")
        assert 'data-nav="worlds"' in resp.text

    def test_settings_active(self):
        resp = client.get("/settings/ai")
        assert 'data-nav="settings"' in resp.text

    def test_data_active(self):
        resp = client.get("/data")
        assert 'data-nav="data"' in resp.text
