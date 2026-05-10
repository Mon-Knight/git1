"""
Tests for the FastAPI application entry point and home page.
"""


def test_app_import():
    """Test that the FastAPI app can be imported."""
    from app.main import app
    assert app is not None
    assert app.title == "AI World Engine"


def test_home_page_returns_200(client):
    """Test that the home page returns HTTP 200."""
    response = client.get("/")
    assert response.status_code == 200


def test_home_page_contains_title(client):
    """Test that the home page contains 'AI World Engine'."""
    response = client.get("/")
    assert "AI World Engine" in response.text


def test_home_page_contains_version(client):
    """Test that the home page contains the version number."""
    response = client.get("/")
    assert "v1.3.0" in response.text


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_static_css_accessible(client):
    """Test that static CSS files are accessible."""
    response = client.get("/static/css/style.css")
    assert response.status_code == 200
    assert "text/css" in response.headers.get("content-type", "")
