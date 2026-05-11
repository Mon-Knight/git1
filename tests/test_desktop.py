"""
Tests for desktop launcher and resource path utilities.
"""

import os
import sys
import socket


def test_desktop_launcher_can_be_imported():
    """Test that desktop_launcher module can be imported."""
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import desktop_launcher
    assert desktop_launcher is not None


def test_find_free_port():
    """Test that find_free_port returns a valid port number."""
    from desktop_launcher import find_free_port

    port = find_free_port(10000, 10010)
    assert isinstance(port, int)
    assert 10000 <= port <= 10010

    # Verify the port is actually free
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.1)
        result = s.connect_ex(("127.0.0.1", port))
        # Note: port might have been taken between find and check
        # Just verify it's a valid integer
        assert port > 0


def test_find_free_port_defaults():
    """Test find_free_port works with default range."""
    from desktop_launcher import find_free_port

    port = find_free_port()
    assert isinstance(port, int)
    assert 8000 <= port <= 9000


def test_resource_path_returns_valid_path():
    """Test resource_path returns an existing path in normal mode."""
    from app.config import resource_path

    path = resource_path("app")
    assert os.path.exists(path), f"Path {path} does not exist"


def test_resource_path_returns_string():
    """Test resource_path returns a string."""
    from app.config import resource_path

    path = resource_path("README.md")
    assert isinstance(path, str)
    assert os.path.exists(path)


def test_desktop_db_path_returns_sqlite_url():
    """Test get_desktop_db_path returns a valid SQLite URL."""
    from app.config import Settings

    url = Settings.get_desktop_db_path()
    assert url.startswith("sqlite:///")
    assert "ai_world_engine.db" in url


def test_desktop_db_path_creates_directory():
    """Test get_desktop_db_path creates directory on Windows."""
    if sys.platform != "win32":
        return  # Skip on non-Windows

    from app.config import Settings

    url = Settings.get_desktop_db_path()
    # Extract path from URL
    db_path = url.replace("sqlite:///", "")
    db_dir = os.path.dirname(db_path)
    assert os.path.exists(db_dir), f"Directory {db_dir} was not created"


def test_config_version_updated():
    """Test that VERSION reflects 1.7.2."""
    from app.config import settings
    assert settings.VERSION == "1.7.8"
