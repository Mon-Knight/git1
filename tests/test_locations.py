"""
Tests for location management CRUD.
"""


def _create_world(client):
    client.post("/worlds", data={"name": "测试世界", "world_type": "奇幻"})


def test_list_locations_returns_200(client):
    _create_world(client)
    response = client.get("/worlds/1/locations")
    assert response.status_code == 200


def test_new_location_form_returns_200(client):
    _create_world(client)
    response = client.get("/worlds/1/locations/new")
    assert response.status_code == 200


def test_create_location_success(client):
    _create_world(client)
    response = client.post("/worlds/1/locations", data={
        "name": "暴风城", "location_type": "城市", "region": "东部王国",
    }, follow_redirects=False)
    assert response.status_code == 303


def test_created_location_appears_in_list(client):
    _create_world(client)
    client.post("/worlds/1/locations", data={"name": "奥格瑞玛"})
    response = client.get("/worlds/1/locations")
    assert "奥格瑞玛" in response.text


def test_location_detail_returns_200(client):
    _create_world(client)
    client.post("/worlds/1/locations", data={"name": "铁炉堡", "location_type": "城市"})
    response = client.get("/worlds/1/locations/1")
    assert response.status_code == 200
    assert "铁炉堡" in response.text


def test_location_detail_404(client):
    _create_world(client)
    response = client.get("/worlds/1/locations/999")
    assert response.status_code == 404


def test_edit_location_form_returns_200(client):
    _create_world(client)
    client.post("/worlds/1/locations", data={"name": "测试地点"})
    response = client.get("/worlds/1/locations/1/edit")
    assert response.status_code == 200


def test_update_location_success(client):
    _create_world(client)
    client.post("/worlds/1/locations", data={"name": "原名"})
    client.post("/worlds/1/locations/1/edit", data={
        "name": "新地名", "location_type": "遗迹",
    }, follow_redirects=False)
    detail = client.get("/worlds/1/locations/1")
    assert "新地名" in detail.text


def test_delete_location_success(client):
    _create_world(client)
    client.post("/worlds/1/locations", data={"name": "待删除"})
    client.post("/worlds/1/locations/1/delete", follow_redirects=False)
    response = client.get("/worlds/1/locations")
    assert "待删除" not in response.text


def test_create_location_empty_name_fails(client):
    _create_world(client)
    response = client.post("/worlds/1/locations", data={"name": ""})
    assert response.status_code == 422
    assert "名称不能为空" in response.text


def test_location_not_shown_in_other_world(client):
    client.post("/worlds", data={"name": "世界A", "world_type": "奇幻"})
    client.post("/worlds", data={"name": "世界B", "world_type": "科幻"})
    client.post("/worlds/1/locations", data={"name": "A地点"})
    client.post("/worlds/2/locations", data={"name": "B地点"})
    resp_a = client.get("/worlds/1/locations")
    assert "A地点" in resp_a.text
    assert "B地点" not in resp_a.text
