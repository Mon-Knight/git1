"""
Tests for polish: navigation, error pages, empty states, and cross-world isolation.
"""


def _create_world(client):
    client.post("/worlds", data={"name": "测试世界", "world_type": "奇幻"})


# --- Navigation Tests ---

def test_home_page_has_world_list_link(client):
    response = client.get("/")
    assert 'href="/worlds"' in response.text


def test_world_list_has_create_link(client):
    _create_world(client)
    response = client.get("/worlds")
    assert 'href="/worlds/new"' in response.text


def test_world_detail_has_all_module_links(client):
    _create_world(client)
    response = client.get("/worlds/1")
    modules = [
        "/characters", "/factions", "/locations", "/rules",
        "/events", "/timeline", "/simulation", "/records",
        "/branches", "/checks",
    ]
    for mod in modules:
        assert f'href="/worlds/1{mod}"' in response.text, f"Missing link: {mod}"


def test_character_list_has_back_to_world(client):
    _create_world(client)
    response = client.get("/worlds/1/characters")
    assert 'href="/worlds/1"' in response.text


def test_faction_list_has_back_to_world(client):
    _create_world(client)
    response = client.get("/worlds/1/factions")
    assert 'href="/worlds/1"' in response.text


def test_location_list_has_back_to_world(client):
    _create_world(client)
    response = client.get("/worlds/1/locations")
    assert 'href="/worlds/1"' in response.text


def test_rules_list_has_back_to_world(client):
    _create_world(client)
    response = client.get("/worlds/1/rules")
    assert 'href="/worlds/1"' in response.text


def test_events_list_has_back_to_world(client):
    _create_world(client)
    response = client.get("/worlds/1/events")
    assert 'href="/worlds/1"' in response.text


def test_timeline_has_back_to_world(client):
    _create_world(client)
    response = client.get("/worlds/1/timeline")
    assert 'href="/worlds/1"' in response.text


def test_simulation_has_back_to_world(client):
    _create_world(client)
    response = client.get("/worlds/1/simulation")
    assert 'href="/worlds/1"' in response.text


def test_records_list_has_back_to_world(client):
    _create_world(client)
    response = client.get("/worlds/1/records")
    assert 'href="/worlds/1"' in response.text


def test_branches_list_has_back_to_world(client):
    _create_world(client)
    response = client.get("/worlds/1/branches")
    assert 'href="/worlds/1"' in response.text


def test_checks_index_has_back_to_world(client):
    _create_world(client)
    response = client.get("/worlds/1/checks")
    assert 'href="/worlds/1"' in response.text


# --- Error Page Tests ---

def test_world_404_shows_message(client):
    response = client.get("/worlds/999")
    assert response.status_code == 404
    assert "世界不存在" in response.text or "未找到" in response.text


def test_character_404_shows_message(client):
    _create_world(client)
    response = client.get("/worlds/1/characters/999")
    assert response.status_code == 404


def test_faction_404_shows_message(client):
    _create_world(client)
    response = client.get("/worlds/1/factions/999")
    assert response.status_code == 404


def test_location_404_shows_message(client):
    _create_world(client)
    response = client.get("/worlds/1/locations/999")
    assert response.status_code == 404


def test_rule_404_shows_message(client):
    _create_world(client)
    response = client.get("/worlds/1/rules/999")
    assert response.status_code == 404


def test_event_404_shows_message(client):
    _create_world(client)
    response = client.get("/worlds/1/events/999")
    assert response.status_code == 404


def test_record_404_shows_message(client):
    _create_world(client)
    response = client.get("/worlds/1/records/999")
    assert response.status_code == 404


def test_branch_404_shows_message(client):
    _create_world(client)
    response = client.get("/worlds/1/branches/999")
    assert response.status_code == 404


# --- Empty State Tests ---

def test_empty_world_list_shows_message(client):
    response = client.get("/worlds")
    assert "还没有任何世界" in response.text


def test_empty_character_list_shows_message(client):
    _create_world(client)
    response = client.get("/worlds/1/characters")
    assert "还没有角色" in response.text


def test_empty_faction_list_shows_message(client):
    _create_world(client)
    response = client.get("/worlds/1/factions")
    assert "还没有势力" in response.text


def test_empty_location_list_shows_message(client):
    _create_world(client)
    response = client.get("/worlds/1/locations")
    assert "还没有地点" in response.text


def test_empty_rules_list_shows_message(client):
    _create_world(client)
    response = client.get("/worlds/1/rules")
    assert "还没有规则" in response.text


def test_empty_events_list_shows_message(client):
    _create_world(client)
    response = client.get("/worlds/1/events")
    assert "还没有历史事件" in response.text


def test_empty_records_list_shows_message(client):
    _create_world(client)
    response = client.get("/worlds/1/records")
    assert "还没有推演记录" in response.text


def test_empty_branches_list_shows_message(client):
    _create_world(client)
    response = client.get("/worlds/1/branches")
    assert "还没有分支记录" in response.text


# --- Form Error Tests ---

