"""
Tests for v1.7.11.3: Homepage current world module switching.
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


class TestHomepageNoWorld:
    def test_no_world_shows_placeholder(self):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "请先创建或选择" in resp.text

    def test_no_world_has_world_list_button(self):
        resp = client.get("/")
        assert "/worlds" in resp.text

    def test_no_world_has_new_world_button(self):
        resp = client.get("/")
        assert "/worlds/new" in resp.text

    def test_no_world_no_none_links(self):
        resp = client.get("/")
        assert "/worlds/None" not in resp.text
        assert "/worlds//" not in resp.text


class TestHomepageStructure:
    """Tests that verify homepage template structure for world module switching."""

    def test_homepage_has_quick_actions(self):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "快捷操作" in resp.text

    def test_homepage_has_world_section(self):
        resp = client.get("/")
        assert resp.status_code == 200
        assert ("当前世界" in resp.text or "请先创建" in resp.text)

    def test_homepage_no_none_links(self):
        resp = client.get("/")
        assert "/worlds/None" not in resp.text
        assert "/worlds//" not in resp.text

    def test_homepage_sidebar_has_world_modules(self):
        resp = client.get("/")
        assert "世界控制台" in resp.text
        assert "AI 推演" in resp.text
        assert "创作资产" in resp.text
        assert "小说工程" in resp.text
        assert "检查中心" in resp.text
