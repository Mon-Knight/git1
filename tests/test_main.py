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
    assert "v1.7.8.2" in response.text


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


# --- v1.3.2: AI Settings Entry Tests ---

def test_home_page_has_settings_link(client):
    """Home page should contain /settings/ai link."""
    response = client.get("/")
    assert response.status_code == 200
    assert "/settings/ai" in response.text


def test_home_page_has_ai_settings_button(client):
    """Home page should have a '配置 AI' or 'AI 设置' button."""
    response = client.get("/")
    assert "配置 AI" in response.text or "AI 设置" in response.text


def test_home_page_shows_ai_config_card(client):
    """Home page should display AI mode status."""
    response = client.get("/")
    assert "Mock AI" in response.text or "Live API" in response.text


def test_home_page_shows_mock_ai_hint(client):
    """In default (mock) mode, home page should show Mock AI description."""
    response = client.get("/")
    assert "Mock AI" in response.text


def test_home_page_does_not_leak_api_key(client):
    """Home page should never show a full API key."""
    from app.main import app
    from app.database import get_db
    from app.services.settings_service import SettingsService
    db = next(app.dependency_overrides[get_db]())
    try:
        SettingsService.set(db, "ai_api_key", "sk-verysecretkey12345678", is_secret=True)
    finally:
        db.close()
    response = client.get("/")
    assert "sk-verysecretkey12345678" not in response.text


def test_home_page_passes_ai_summary(client):
    """Home page should receive ai_summary data from the route."""
    response = client.get("/")
    # Should contain AI summary indicators (mode label)
    assert "Mock AI" in response.text or "Mock (演示)" in response.text


def test_home_page_has_primary_config_button(client):
    """Home page should have a link to AI settings."""
    response = client.get("/")
    assert 'href="/settings/ai"' in response.text
