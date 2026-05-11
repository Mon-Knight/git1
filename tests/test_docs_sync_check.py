"""
Tests for documentation sync checker (scripts/check_docs_sync.py).
"""
import os
import sys
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


class TestDocsSyncScript:
    """Verify check_docs_sync.py exists and has correct structure."""

    def test_script_exists(self):
        assert (PROJECT_ROOT / "scripts" / "check_docs_sync.py").is_file()

    def test_script_is_valid_python(self):
        path = PROJECT_ROOT / "scripts" / "check_docs_sync.py"
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "def check_docs_sync" in content
        assert "def main" in content
        assert "TRIGGER_PATTERNS" in content
        assert "DOC_FILES" in content

    def test_script_has_staged_mode(self):
        path = PROJECT_ROOT / "scripts" / "check_docs_sync.py"
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "--staged" in content

    def test_script_has_all_mode(self):
        path = PROJECT_ROOT / "scripts" / "check_docs_sync.py"
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "--all" in content

    def test_script_recognizes_code_files(self):
        path = PROJECT_ROOT / "scripts" / "check_docs_sync.py"
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "app/**/*.py" in content
        assert "templates" in content
        assert "static" in content

    def test_script_recognizes_doc_files(self):
        path = PROJECT_ROOT / "scripts" / "check_docs_sync.py"
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "CHANGELOG.md" in content
        assert "dev-log.md" in content
        assert "README.md" in content

    def test_script_checks_version_change(self):
        path = PROJECT_ROOT / "scripts" / "check_docs_sync.py"
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "app/config.py" in content
        assert "VERSION" in content or "config_changed" in content

    def test_script_checks_ui_changes(self):
        path = PROJECT_ROOT / "scripts" / "check_docs_sync.py"
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "ui-information-architecture" in content

    def test_script_runnable_all_mode(self):
        """Test that --all mode runs without error."""
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts" / "check_docs_sync.py"), "--all"],
            capture_output=True, text=True, cwd=PROJECT_ROOT, timeout=30
        )
        # --all mode should always succeed (all tracked files exist and is valid check)
        assert result.returncode == 0, f"check_docs_sync.py --all failed: {result.stderr}"