def test_world_empty_name_shows_error(client):
    response = client.post("/worlds", data={"name": ""})
    assert response.status_code == 422
    assert "不能为空" in response.text


def test_character_empty_name_shows_error(client):
    _create_world(client)
    response = client.post("/worlds/1/characters", data={"name": ""})
    assert response.status_code == 422
    assert "不能为空" in response.text


def test_faction_empty_name_shows_error(client):
    _create_world(client)
    response = client.post("/worlds/1/factions", data={"name": ""})
    assert response.status_code == 422
    assert "不能为空" in response.text


def test_location_empty_name_shows_error(client):
    _create_world(client)
    response = client.post("/worlds/1/locations", data={"name": ""})
    assert response.status_code == 422
    assert "不能为空" in response.text


def test_rule_empty_name_shows_error(client):
    _create_world(client)
    response = client.post("/worlds/1/rules", data={"name": ""})
    assert response.status_code == 422
    assert "不能为空" in response.text


def test_event_empty_title_shows_error(client):
    _create_world(client)
    response = client.post("/worlds/1/events", data={"title": ""})
    assert response.status_code == 422
    assert "不能为空" in response.text


def test_simulation_empty_question_shows_error(client):
    _create_world(client)
    response = client.post("/worlds/1/simulation", data={"question": ""})
    assert response.status_code == 422
    assert "不能为空" in response.text


def test_conflict_empty_content_shows_error(client):
    _create_world(client)
    response = client.post("/worlds/1/checks/conflicts", data={"content": ""})
    assert response.status_code == 422
    assert "不能为空" in response.text


def test_behavior_empty_shows_error(client):
    _create_world(client)
    client.post("/worlds/1/characters", data={"name": "测试角色"})
    response = client.post("/worlds/1/checks/behavior", data={
        "character_id": "1", "behavior": "",
    })
    assert response.status_code == 422
    assert "不能为空" in response.text


# --- Check Center Path Tests ---

def test_checks_center_path(client):
    _create_world(client)
    assert client.get("/worlds/1/checks").status_code == 200


def test_checks_conflicts_path(client):
    _create_world(client)
    assert client.get("/worlds/1/checks/conflicts").status_code == 200


def test_checks_behavior_path(client):
    _create_world(client)
    assert client.get("/worlds/1/checks/behavior").status_code == 200


# --- Cross-World Isolation (comprehensive) ---

def test_all_modules_cross_world_isolation(client):
    """Ensure all modules maintain cross-world data isolation."""
    client.post("/worlds", data={"name": "世界A", "world_type": "奇幻"})
    client.post("/worlds", data={"name": "世界B", "world_type": "科幻"})

    # Create data in world A
    client.post("/worlds/1/characters", data={"name": "A角色"})
    client.post("/worlds/1/factions", data={"name": "A势力"})
    client.post("/worlds/1/locations", data={"name": "A地点"})
    client.post("/worlds/1/rules", data={"name": "A规则"})
    client.post("/worlds/1/events", data={"title": "A事件", "is_canon": "true"})
    client.post("/worlds/1/simulation", data={"question": "A推演"})

    # Create data in world B
    client.post("/worlds/2/characters", data={"name": "B角色"})
    client.post("/worlds/2/factions", data={"name": "B势力"})
    client.post("/worlds/2/locations", data={"name": "B地点"})
    client.post("/worlds/2/rules", data={"name": "B规则"})
    client.post("/worlds/2/events", data={"title": "B事件", "is_canon": "true"})
    client.post("/worlds/2/simulation", data={"question": "B推演"})

    # World A pages should not show World B data
    checks = [
        ("/worlds/1/characters", "B角色", False),
        ("/worlds/1/factions", "B势力", False),
        ("/worlds/1/locations", "B地点", False),
        ("/worlds/1/rules", "B规则", False),
        ("/worlds/1/events", "B事件", False),
        ("/worlds/1/timeline?view=all", "B事件", False),
        ("/worlds/1/records", "B推演", False),
        ("/worlds/1/characters", "A角色", True),
        ("/worlds/1/factions", "A势力", True),
    ]

    for path, text, should_contain in checks:
        resp = client.get(path)
        if should_contain:
            assert text in resp.text, f"{path} should contain {text}"
        else:
            assert text not in resp.text, f"{path} should NOT contain {text}"


# --- Git Safety Tests ---

def test_db_not_in_git():
    """Verify ai_world_engine.db is gitignored (indirect check via git ls-files)."""
    import subprocess
    result = subprocess.run(
        ["git", "ls-files", "ai_world_engine.db"],
        capture_output=True, text=True, cwd="f:/git"
    )
    assert result.stdout.strip() == "", "ai_world_engine.db should not be tracked by git"


def test_backups_not_in_git():
    """Verify .project_backups/ is gitignored."""
    import subprocess
    result = subprocess.run(
        ["git", "ls-files", ".project_backups/"],
        capture_output=True, text=True, cwd="f:/git"
    )
    assert result.stdout.strip() == "", ".project_backups/ should not be tracked by git"
