"""
AI World Engine - Test Data Routes
"""


def _create_world(client):
    return client.post("/worlds", data={"name": "DataRouteTestWorld", "world_type": "奇幻"})


def test_data_index_returns_200(client):
    response = client.get("/data")
    assert response.status_code == 200
    assert "数据管理" in response.text


def test_import_page_returns_200(client):
    response = client.get("/data/import")
    assert response.status_code == 200
    assert "导入" in response.text


def test_backups_page_returns_200(client):
    response = client.get("/data/backups")
    assert response.status_code == 200
    assert "备份" in response.text


def test_world_detail_has_export_button(client):
    _create_world(client)
    response = client.get("/worlds/1")
    assert "/export" in response.text


def test_export_page_returns_200(client):
    _create_world(client)
    response = client.get("/worlds/1/export")
    assert response.status_code == 200
    assert "导出" in response.text


def test_export_json_returns_200(client):
    _create_world(client)
    response = client.get("/worlds/1/export.json")
    assert response.status_code == 200
    assert response.headers.get("content-type", "").startswith("application/json")


def test_export_json_404(client):
    response = client.get("/worlds/999/export.json")
    assert response.status_code == 404


def test_home_page_has_data_link(client):
    response = client.get("/")
    assert "/data" in response.text or "数据管理" in response.text


def test_import_post_invalid_json(client):
    import io
    data = io.BytesIO(b"not valid json")
    response = client.post("/data/import", files={"import_file": ("test.json", data, "application/json")})
    assert response.status_code == 422


def test_create_backup_route(client):
    response = client.post("/data/backups/create")
    assert response.status_code == 200
    assert "备份" in response.text


def test_restore_no_filename_returns_error(client):
    response = client.post("/data/backups/restore", data={"backup_filename": "", "confirm": "YES_RESTORE"})
    assert response.status_code == 200


def test_sim_type_label_in_data_page(client):
    _create_world(client)
    client.post("/worlds/1/novel", data={"main_story_direction": "主线测试"})
    response = client.get("/worlds/1/records")
    assert "小说工程推演" in response.text
