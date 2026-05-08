"""
Tests for canon adoption and branch creation from simulation records.
"""


def _create_world(client):
    client.post("/worlds", data={"name": "测试世界", "world_type": "奇幻"})


def _create_pending_record(client):
    """Create a world and a pending simulation record."""
    _create_world(client)
    client.post("/worlds/1/simulation", data={
        "question": "测试推演问题ABC",
        "simulation_type": "剧情发展",
    })


# --- Adoption Tests ---

def test_adopt_pending_record_success(client):
    _create_pending_record(client)
    response = client.post("/worlds/1/records/1/adopt", follow_redirects=False)
    assert response.status_code == 303
    # Should redirect to events/{id}
    assert "/events/" in response.headers["location"]


def test_adopt_changes_record_status(client):
    _create_pending_record(client)
    client.post("/worlds/1/records/1/adopt", follow_redirects=False)
    detail = client.get("/worlds/1/records/1")
    assert "adopted" in detail.text
    assert "已采纳为正史" in detail.text


def test_adopt_creates_historical_event(client):
    _create_pending_record(client)
    client.post("/worlds/1/records/1/adopt", follow_redirects=False)
    # Check events list
    events_resp = client.get("/worlds/1/events")
    assert "AI推演采纳" in events_resp.text


def test_adopted_event_is_canon(client):
    _create_pending_record(client)
    client.post("/worlds/1/records/1/adopt", follow_redirects=False)
    event_resp = client.get("/worlds/1/events/1")
    assert "正史" in event_resp.text


def test_adopted_event_source_is_simulation(client):
    _create_pending_record(client)
    client.post("/worlds/1/records/1/adopt", follow_redirects=False)
    event_resp = client.get("/worlds/1/events/1")
    assert "simulation" in event_resp.text


def test_adopted_event_appears_in_canon_timeline(client):
    _create_pending_record(client)
    client.post("/worlds/1/records/1/adopt", follow_redirects=False)
    timeline = client.get("/worlds/1/timeline?view=canon")
    assert "AI推演采纳" in timeline.text


def test_adopted_event_not_in_non_canon_timeline(client):
    _create_pending_record(client)
    client.post("/worlds/1/records/1/adopt", follow_redirects=False)
    timeline = client.get("/worlds/1/timeline?view=non_canon")
    assert "AI推演采纳" not in timeline.text


def test_cannot_adopt_twice(client):
    _create_pending_record(client)
    client.post("/worlds/1/records/1/adopt", follow_redirects=False)
    # Try again
    response = client.post("/worlds/1/records/1/adopt", follow_redirects=False)
    assert response.status_code == 400
    assert "不允许操作" in response.text


def test_cannot_adopt_from_other_world(client):
    client.post("/worlds", data={"name": "世界A", "world_type": "奇幻"})
    client.post("/worlds", data={"name": "世界B", "world_type": "科幻"})
    client.post("/worlds/1/simulation", data={"question": "A的推演"})
    # World B tries to adopt World A's record
    response = client.post("/worlds/2/records/1/adopt", follow_redirects=False)
    assert response.status_code == 404


# --- Branch Tests ---

def test_branch_pending_record_success(client):
    _create_pending_record(client)
    response = client.post("/worlds/1/records/1/branch", follow_redirects=False)
    assert response.status_code == 303
    assert "/branches/" in response.headers["location"]


def test_branch_changes_record_status(client):
    _create_pending_record(client)
    client.post("/worlds/1/records/1/branch", follow_redirects=False)
    detail = client.get("/worlds/1/records/1")
    assert "branched" in detail.text
    assert "已保存为分支" in detail.text


def test_branch_creates_branch_record(client):
    _create_pending_record(client)
    client.post("/worlds/1/records/1/branch", follow_redirects=False)
    branches_resp = client.get("/worlds/1/branches")
    assert "分支" in branches_resp.text


