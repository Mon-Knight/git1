"""
Tests for world rule management CRUD.
"""


def _create_world(client):
    client.post("/worlds", data={"name": "测试世界", "world_type": "奇幻"})


def test_list_rules_returns_200(client):
    _create_world(client)
    response = client.get("/worlds/1/rules")
    assert response.status_code == 200


def test_new_rule_form_returns_200(client):
    _create_world(client)
    response = client.get("/worlds/1/rules/new")
    assert response.status_code == 200


def test_create_rule_success(client):
    _create_world(client)
    response = client.post("/worlds/1/rules", data={
        "name": "魔法守恒定律", "rule_type": "魔法体系",
        "content": "魔法能量不可被创造或毁灭",
    }, follow_redirects=False)
    assert response.status_code == 303


def test_created_rule_appears_in_list(client):
    _create_world(client)
    client.post("/worlds/1/rules", data={"name": "重力法则"})
    response = client.get("/worlds/1/rules")
    assert "重力法则" in response.text


def test_rule_detail_returns_200(client):
    _create_world(client)
    client.post("/worlds/1/rules", data={"name": "等价交换", "rule_type": "魔法体系"})
    response = client.get("/worlds/1/rules/1")
    assert response.status_code == 200
    assert "等价交换" in response.text


def test_rule_detail_404(client):
    _create_world(client)
    response = client.get("/worlds/1/rules/999")
    assert response.status_code == 404


def test_edit_rule_form_returns_200(client):
    _create_world(client)
    client.post("/worlds/1/rules", data={"name": "测试规则"})
    response = client.get("/worlds/1/rules/1/edit")
    assert response.status_code == 200


def test_update_rule_success(client):
    _create_world(client)
    client.post("/worlds/1/rules", data={"name": "原名"})
    client.post("/worlds/1/rules/1/edit", data={
        "name": "新规则名", "rule_type": "社会结构",
    }, follow_redirects=False)
    detail = client.get("/worlds/1/rules/1")
    assert "新规则名" in detail.text


def test_delete_rule_success(client):
    _create_world(client)
    client.post("/worlds/1/rules", data={"name": "待删除"})
    client.post("/worlds/1/rules/1/delete", follow_redirects=False)
    response = client.get("/worlds/1/rules")
    assert "待删除" not in response.text


def test_create_rule_empty_name_fails(client):
    _create_world(client)
    response = client.post("/worlds/1/rules", data={"name": ""})
    assert response.status_code == 422
    assert "名称不能为空" in response.text


def test_rule_not_shown_in_other_world(client):
    client.post("/worlds", data={"name": "世界A", "world_type": "奇幻"})
    client.post("/worlds", data={"name": "世界B", "world_type": "科幻"})
    client.post("/worlds/1/rules", data={"name": "A规则"})
    client.post("/worlds/2/rules", data={"name": "B规则"})
    resp_a = client.get("/worlds/1/rules")
    assert "A规则" in resp_a.text
    assert "B规则" not in resp_a.text
