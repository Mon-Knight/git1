"""
Tests for timeline viewing.
"""


def _create_world(client):
    client.post("/worlds", data={"name": "测试世界", "world_type": "奇幻"})


def test_timeline_returns_200(client):
    _create_world(client)
    response = client.get("/worlds/1/timeline")
    assert response.status_code == 200


def test_timeline_shows_canon_event(client):
    _create_world(client)
    client.post("/worlds/1/events", data={
        "title": "正史事件A", "event_time": "0001-01-01",
        "content": "正史内容", "is_canon": "true",
    })
    response = client.get("/worlds/1/timeline?view=canon")
    assert "正史事件A" in response.text


def test_timeline_canon_view_only_canon(client):
    _create_world(client)
    client.post("/worlds/1/events", data={
        "title": "AAA正史事件", "is_canon": "true",
    })
    client.post("/worlds/1/events", data={
        "title": "BBB非正史事件", "is_canon": "false",
    })
    response = client.get("/worlds/1/timeline?view=canon")
    assert "AAA正史事件" in response.text
    assert "BBB非正史事件" not in response.text


def test_timeline_all_view_shows_all(client):
    _create_world(client)
    client.post("/worlds/1/events", data={
        "title": "CCC正史事件", "is_canon": "true",
    })
    client.post("/worlds/1/events", data={
        "title": "DDD非正史事件", "is_canon": "false",
    })
    response = client.get("/worlds/1/timeline?view=all")
    assert "CCC正史事件" in response.text
    assert "DDD非正史事件" in response.text


def test_timeline_non_canon_view_only_non_canon(client):
    _create_world(client)
    client.post("/worlds/1/events", data={
        "title": "EEE正史事件", "is_canon": "true",
    })
    client.post("/worlds/1/events", data={
        "title": "FFF非正史事件", "is_canon": "false",
    })
    response = client.get("/worlds/1/timeline?view=non_canon")
    assert "FFF非正史事件" in response.text
    assert "EEE正史事件" not in response.text


def test_timeline_distinguishes_canon(client):
    """Timeline page shows visual distinction between canon and non-canon."""
    _create_world(client)
    client.post("/worlds/1/events", data={
        "title": "GGG正史事件", "is_canon": "true",
    })
    client.post("/worlds/1/events", data={
        "title": "HHH非正史事件", "is_canon": "false",
    })
    response = client.get("/worlds/1/timeline?view=all")
    assert "正史" in response.text
    assert "非正史" in response.text


def test_timeline_not_show_other_world(client):
    client.post("/worlds", data={"name": "世界A", "world_type": "奇幻"})
    client.post("/worlds", data={"name": "世界B", "world_type": "科幻"})
    client.post("/worlds/1/events", data={"title": "A事件", "is_canon": "true"})
    client.post("/worlds/2/events", data={"title": "B事件", "is_canon": "true"})
    resp_a = client.get("/worlds/1/timeline?view=all")
    assert "A事件" in resp_a.text
    assert "B事件" not in resp_a.text