def test_branch_does_not_create_historical_event(client):
    _create_pending_record(client)
    # Count events before
    before = client.get("/worlds/1/events")
    before_count = before.text.count("world-card")

    client.post("/worlds/1/records/1/branch", follow_redirects=False)

    after = client.get("/worlds/1/events")
    after_count = after.text.count("world-card")
    assert after_count == before_count


def test_branch_does_not_change_canon_timeline(client):
    _create_pending_record(client)
    client.post("/worlds/1/records/1/branch", follow_redirects=False)
    timeline = client.get("/worlds/1/timeline?view=canon")
    # Should still be empty (no canon events)
    assert "timeline-item" not in timeline.text or "暂无事件" in timeline.text


def test_cannot_branch_twice(client):
    _create_pending_record(client)
    client.post("/worlds/1/records/1/branch", follow_redirects=False)
    response = client.post("/worlds/1/records/1/branch", follow_redirects=False)
    assert response.status_code == 400
    assert "不允许操作" in response.text


def test_branched_record_cannot_be_adopted(client):
    _create_pending_record(client)
    client.post("/worlds/1/records/1/branch", follow_redirects=False)
    response = client.post("/worlds/1/records/1/adopt", follow_redirects=False)
    assert response.status_code == 400


def test_adopted_record_cannot_be_branched(client):
    _create_pending_record(client)
    client.post("/worlds/1/records/1/adopt", follow_redirects=False)
    response = client.post("/worlds/1/records/1/branch", follow_redirects=False)
    assert response.status_code == 400


def test_cannot_branch_from_other_world(client):
    client.post("/worlds", data={"name": "世界A", "world_type": "奇幻"})
    client.post("/worlds", data={"name": "世界B", "world_type": "科幻"})
    client.post("/worlds/1/simulation", data={"question": "A的推演"})
    response = client.post("/worlds/2/records/1/branch", follow_redirects=False)
    assert response.status_code == 404


# --- Branch Pages ---

def test_branches_list_returns_200(client):
    _create_world(client)
    response = client.get("/worlds/1/branches")
    assert response.status_code == 200


def test_branch_detail_returns_200(client):
    _create_pending_record(client)
    client.post("/worlds/1/records/1/branch", follow_redirects=False)
    response = client.get("/worlds/1/branches/1")
    assert response.status_code == 200


def test_branch_detail_404(client):
    _create_world(client)
    response = client.get("/worlds/1/branches/999")
    assert response.status_code == 404


def test_branch_not_visible_from_other_world(client):
    client.post("/worlds", data={"name": "世界A", "world_type": "奇幻"})
    client.post("/worlds", data={"name": "世界B", "world_type": "科幻"})
    client.post("/worlds/1/simulation", data={"question": "A的推演"})
    client.post("/worlds/1/records/1/branch", follow_redirects=False)
    # World B should not see World A's branch
    resp_b = client.get("/worlds/2/branches")
    assert "分支" not in resp_b.text or "还没有分支记录" in resp_b.text


# --- UI State Tests ---

def test_pending_record_shows_action_buttons(client):
    _create_pending_record(client)
    response = client.get("/worlds/1/records/1")
    assert "采纳为正史" in response.text
    assert "保存为分支" in response.text


def test_adopted_record_hides_action_buttons(client):
    _create_pending_record(client)
    client.post("/worlds/1/records/1/adopt", follow_redirects=False)
    response = client.get("/worlds/1/records/1")
    # The form action URLs should not be present
    assert 'records/1/adopt' not in response.text
    assert 'records/1/branch' not in response.text


def test_branched_record_hides_action_buttons(client):
    _create_pending_record(client)
    client.post("/worlds/1/records/1/branch", follow_redirects=False)
    response = client.get("/worlds/1/records/1")
    # The form action URLs should not be present
    assert 'records/1/adopt' not in response.text
    assert 'records/1/branch' not in response.text
