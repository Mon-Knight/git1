"""
Tests for v1.7.12: Main flow smoke test.
Verifies the complete end-to-end user workflow.
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


class TestMainFlowSmoke:
    def test_create_world_flow(self):
        # Create world
        resp = client.post("/worlds", data={
            "name": "冒烟测试世界", "world_type": "奇幻",
            "description": "主流程冒烟测试", "current_era": "古代", "tone": "史诗"
        }, follow_redirects=False)
        assert resp.status_code in (303, 302)

        # Access world console
        resp = client.get("/worlds/1")
        assert resp.status_code == 200
        assert "冒烟测试世界" in resp.text

    def test_character_crud_flow(self):
        client.post("/worlds", data={"name": "角色测试", "world_type": "奇幻",
            "description": "测试", "current_era": "古代", "tone": "史诗"})

        # List
        assert client.get("/worlds/1/characters").status_code == 200
        # New form
        assert client.get("/worlds/1/characters/new").status_code == 200
        # Create
        resp = client.post("/worlds/1/characters", data={
            "name": "测试角色", "role": "战士",
        }, follow_redirects=False)
        assert resp.status_code in (303, 302)

    def test_faction_crud_flow(self):
        client.post("/worlds", data={"name": "势力测试", "world_type": "奇幻",
            "description": "测试", "current_era": "古代", "tone": "史诗"})

        assert client.get("/worlds/1/factions").status_code == 200
        assert client.get("/worlds/1/factions/new").status_code == 200
        resp = client.post("/worlds/1/factions", data={
            "name": "测试势力", "faction_type": "王国",
        }, follow_redirects=False)
        assert resp.status_code in (303, 302)

    def test_location_crud_flow(self):
        client.post("/worlds", data={"name": "地点测试", "world_type": "奇幻",
            "description": "测试", "current_era": "古代", "tone": "史诗"})

        assert client.get("/worlds/1/locations").status_code == 200
        assert client.get("/worlds/1/locations/new").status_code == 200
        resp = client.post("/worlds/1/locations", data={
            "name": "测试地点", "location_type": "城市",
        }, follow_redirects=False)
        assert resp.status_code in (303, 302)

    def test_rule_crud_flow(self):
        client.post("/worlds", data={"name": "规则测试", "world_type": "奇幻",
            "description": "测试", "current_era": "古代", "tone": "史诗"})

        assert client.get("/worlds/1/rules").status_code == 200
        assert client.get("/worlds/1/rules/new").status_code == 200
        resp = client.post("/worlds/1/rules", data={
            "name": "测试规则", "rule_type": "魔法规则",
        }, follow_redirects=False)
        assert resp.status_code in (303, 302)

    def test_ai_simulation_flow(self):
        client.post("/worlds", data={"name": "推演测试", "world_type": "奇幻",
            "description": "测试", "current_era": "古代", "tone": "史诗"})

        # Simulation page
        assert client.get("/worlds/1/simulation").status_code == 200
        # Run simulation
        resp = client.post("/worlds/1/simulation", data={
            "question": "测试推演问题",
        })
        assert resp.status_code in (200, 303, 302)

    def test_setting_suggestions_flow(self):
        client.post("/worlds", data={"name": "设定库测试", "world_type": "奇幻",
            "description": "测试", "current_era": "古代", "tone": "史诗"})

        # Suggestions list
        assert client.get("/worlds/1/setting-suggestions").status_code == 200
        # New suggestion form
        assert client.get("/worlds/1/setting-suggestions/new").status_code == 200

    def test_context_flow(self):
        client.post("/worlds", data={"name": "上下文测试", "world_type": "奇幻",
            "description": "测试", "current_era": "古代", "tone": "史诗"})

        assert client.get("/worlds/1/context").status_code == 200
        assert client.get("/worlds/1/context/styles").status_code == 200
        assert client.get("/worlds/1/context/anchors").status_code == 200
        assert client.get("/worlds/1/context/packages").status_code == 200

    def test_novel_engineering_flow(self):
        client.post("/worlds", data={"name": "小说工程测试", "world_type": "奇幻",
            "description": "测试", "current_era": "古代", "tone": "史诗"})

        assert client.get("/worlds/1/novel/evolution").status_code == 200
        assert client.get("/worlds/1/novel/evolutions").status_code == 200

    def test_checks_flow(self):
        client.post("/worlds", data={"name": "检查测试", "world_type": "奇幻",
            "description": "测试", "current_era": "古代", "tone": "史诗"})

        assert client.get("/worlds/1/checks").status_code == 200
        assert client.get("/worlds/1/checks/conflicts").status_code == 200
        assert client.get("/worlds/1/checks/behavior").status_code == 200

    def test_data_and_export_flow(self):
        assert client.get("/data").status_code == 200
        assert client.get("/data/export").status_code == 200

    def test_settings_flow(self):
        assert client.get("/settings/ai").status_code == 200
        # Save AI settings
        resp = client.post("/settings/ai", data={
            "ai_provider": "mock", "action": "save",
            "ai_temperature": "0.7", "ai_max_tokens": "2000", "ai_timeout": "60",
        })
        assert resp.status_code == 200
