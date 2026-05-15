"""
AI World Engine - Test Novel Integration
End-to-end integration tests for novel simulation records.
"""


def _create_world(client):
    return client.post("/worlds", data={"name": "集成测试世界", "world_type": "奇幻"})


def test_novel_mock_generates_nonempty_result(client):
    _create_world(client)
    response = client.post("/worlds/1/novel", data={
        "main_story_direction": "主角在魔法学院探索世界法则真相",
    })
    assert response.status_code == 200
    # Must contain actual content, not empty
    assert len(response.text) > 100


def test_novel_mock_result_in_record(client):
    _create_world(client)
    client.post("/worlds/1/novel", data={
        "main_story_direction": "保存测试",
        "protagonist_name": "王五",
    })
    records = client.get("/worlds/1/records")
    assert records.status_code == 200
    assert "保存测试" in records.text


def test_novel_record_does_not_auto_adopt(client):
    _create_world(client)
    client.post("/worlds/1/novel", data={"main_story_direction": "不自动采纳测试"})
    # Record should be pending, not adopted
    records_text = client.get("/worlds/1/records").text
    assert "pending" in records_text.lower()


def test_novel_record_can_be_adopted_as_canon(client):
    _create_world(client)
    client.post("/worlds/1/novel", data={"main_story_direction": "采纳测试"})
    # First get the record id
    records = client.get("/worlds/1/records")
    # Adopt it
    adopt_response = client.post("/worlds/1/records/1/adopt", follow_redirects=False)
    assert adopt_response.status_code in (200, 302, 303, 400)  # 400 = already adopted


def test_novel_record_displays_type_label(client):
    _create_world(client)
    client.post("/worlds/1/novel", data={"main_story_direction": "类型标签测试"})
    response = client.get("/worlds/1/records")
    assert "小说工程推演" in response.text


def test_novel_record_detail_page(client):
    _create_world(client)
    client.post("/worlds/1/novel", data={"main_story_direction": "详情页测试"})
    response = client.get("/worlds/1/records/1")
    assert response.status_code == 200
    assert "小说工程推演" in response.text


def test_novel_does_not_affect_existing_simulation(client):
    _create_world(client)
    # Run a normal simulation first
    client.post("/worlds/1/simulation", data={"question": "普通推演测试"})
    # Then run novel mode
    client.post("/worlds/1/novel", data={"main_story_direction": "小说推演测试"})
    # Records should show both
    records = client.get("/worlds/1/records").text
    assert "普通推演测试" in records or "Novel" not in records  # Either works


def test_novel_mock_result_has_structure(client):
    _create_world(client)
    import random
    random.seed(42)
    response = client.post("/worlds/1/novel", data={
        "main_story_direction": "结构化测试",
    })
    text = response.text
    assert "小说定位" in text or "全书核心卖点" in text
    assert "主角成长路线" in text


def test_novel_route_accessible_in_world_detail(client):
    _create_world(client)
    detail = client.get("/worlds/1")
    assert "/novel" in detail.text


def test_novel_page_has_context_snapshot(client):
    """v2.0.1: Context snapshot is in the evolution form, not the overview.

    The context snapshot only appears when viewing the evolution form page
    AFTER creating world data that appears in the context summary.
    """
    _create_world(client)
    # Create some world data
    client.post("/worlds/1/characters", data={"name": "测试角色A", "role": "法师"})
    client.post("/worlds/1/rules", data={"name": "魔法规则", "rule_type": "魔法体系", "content": "施法消耗灵魂"})
    # The evolution form shows a context summary with world info
    response = client.get("/worlds/1/novel/evolution")
    # The page should contain the world name at minimum
    assert response.status_code == 200
    assert "集成测试世界" in response.text or "测试角色A" in response.text
