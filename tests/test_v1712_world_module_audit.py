"""
Tests for v1.7.12: World module page audit.
Verifies all world-internal module pages are accessible.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.services.world_service import WorldService

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield


def _create_world():
    client.post("/worlds", data={
        "name": "审计测试世界", "world_type": "奇幻",
        "description": "审计", "current_era": "古代", "tone": "史诗"
    })


class TestWorldPages200:
    def test_world_detail_200(self):
        _create_world()
        assert client.get("/worlds/1").status_code == 200

    def test_characters_list_200(self):
        _create_world()
        assert client.get("/worlds/1/characters").status_code == 200

    def test_characters_new_200(self):
        _create_world()
        assert client.get("/worlds/1/characters/new").status_code == 200

    def test_factions_list_200(self):
        _create_world()
        assert client.get("/worlds/1/factions").status_code == 200

    def test_factions_new_200(self):
        _create_world()
        assert client.get("/worlds/1/factions/new").status_code == 200

    def test_locations_list_200(self):
        _create_world()
        assert client.get("/worlds/1/locations").status_code == 200

    def test_locations_new_200(self):
        _create_world()
        assert client.get("/worlds/1/locations/new").status_code == 200

    def test_rules_list_200(self):
        _create_world()
        assert client.get("/worlds/1/rules").status_code == 200

    def test_rules_new_200(self):
        _create_world()
        assert client.get("/worlds/1/rules/new").status_code == 200

    def test_events_list_200(self):
        _create_world()
        assert client.get("/worlds/1/events").status_code == 200

    def test_events_new_200(self):
        _create_world()
        assert client.get("/worlds/1/events/new").status_code == 200

    def test_timeline_200(self):
        _create_world()
        assert client.get("/worlds/1/timeline").status_code == 200

    def test_simulation_200(self):
        _create_world()
        assert client.get("/worlds/1/simulation").status_code == 200

    def test_records_list_200(self):
        _create_world()
        assert client.get("/worlds/1/records").status_code == 200

    def test_branches_200(self):
        _create_world()
        assert client.get("/worlds/1/branches").status_code == 200

    def test_context_200(self):
        _create_world()
        assert client.get("/worlds/1/context").status_code == 200

    def test_context_styles_200(self):
        _create_world()
        assert client.get("/worlds/1/context/styles").status_code == 200

    def test_context_anchors_200(self):
        _create_world()
        assert client.get("/worlds/1/context/anchors").status_code == 200

    def test_context_packages_200(self):
        _create_world()
        assert client.get("/worlds/1/context/packages").status_code == 200

    def test_novel_evolution_200(self):
        _create_world()
        assert client.get("/worlds/1/novel/evolution").status_code == 200

    def test_novel_evolutions_200(self):
        _create_world()
        assert client.get("/worlds/1/novel/evolutions").status_code == 200

    def test_checks_index_200(self):
        _create_world()
        assert client.get("/worlds/1/checks").status_code == 200

    def test_checks_conflicts_200(self):
        _create_world()
        assert client.get("/worlds/1/checks/conflicts").status_code == 200

    def test_checks_behavior_200(self):
        _create_world()
        assert client.get("/worlds/1/checks/behavior").status_code == 200

    def test_setting_suggestions_200(self):
        _create_world()
        assert client.get("/worlds/1/setting-suggestions").status_code == 200

    def test_setting_suggestions_new_200(self):
        _create_world()
        assert client.get("/worlds/1/setting-suggestions/new").status_code == 200

    def test_world_edit_200(self):
        _create_world()
        assert client.get("/worlds/1/edit").status_code == 200


class TestNoNoneLinks:
    def test_no_none_in_world_pages(self):
        _create_world()
        pages = [
            "/worlds/1", "/worlds/1/characters", "/worlds/1/factions",
            "/worlds/1/locations", "/worlds/1/rules", "/worlds/1/events",
            "/worlds/1/timeline", "/worlds/1/simulation", "/worlds/1/records",
            "/worlds/1/branches", "/worlds/1/context", "/worlds/1/checks",
            "/worlds/1/novel/evolution", "/worlds/1/setting-suggestions",
        ]
        for page in pages:
            resp = client.get(page)
            assert "/worlds/None" not in resp.text, f"{page} contains /worlds/None"
            assert "/worlds//" not in resp.text, f"{page} contains /worlds//"
