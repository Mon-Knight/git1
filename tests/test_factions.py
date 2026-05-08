"""
Tests for faction management CRUD.
"""


def _create_world(client):
    client.post("/worlds", data={"name": "测试世界", "world_type": "奇幻"})


def test_list_factions_returns_200(client):
    _create_world(client)
    response = client.get("/worlds/1/factions")
    assert response.status_code == 200


def test_new_faction_form_returns_200(client):
    _create_world(client)
    response = client.get("/worlds/1/factions/new")
    assert response.status_code == 200


def test_create_faction_success(client):
    _create_world(client)
    response = client.post("/worlds/1/factions", data={
        "name": "洛丹伦", "faction_type": "王国", "goal": "和平",
    }, follow_redirects=False)
    assert response.status_code == 303


def test_created_faction_appears_in_list(client):
    _create_world(client)
    client.post("/worlds/1/factions", data={"name": "部落"})
    response = client.get("/worlds/1/factions")
    assert "部落" in response.text


def test_faction_detail_returns_200(client):
    _create_world(client)
    client.post("/worlds/1/factions", data={"name": "联盟", "faction_type": "联盟"})
    response = client.get("/worlds/1/factions/1")
    assert response.status_code == 200
    assert "联盟" in response.text


def test_faction_detail_404(client):
    _create_world(client)
    response = client.get("/worlds/1/factions/999")
    assert response.status_code == 404


def test_edit_faction_form_returns_200(client):
    _create_world(client)
    client.post("/worlds/1/factions", data={"name": "测试势力"})
    response = client.get("/worlds/1/factions/1/edit")
    assert response.status_code == 200


def test_update_faction_success(client):
    _create_world(client)
    client.post("/worlds/1/factions", data={"name": "原名"})
    client.post("/worlds/1/factions/1/edit", data={
        "name": "新势力名", "faction_type": "帝国",
    }, follow_redirects=False)
    detail = client.get("/worlds/1/factions/1")
    assert "新势力名" in detail.text


def test_delete_faction_success(client):
    _create_world(client)
    client.post("/worlds/1/factions", data={"name": "待删除"})
    client.post("/worlds/1/factions/1/delete", follow_redirects=False)
    response = client.get("/worlds/1/factions")
    assert "待删除" not in response.text


def test_create_faction_empty_name_fails(client):
    _create_world(client)
    response = client.post("/worlds/1/factions", data={"name": ""})
    assert response.status_code == 422
    assert "名称不能为空" in response.text


def test_faction_not_shown_in_other_world(client):
    client.post("/worlds", data={"name": "世界A", "world_type": "奇幻"})
    client.post("/worlds", data={"name": "世界B", "world_type": "科幻"})
    client.post("/worlds/1/factions", data={"name": "A势力"})
    client.post("/worlds/2/factions", data={"name": "B势力"})
    resp_a = client.get("/worlds/1/factions")
    assert "A势力" in resp_a.text
    assert "B势力" not in resp_a.text
