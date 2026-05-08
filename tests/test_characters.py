"""
Tests for character management CRUD.
"""


def _create_world(client):
    client.post("/worlds", data={
        "name": "测试世界", "world_type": "奇幻",
        "description": "", "current_era": "", "tone": "",
    })


def test_list_characters_returns_200(client):
    _create_world(client)
    response = client.get("/worlds/1/characters")
    assert response.status_code == 200


def test_new_character_form_returns_200(client):
    _create_world(client)
    response = client.get("/worlds/1/characters/new")
    assert response.status_code == 200


def test_create_character_success(client):
    _create_world(client)
    response = client.post("/worlds/1/characters", data={
        "name": "阿尔萨斯", "role": "王子", "personality": "骄傲",
        "goal": "拯救王国", "abilities": "剑术", "current_status": "存活",
    }, follow_redirects=False)
    assert response.status_code == 303


def test_created_character_appears_in_list(client):
    _create_world(client)
    client.post("/worlds/1/characters", data={
        "name": "吉安娜", "role": "法师", "personality": "聪慧",
    })
    response = client.get("/worlds/1/characters")
    assert "吉安娜" in response.text


def test_character_detail_returns_200(client):
    _create_world(client)
    client.post("/worlds/1/characters", data={
        "name": "萨尔", "role": "萨满", "personality": "睿智",
    })
    response = client.get("/worlds/1/characters/1")
    assert response.status_code == 200
    assert "萨尔" in response.text


def test_character_detail_404(client):
    _create_world(client)
    response = client.get("/worlds/1/characters/999")
    assert response.status_code == 404


def test_edit_character_form_returns_200(client):
    _create_world(client)
    client.post("/worlds/1/characters", data={"name": "测试角色"})
    response = client.get("/worlds/1/characters/1/edit")
    assert response.status_code == 200


def test_update_character_success(client):
    _create_world(client)
    client.post("/worlds/1/characters", data={"name": "原名"})
    client.post("/worlds/1/characters/1/edit", data={
        "name": "新名", "role": "国王", "current_status": "存活",
    }, follow_redirects=False)
    detail = client.get("/worlds/1/characters/1")
    assert "新名" in detail.text


def test_delete_character_success(client):
    _create_world(client)
    client.post("/worlds/1/characters", data={"name": "待删除"})
    client.post("/worlds/1/characters/1/delete", follow_redirects=False)
    response = client.get("/worlds/1/characters")
    assert "待删除" not in response.text


def test_create_character_empty_name_fails(client):
    _create_world(client)
    response = client.post("/worlds/1/characters", data={"name": ""})
    assert response.status_code == 422
    assert "名称不能为空" in response.text


def test_character_not_shown_in_other_world(client):
    client.post("/worlds", data={"name": "世界A", "world_type": "奇幻"})
    client.post("/worlds", data={"name": "世界B", "world_type": "科幻"})
    client.post("/worlds/1/characters", data={"name": "A角色"})
    client.post("/worlds/2/characters", data={"name": "B角色"})
    # World A should not show B's character
    resp_a = client.get("/worlds/1/characters")
    assert "A角色" in resp_a.text
    assert "B角色" not in resp_a.text
