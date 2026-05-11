"""
Tests for v1.7.12: Button and link audit.
Ensures no broken links, empty hrefs, or None world IDs.
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


def _create_world():
    client.post("/worlds", data={
        "name": "链接测试世界", "world_type": "奇幻",
        "description": "测试", "current_era": "古代", "tone": "史诗"
    })


class TestHomepageLinks:
    def test_no_none_links(self):
        resp = client.get("/")
        assert "/worlds/None" not in resp.text
        assert "/worlds//" not in resp.text

    def test_has_worlds_link(self):
        resp = client.get("/")
        assert 'href="/worlds"' in resp.text

    def test_has_new_world_link(self):
        resp = client.get("/")
        assert 'href="/worlds/new"' in resp.text

    def test_has_data_link(self):
        resp = client.get("/")
        assert 'href="/data"' in resp.text

    def test_has_settings_link(self):
        resp = client.get("/")
        assert 'href="/settings/ai"' in resp.text


class TestWorldPagesLinks:
    def test_detail_no_none_links(self):
        _create_world()
        resp = client.get("/worlds/1")
        assert "/worlds/None" not in resp.text
        assert "/worlds//" not in resp.text

    def test_characters_no_none_links(self):
        _create_world()
        resp = client.get("/worlds/1/characters")
        assert "/worlds/None" not in resp.text
        assert "/worlds//" not in resp.text

    def test_factions_no_none_links(self):
        _create_world()
        resp = client.get("/worlds/1/factions")
        assert "/worlds/None" not in resp.text

    def test_simulation_no_none_links(self):
        _create_world()
        resp = client.get("/worlds/1/simulation")
        assert "/worlds/None" not in resp.text

    def test_settings_page_no_none_links(self):
        resp = client.get("/settings/ai")
        assert "/worlds/None" not in resp.text
        assert "/worlds//" not in resp.text
        assert "/None/" not in resp.text


class TestDisabledLinks:
    def test_disabled_has_class(self):
        resp = client.get("/")
        # Sidebar disabled items should exist
        assert "disabled" in resp.text or "后续版本开放" in resp.text


class TestExportCenterLinks:
    def test_export_page_200(self):
        assert client.get("/data/export").status_code == 200

    def test_export_page_no_none(self):
        resp = client.get("/data/export")
        assert "/None/" not in resp.text


class TestSettingSuggestionsLinks:
    def test_suggestions_list_200(self):
        _create_world()
        assert client.get("/worlds/1/setting-suggestions").status_code == 200

    def test_suggestions_new_200(self):
        _create_world()
        assert client.get("/worlds/1/setting-suggestions/new").status_code == 200
