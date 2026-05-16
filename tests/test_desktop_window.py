"""
AI World Engine - Test Desktop Window Configuration
Tests for v1.7.7 desktop window size and EXE configuration.
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read_root(filename: str) -> str:
    path = os.path.join(PROJECT_ROOT, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class TestDesktopWindowConfig:
    """Tests for desktop_launcher.py window configuration."""

    def test_desktop_launcher_has_default_width(self):
        content = _read_root("desktop_launcher.py")
        assert "win_width" in content or "width=1280" in content, "desktop_launcher.py missing window width config"

    def test_desktop_launcher_has_default_height(self):
        content = _read_root("desktop_launcher.py")
        assert "win_height" in content or "height=820" in content, "desktop_launcher.py missing window height config"

    def test_desktop_launcher_has_min_size(self):
        content = _read_root("desktop_launcher.py")
        assert "min_size=(1024, 700)" in content, (
            "desktop_launcher.py missing min_size (1024, 700)"
        )

    def test_desktop_launcher_has_resizable_true(self):
        content = _read_root("desktop_launcher.py")
        assert "resizable=True" in content, "desktop_launcher.py missing resizable=True"

    def test_desktop_launcher_creates_webview_window(self):
        content = _read_root("desktop_launcher.py")
        assert "webview.create_window" in content, "desktop_launcher.py missing webview window creation"


class TestVersionConfig:
    """Tests that version is updated to 1.7.8."""

    def test_config_version_is_200(self):
        from app.config import settings
        assert settings.VERSION == "2.0.1.2", (
            f"Expected 2.0.1.2, got {settings.VERSION}"
        )

    def test_desktop_test_version_matches(self):
        # The test_desktop.py test should also reflect 2.0.0
        content = _read_root("tests/test_desktop.py")
        assert "2.0.1.2" in content, "tests/test_desktop.py missing version 2.0.1.2"
