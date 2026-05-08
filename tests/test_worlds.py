"""
Tests for world management CRUD.
"""


def test_list_worlds_returns_200(client):
    """Test that GET /worlds returns 200."""
    response = client.get("/worlds")
    assert response.status_code == 200


def test_list_worlds_shows_empty_state(client):
    """Test that empty world list shows empty state message."""
    response = client.get("/worlds")
    assert "还没有任何世界" in response.text


def test_new_world_form_returns_200(client):
    """Test that GET /worlds/new returns 200."""
    response = client.get("/worlds/new")
    assert response.status_code == 200


def test_create_world_success(client):
    """Test that POST /worlds creates a world and redirects."""
    response = client.post("/worlds", data={
        "name": "测试世界",
        "world_type": "奇幻",
        "description": "一个测试世界",
        "current_era": "第一纪元",
        "tone": "史诗",
    }, follow_redirects=False)
    # Should redirect to /worlds
    assert response.status_code == 303
    assert response.headers["location"] == "/worlds"


def test_create_world_appears_in_list(client):
    """Test that a created world appears in the list."""
    client.post("/worlds", data={
        "name": "艾泽拉斯",
        "world_type": "奇幻",
        "description": "魔兽世界",
        "current_era": "第三纪元",
        "tone": "史诗",
    })
    response = client.get("/worlds")
    assert "艾泽拉斯" in response.text
    assert "奇幻" in response.text


def test_world_detail_returns_200(client):
    """Test that GET /worlds/{id} returns 200 for existing world."""
    client.post("/worlds", data={
        "name": "中土世界",
        "world_type": "奇幻",
        "description": "指环王世界",
        "current_era": "第三纪元",
        "tone": "史诗",
    })
    response = client.get("/worlds/1")
    assert response.status_code == 200
    assert "中土世界" in response.text
    assert "指环王世界" in response.text


def test_world_detail_404_for_nonexistent(client):
    """Test that GET /worlds/{id} returns 404 for nonexistent world."""
    response = client.get("/worlds/999")
    assert response.status_code == 404
    assert "世界不存在" in response.text


def test_edit_world_form_returns_200(client):
    """Test that GET /worlds/{id}/edit returns 200."""
    client.post("/worlds", data={
        "name": "编辑测试",
        "world_type": "科幻",
        "description": "测试编辑",
        "current_era": "未来",
        "tone": "黑暗",
    })
    response = client.get("/worlds/1/edit")
    assert response.status_code == 200
    assert "编辑测试" in response.text


def test_edit_world_form_404_for_nonexistent(client):
    """Test that GET /worlds/{id}/edit returns 404 for nonexistent world."""
    response = client.get("/worlds/999/edit")
    assert response.status_code == 404


def test_update_world_success(client):
    """Test that POST /worlds/{id}/edit updates a world."""
    client.post("/worlds", data={
        "name": "原始名称",
        "world_type": "奇幻",
        "description": "原始描述",
        "current_era": "古代",
        "tone": "中性",
    })
    response = client.post("/worlds/1/edit", data={
        "name": "新名称",
        "world_type": "科幻",
        "description": "新描述",
        "current_era": "未来",
        "tone": "黑暗",
    }, follow_redirects=False)
    assert response.status_code == 303

    # Verify the update
    detail = client.get("/worlds/1")
    assert "新名称" in detail.text
    assert "新描述" in detail.text


def test_update_nonexistent_world_returns_404(client):
    """Test that updating nonexistent world returns 404."""
    response = client.post("/worlds/999/edit", data={
        "name": "不存在",
        "world_type": "科幻",
        "description": "",
        "current_era": "",
        "tone": "",
    })
    assert response.status_code == 404


def test_delete_world_success(client):
    """Test that deleting a world removes it from the list."""
    client.post("/worlds", data={
        "name": "待删除世界",
        "world_type": "末世",
        "description": "将被删除",
        "current_era": "末日",
        "tone": "黑暗",
    })
    # Verify it exists
    list_before = client.get("/worlds")
    assert "待删除世界" in list_before.text

    # Delete it
    response = client.post("/worlds/1/delete", follow_redirects=False)
    assert response.status_code == 303

    # Verify it's gone
    list_after = client.get("/worlds")
    assert "待删除世界" not in list_after.text


def test_delete_nonexistent_world_redirects(client):
    """Test that deleting nonexistent world still redirects gracefully."""
    response = client.post("/worlds/999/delete", follow_redirects=False)
    assert response.status_code == 303


def test_create_world_empty_name_fails(client):
    """Test that creating a world with empty name shows error."""
    response = client.post("/worlds", data={
        "name": "",
        "world_type": "奇幻",
        "description": "",
        "current_era": "",
        "tone": "",
    })
    assert response.status_code == 422
    assert "世界名称不能为空" in response.text


def test_create_world_whitespace_name_fails(client):
    """Test that creating a world with whitespace-only name shows error."""
    response = client.post("/worlds", data={
        "name": "   ",
        "world_type": "奇幻",
        "description": "",
        "current_era": "",
        "tone": "",
    })
    assert response.status_code == 422
    assert "世界名称不能为空" in response.text


def test_create_world_name_too_long_fails(client):
    """Test that creating a world with name > 100 chars shows error."""
    response = client.post("/worlds", data={
        "name": "A" * 101,
        "world_type": "奇幻",
        "description": "",
        "current_era": "",
        "tone": "",
    })
    assert response.status_code == 422
    assert "不能超过100个字符" in response.text


def test_update_world_empty_name_fails(client):
    """Test that updating a world with empty name shows error."""
    client.post("/worlds", data={
        "name": "测试世界",
        "world_type": "奇幻",
        "description": "",
        "current_era": "",
        "tone": "",
    })
    response = client.post("/worlds/1/edit", data={
        "name": "",
        "world_type": "奇幻",
        "description": "",
        "current_era": "",
        "tone": "",
    })
    assert response.status_code == 422
    assert "世界名称不能为空" in response.text


def test_world_detail_shows_module_placeholders(client):
    """Test that world detail shows module navigation entries."""
    client.post("/worlds", data={
        "name": "模块测试",
        "world_type": "奇幻",
        "description": "测试",
        "current_era": "古代",
        "tone": "史诗",
    })
    response = client.get("/worlds/1")
    assert "角色管理" in response.text
    assert "势力管理" in response.text
    assert "地点管理" in response.text
    assert "规则管理" in response.text
    assert "时间线" in response.text
    assert "AI 推演" in response.text
    # Time and AI still show "即将推出"
    assert "即将推出" in response.text
