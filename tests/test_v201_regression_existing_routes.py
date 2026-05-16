"""
v2.0.1 — Regression Tests for Existing Routes
验证所有旧路由继续可用。
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, init_db
from app.models import World


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_world():
    """Create a test world."""
    init_db()
    db = SessionLocal()
    try:
        world = World(name="回归测试世界", world_type="奇幻", description="测试")
        db.add(world)
        db.commit()
        db.refresh(world)
        return world.id
    finally:
        db.close()


class TestV201RegressionExistingRoutes:
    """验证 v2.0.1 所有旧路由继续可用。"""

    # ---- Top-level routes ----
    def test_route_home(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_route_worlds_list(self, client):
        resp = client.get("/worlds")
        assert resp.status_code == 200

    def test_route_worlds_new(self, client):
        resp = client.get("/worlds/new")
        assert resp.status_code == 200

    def test_route_data(self, client):
        resp = client.get("/data")
        assert resp.status_code == 200

    def test_route_data_export(self, client):
        resp = client.get("/data/export")
        assert resp.status_code == 200

    def test_route_settings_ai(self, client):
        resp = client.get("/settings/ai")
        assert resp.status_code == 200

    def test_route_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["version"] == "2.5.0"

    # ---- World-specific routes ----
    def test_route_world_detail(self, client, test_world):
        resp = client.get(f"/worlds/{test_world}")
        assert resp.status_code == 200

    def test_route_characters(self, client, test_world):
        resp = client.get(f"/worlds/{test_world}/characters")
        assert resp.status_code == 200

    def test_route_factions(self, client, test_world):
        resp = client.get(f"/worlds/{test_world}/factions")
        assert resp.status_code == 200

    def test_route_locations(self, client, test_world):
        resp = client.get(f"/worlds/{test_world}/locations")
        assert resp.status_code == 200

    def test_route_rules(self, client, test_world):
        resp = client.get(f"/worlds/{test_world}/rules")
        assert resp.status_code == 200

    def test_route_events(self, client, test_world):
        resp = client.get(f"/worlds/{test_world}/events")
        assert resp.status_code == 200

    def test_route_timeline(self, client, test_world):
        resp = client.get(f"/worlds/{test_world}/timeline")
        assert resp.status_code == 200

    def test_route_simulation(self, client, test_world):
        resp = client.get(f"/worlds/{test_world}/simulation")
        assert resp.status_code == 200

    def test_route_records(self, client, test_world):
        resp = client.get(f"/worlds/{test_world}/records")
        assert resp.status_code == 200

    def test_route_branches(self, client, test_world):
        resp = client.get(f"/worlds/{test_world}/branches")
        assert resp.status_code == 200

    def test_route_checks(self, client, test_world):
        resp = client.get(f"/worlds/{test_world}/checks")
        assert resp.status_code == 200

    def test_route_setting_suggestions(self, client, test_world):
        resp = client.get(f"/worlds/{test_world}/setting-suggestions")
        assert resp.status_code == 200

    # ---- Novel engineering routes ----
    def test_route_novel_overview(self, client, test_world):
        resp = client.get(f"/worlds/{test_world}/novel")
        assert resp.status_code == 200

    def test_route_novel_evolution(self, client, test_world):
        resp = client.get(f"/worlds/{test_world}/novel/evolution")
        assert resp.status_code == 200

    def test_route_novel_evolutions(self, client, test_world):
        resp = client.get(f"/worlds/{test_world}/novel/evolutions")
        assert resp.status_code == 200

    def test_route_volume_outlines(self, client, test_world):
        resp = client.get(f"/worlds/{test_world}/novel/volume-outlines")
        assert resp.status_code == 200

    def test_route_chapter_outlines(self, client, test_world):
        resp = client.get(f"/worlds/{test_world}/novel/chapter-outlines")
        assert resp.status_code == 200

    def test_route_novel_drafts(self, client, test_world):
        resp = client.get(f"/worlds/{test_world}/novel/drafts")
        assert resp.status_code == 200

    # ---- Context routes ----
    def test_route_context(self, client, test_world):
        resp = client.get(f"/worlds/{test_world}/context")
        assert resp.status_code == 200

    # ---- Settings routes ----
    def test_route_settings_center(self, client):
        resp = client.get("/settings/ai")
        assert resp.status_code == 200

    # ---- Data routes ----
    def test_route_data_import(self, client):
        resp = client.get("/data/import")
        assert resp.status_code == 200

    def test_route_data_backups(self, client):
        resp = client.get("/data/backups")
        assert resp.status_code == 200
