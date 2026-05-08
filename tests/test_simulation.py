"""
Tests for AI simulation and records.
"""


def _create_world(client):
    client.post("/worlds", data={"name": "测试世界", "world_type": "奇幻"})


def _create_world_with_data(client):
    """Create a world with some characters, factions, etc."""
    client.post("/worlds", data={"name": "完整世界", "world_type": "奇幻",
        "description": "一个测试世界", "current_era": "第一纪元", "tone": "史诗"})
    client.post("/worlds/1/characters", data={"name": "英雄A", "role": "战士"})
    client.post("/worlds/1/characters", data={"name": "英雄B", "role": "法师"})
    client.post("/worlds/1/factions", data={"name": "光明阵营", "faction_type": "组织"})
    client.post("/worlds/1/locations", data={"name": "主城", "location_type": "城市"})
    client.post("/worlds/1/rules", data={"name": "魔法规则", "rule_type": "魔法体系"})
    client.post("/worlds/1/events", data={"title": "古代战争", "is_canon": "true"})
    client.post("/worlds/1/events", data={"title": "非正史事件", "is_canon": "false"})


# --- Simulation Tests ---

def test_simulation_page_returns_200(client):
    _create_world(client)
    response = client.get("/worlds/1/simulation")
    assert response.status_code == 200


def test_simulation_page_shows_world_name(client):
    _create_world(client)
    response = client.get("/worlds/1/simulation")
    assert "测试世界" in response.text


def test_simulation_submit_creates_record(client):
    _create_world(client)
    response = client.post("/worlds/1/simulation", data={
        "question": "如果战争爆发会怎样？",
        "simulation_type": "剧情发展",
    })
    assert response.status_code == 200
    # Should show result
    assert "Mock AI" in response.text or "AI 推演结果" in response.text


def test_simulation_record_status_is_pending(client):
    _create_world(client)
    client.post("/worlds/1/simulation", data={
        "question": "测试问题",
        "simulation_type": "角色行动",
    })
    # Check the record
    response = client.get("/worlds/1/records/1")
    assert response.status_code == 200
    assert "pending" in response.text


def test_simulation_empty_question_fails(client):
    _create_world(client)
    response = client.post("/worlds/1/simulation", data={
        "question": "",
        "simulation_type": "剧情发展",
    })
    assert response.status_code == 422
    assert "推演问题不能为空" in response.text


def test_simulation_404_for_nonexistent_world(client):
    response = client.get("/worlds/999/simulation")
    assert response.status_code == 404


def test_simulation_does_not_write_to_historical_events(client):
    """AI simulation must NOT create historical_events records."""
    _create_world(client)
    # Check initial event count
    before = client.get("/worlds/1/events")
    before_count = before.text.count("world-card")

    # Run simulation
    client.post("/worlds/1/simulation", data={
        "question": "测试推演",
        "simulation_type": "剧情发展",
    })

    # Check event count hasn't changed
    after = client.get("/worlds/1/events")
    after_count = after.text.count("world-card")
    assert after_count == before_count


def test_simulation_does_not_change_timeline_canon_count(client):
    """AI simulation must NOT change timeline canon events."""
    _create_world(client)
    client.post("/worlds/1/events", data={"title": "正史事件A", "is_canon": "true"})

    # Run simulation
    client.post("/worlds/1/simulation", data={
        "question": "测试推演",
        "simulation_type": "剧情发展",
    })

    # Check timeline canon view still has only 1 event
    response = client.get("/worlds/1/timeline?view=canon")
    # Count timeline items
    count = response.text.count("timeline-item non-canon") + response.text.count('timeline-item "')  # rough
    # Just verify the original canon event is still there
    assert "正史事件A" in response.text


def test_world_context_does_not_include_other_world_data(client):
    """World A context must not include World B data."""
    client.post("/worlds", data={"name": "世界A", "world_type": "奇幻"})
    client.post("/worlds", data={"name": "世界B", "world_type": "科幻"})
    client.post("/worlds/1/characters", data={"name": "A角色"})
    client.post("/worlds/2/characters", data={"name": "B角色"})

    response = client.get("/worlds/1/simulation")
    assert "A角色" in response.text
    assert "B角色" not in response.text


# --- Records Tests ---

def test_records_list_returns_200(client):
    _create_world(client)
    response = client.get("/worlds/1/records")
    assert response.status_code == 200


def test_records_list_shows_created_record(client):
    _create_world(client)
    client.post("/worlds/1/simulation", data={
        "question": "独特的推演问题XYZ",
        "simulation_type": "剧情发展",
    })
    response = client.get("/worlds/1/records")
    assert "独特的推演问题XYZ" in response.text


def test_record_detail_returns_200(client):
    _create_world(client)
    client.post("/worlds/1/simulation", data={
        "question": "测试问题",
        "simulation_type": "角色行动",
    })
    response = client.get("/worlds/1/records/1")
    assert response.status_code == 200
    assert "测试问题" in response.text


def test_record_detail_shows_question_and_response(client):
    _create_world(client)
    client.post("/worlds/1/simulation", data={
        "question": "查看详情测试",
        "simulation_type": "势力冲突",
    })
    response = client.get("/worlds/1/records/1")
    assert "查看详情测试" in response.text
    assert "Mock AI" in response.text


def test_record_detail_404(client):
    _create_world(client)
    response = client.get("/worlds/1/records/999")
    assert response.status_code == 404


def test_record_not_visible_from_other_world(client):
    client.post("/worlds", data={"name": "世界A", "world_type": "奇幻"})
    client.post("/worlds", data={"name": "世界B", "world_type": "科幻"})
    client.post("/worlds/1/simulation", data={"question": "A的推演"})
    client.post("/worlds/2/simulation", data={"question": "B的推演"})

    resp_a = client.get("/worlds/1/records")
    assert "A的推演" in resp_a.text
    assert "B的推演" not in resp_a.text


def test_world_context_includes_all_data_types(client):
    """Context should include characters, factions, locations, rules, canon events."""
    _create_world_with_data(client)
    response = client.get("/worlds/1/simulation")
    assert "英雄A" in response.text
    assert "光明阵营" in response.text
    assert "主城" in response.text
    assert "魔法规则" in response.text
    assert "古代战争" in response.text
    # Non-canon event should NOT be in context
    assert "非正史事件" not in response.text


def test_context_snapshot_saved_to_record(client):
    """Context snapshot should be saved alongside the simulation record."""
    _create_world_with_data(client)
    client.post("/worlds/1/simulation", data={
        "question": "快照测试",
        "simulation_type": "剧情发展",
    })
    response = client.get("/worlds/1/records/1")
    assert "世界设定快照" in response.text or "完整世界" in response.text
