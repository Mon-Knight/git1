"""
Tests for v1.7.11.3: New world page adaptation to desktop software style.
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


class TestNewWorldPage:
    def test_page_returns_200(self):
        assert client.get("/worlds/new").status_code == 200

    def test_page_extends_base(self):
        resp = client.get("/worlds/new")
        assert "app-shell-body" in resp.text
        assert "sidebar" in resp.text

    def test_page_has_app_main_inner(self):
        resp = client.get("/worlds/new")
        assert "app-main-inner" in resp.text

    def test_page_has_page_form_class(self):
        resp = client.get("/worlds/new")
        assert "page-form" in resp.text

    def test_page_title_is_new_world(self):
        resp = client.get("/worlds/new")
        assert "新建世界" in resp.text

    def test_page_has_card_layout(self):
        resp = client.get("/worlds/new")
        assert "new-world-card" in resp.text

    def test_page_has_form_fields(self):
        resp = client.get("/worlds/new")
        assert 'name="name"' in resp.text
        assert 'name="world_type"' in resp.text
        assert 'name="description"' in resp.text
        assert 'name="current_era"' in resp.text
        assert 'name="tone"' in resp.text

    def test_page_has_submit_button(self):
        resp = client.get("/worlds/new")
        assert 'type="submit"' in resp.text

    def test_page_no_none_world_id(self):
        resp = client.get("/worlds/new")
        assert "/worlds/None" not in resp.text
        assert "/worlds//" not in resp.text

    def test_page_has_back_link(self):
        resp = client.get("/worlds/new")
        assert "/worlds" in resp.text
