"""
Tests for historical event management CRUD.
"""


def _create_world(client):
    client.post("/worlds", data={"name": "测试世界", "world_type": "奇幻"})


def test_list_events_returns_200(client):
    _create_world(client)
    response = client.get("/worlds/1/events")
    assert response.status_code == 200


def test_new_event_form_returns_200(client):
    _create_world(client)
    response = client.get("/worlds/1/events/new")
    assert response.status_code == 200


def test_create_event_success(client):
    _create_world(client)
    response = client.post("/worlds/1/events", data={
        "title": "大战爆发", "event_time": "2024-01-01",
        "content": "一场大战", "is_canon": "true",
    }, follow_redirects=False)
    assert response.status_code == 303


def test_created_event_appears_in_list(client):
    _create_world(client)
    client.post("/worlds/1/events", data={"title": "王国建立", "is_canon": "true"})
    response = client.get("/worlds/1/events")
    assert "王国建立" in response.text


def test_event_detail_returns_200(client):
    _create_world(client)
    client.post("/worlds/1/events", data={
        "title": "和平条约", "event_time": "2024-06-01",
        "content": "签署和平条约", "is_canon": "true",
    })
    response = client.get("/worlds/1/events/1")
    assert response.status_code == 200
    assert "和平条约" in response.text


def test_event_detail_404(client):
    _create_world(client)
    response = client.get("/worlds/1/events/999")
    assert response.status_code == 404


def test_edit_event_form_returns_200(client):
    _create_world(client)
    client.post("/worlds/1/events", data={"title": "测试事件", "is_canon": "true"})
    response = client.get("/worlds/1/events/1/edit")
    assert response.status_code == 200


def test_update_event_success(client):
    _create_world(client)
    client.post("/worlds/1/events", data={"title": "原名", "is_canon": "true"})
    client.post("/worlds/1/events/1/edit", data={
        "title": "新事件名", "event_time": "2025-01-01",
        "content": "新内容", "is_canon": "true",
    }, follow_redirects=False)
    detail = client.get("/worlds/1/events/1")
    assert "新事件名" in detail.text


def test_delete_event_success(client):
    _create_world(client)
    client.post("/worlds/1/events", data={"title": "待删除", "is_canon": "true"})
    client.post("/worlds/1/events/1/delete", follow_redirects=False)
    response = client.get("/worlds/1/events")
    assert "待删除" not in response.text


def test_create_event_empty_title_fails(client):
    _create_world(client)
    response = client.post("/worlds/1/events", data={"title": "", "is_canon": "true"})
    assert response.status_code == 422
    assert "事件标题不能为空" in response.text


def test_event_not_shown_in_other_world(client):
    client.post("/worlds", data={"name": "世界A", "world_type": "奇幻"})
    client.post("/worlds", data={"name": "世界B", "world_type": "科幻"})
    client.post("/worlds/1/events", data={"title": "A事件", "is_canon": "true"})
    client.post("/worlds/2/events", data={"title": "B事件", "is_canon": "true"})
    resp_a = client.get("/worlds/1/events")
    assert "A事件" in resp_a.text
    assert "B事件" not in resp_a.text


def test_create_non_canon_event(client):
    _create_world(client)
    client.post("/worlds/1/events", data={
        "title": "非正史事件", "is_canon": "false",
    })
    response = client.get("/worlds/1/events/1")
    assert "非正史" in response.text
