"""
AI World Engine - Test Desktop Export API
Tests for DesktopExportApi class and desktop_launcher configuration.
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read_root(filename: str) -> str:
    path = os.path.join(PROJECT_ROOT, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class TestDesktopExportApiClass:
    """Tests that DesktopExportApi exists in desktop_launcher."""

    def test_api_class_exists(self):
        content = _read_root("desktop_launcher.py")
        assert "class DesktopExportApi" in content, "Missing DesktopExportApi class"

    def test_choose_save_path_method_exists(self):
        content = _read_root("desktop_launcher.py")
        assert "def choose_save_path" in content, "Missing choose_save_path method"

    def test_js_api_passed_to_window(self):
        content = _read_root("desktop_launcher.py")
        assert "js_api=api" in content, "Missing js_api=api in create_window"

    def test_choose_save_path_returns_dict(self):
        content = _read_root("desktop_launcher.py")
        assert '"ok": True' in content or '"ok": False' in content, "Missing ok return"


class TestDesktopWindowConfig:
    """Window config should still match v1.7.7 specs."""

    def test_window_width_1280(self):
        content = _read_root("desktop_launcher.py")
        assert "width=1280" in content

    def test_window_height_820(self):
        content = _read_root("desktop_launcher.py")
        assert "height=820" in content

    def test_min_size_1024_700(self):
        content = _read_root("desktop_launcher.py")
        assert "min_size=(1024, 700)" in content

    def test_desktop_mode_env_set(self):
        content = _read_root("desktop_launcher.py")
        assert "AIWE_DESKTOP_MODE" in content, "Missing AIWE_DESKTOP_MODE env"


class TestExportJS:
    """Tests for export-center.js."""

    def test_js_file_exists(self):
        path = os.path.join(PROJECT_ROOT, "app", "static", "js", "export-center.js")
        assert os.path.isfile(path), "export-center.js not found"

    def test_js_has_desktop_check(self):
        content = _read_root("app/static/js/export-center.js")
        assert "window.pywebview" in content, "Missing pywebview check"
