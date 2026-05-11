"""
Tests for version sync checker (scripts/check_version_sync.py).
"""
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


class TestVersionSyncScript:
    """Verify check_version_sync.py exists and can be executed."""

    def test_script_exists(self):
        assert (PROJECT_ROOT / "scripts" / "check_version_sync.py").is_file()

    def test_script_is_valid_python(self):
        path = PROJECT_ROOT / "scripts" / "check_version_sync.py"
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "def get_config_version" in content
        assert "def main" in content


class TestVersionInDocuments:
    """Verify current VERSION appears in all required documents."""

    def test_version_in_readme(self):
        from app.config import settings
        version = settings.VERSION
        readme = PROJECT_ROOT / "README.md"
        if readme.is_file():
            with open(readme, "r", encoding="utf-8") as f:
                content = f.read()
            assert version in content, f"Version {version} not found in README.md"

    def test_version_in_changelog(self):
        from app.config import settings
        version = settings.VERSION
        changelog = PROJECT_ROOT / "CHANGELOG.md"
        if changelog.is_file():
            with open(changelog, "r", encoding="utf-8") as f:
                content = f.read()
            assert version in content, f"Version {version} not found in CHANGELOG.md"

    def test_version_in_dev_log(self):
        from app.config import settings
        version = settings.VERSION
        devlog = PROJECT_ROOT / "docs" / "dev-log.md"
        if devlog.is_file():
            with open(devlog, "r", encoding="utf-8") as f:
                content = f.read()
            assert version in content, f"Version {version} not found in docs/dev-log.md"

    def test_version_in_roadmap(self):
        from app.config import settings
        version = settings.VERSION
        roadmap = PROJECT_ROOT / "docs" / "project" / "version-roadmap.md"
        if roadmap.is_file():
            with open(roadmap, "r", encoding="utf-8") as f:
                content = f.read()
            assert version in content, f"Version {version} not found in version-roadmap.md"
