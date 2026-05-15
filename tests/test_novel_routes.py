"""
AI World Engine - Test Novel Routes
Tests for /worlds/{id}/novel GET and POST.
"""


def _create_world(client):
    return client.post("/worlds", data={"name": "小说测试世界", "world_type": "奇幻"})


def test_novel_form_returns_200(client):
    _create_world(client)
    response = client.get("/worlds/1/novel")
    assert response.status_code == 200


def test_novel_form_contains_title(client):
    """v2.0.1: GET /novel now renders overview page."""
    _create_world(client)
    response = client.get("/worlds/1/novel")
    assert "小说工程总览" in response.text


def test_novel_form_contains_button(client):
    """v2.0.1: Overview page has quick action links."""
    _create_world(client)
    response = client.get("/worlds/1/novel")
    # Overview page should have navigation links to sub-modules
    assert "全书演化" in response.text


def test_novel_form_contains_fields(client):
    """v2.0.1: Overview page shows status cards, evolution form is at /evolution."""
    _create_world(client)
    response = client.get("/worlds/1/novel")
    # Overview shows status, not form fields
    assert "小说工程总览" in response.text or "未开始" in response.text


def test_novel_form_404_for_nonexistent_world(client):
    response = client.get("/worlds/999/novel")
    assert response.status_code == 404


def test_novel_post_without_direction_shows_error(client):
    _create_world(client)
    response = client.post("/worlds/1/novel", data={
        "main_story_direction": "",
    })
    assert response.status_code == 422
    assert "不能为空" in response.text


def test_novel_post_success_creates_record(client):
    _create_world(client)
    response = client.post("/worlds/1/novel", data={
        "main_story_direction": "主角在魔法学院探索AI系统与世界法则的关系",
        "protagonist_name": "林楚",
        "writing_style": "理性克制",
    })
    assert response.status_code == 200
    assert "小说工程推演" in response.text or "novel_evolution" in response.text or "全书演化方向" in response.text


def test_novel_post_simulation_type_is_novel_evolution(client):
    _create_world(client)
    client.post("/worlds/1/novel", data={
        "main_story_direction": "主角在魔法学院探索AI系统",
    })
    records = client.get("/worlds/1/records")
    assert "novel_evolution" in records.text or "小说工程推演" in records.text


def test_novel_post_does_not_create_historical_event(client):
    _create_world(client)
    events_before = client.get("/worlds/1/events")
    client.post("/worlds/1/novel", data={
        "main_story_direction": "安全测试",
    })
    events_after = client.get("/worlds/1/events")
    # No new canon events should be created
    assert events_before.text.count("block") == events_after.text.count("block")


def test_novel_page_shows_ai_mode(client):
    """v2.0.1: AI mode info is shown on the evolution form page."""
    _create_world(client)
    response = client.get("/worlds/1/novel/evolution")
    assert "Mock AI" in response.text or "mock" in response.text.lower()


def test_novel_page_shows_world_info(client):
    _create_world(client)
    response = client.get("/worlds/1/novel")
    assert "小说测试世界" in response.text


def test_world_detail_has_novel_entry(client):
    _create_world(client)
    response = client.get("/worlds/1")
    assert "/novel" in response.text
    assert "全书演化" in response.text


def test_novel_post_with_all_optional_fields(client):
    _create_world(client)
    response = client.post("/worlds/1/novel", data={
        "main_story_direction": "完整的测试主线",
        "protagonist_name": "张三",
        "protagonist_identity": "穿越者",
        "protagonist_power": "AI辅助系统",
        "protagonist_start": "出生在边陲小镇",
        "core_conflict": "传统vs创新",
        "genre": "领主建设",
        "target_word_count": "100万字",
        "volume_count": "5卷",
        "writing_style": "设定严谨",
        "pacing_preference": "前期成长，后期决战",
        "conflict_density": "中等",
        "dialogue_ratio": "中等对话比例",
        "description_density": "描写适中",
        "information_release": "通过历史遗迹逐步揭示",
        "banned_patterns": "不要无脑爽文",
        "extra_requirements": "保留法师神秘感",
    })
    assert response.status_code == 200
