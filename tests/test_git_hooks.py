"""
Tests for Git Hooks infrastructure.
"""
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


class TestGitHooksExist:
    """Verify all hook files exist."""

    def test_install_script_exists(self):
        assert (PROJECT_ROOT / "scripts" / "install_git_hooks.py").is_file()

    def test_pre_commit_hook_exists(self):
        assert (PROJECT_ROOT / "scripts" / "git-hooks" / "pre-commit").is_file()

    def test_pre_push_hook_exists(self):
        assert (PROJECT_ROOT / "scripts" / "git-hooks" / "pre-push").is_file()

    def test_install_script_is_valid_python(self):
        path = PROJECT_ROOT / "scripts" / "install_git_hooks.py"
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "def main" in content
        assert "install_git_hooks" in content or "Git Hook Installer" in content


class TestPreCommitContent:
    """Verify pre-commit hook contains expected checks."""

    def test_pre_commit_has_encoding_check(self):
        path = PROJECT_ROOT / "scripts" / "git-hooks" / "pre-commit"
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "check_encoding.py" in content

    def test_pre_commit_has_version_sync(self):
        path = PROJECT_ROOT / "scripts" / "git-hooks" / "pre-commit"
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "check_version_sync.py" in content

    def test_pre_commit_has_docs_sync(self):
        path = PROJECT_ROOT / "scripts" / "git-hooks" / "pre-commit"
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "check_docs_sync.py" in content

    def test_pre_commit_has_compileall(self):
        path = PROJECT_ROOT / "scripts" / "git-hooks" / "pre-commit"
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "compileall" in content


class TestPrePushContent:
    """Verify pre-push hook contains expected checks."""

    def test_pre_push_has_compileall(self):
        path = PROJECT_ROOT / "scripts" / "git-hooks" / "pre-push"
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "compileall" in content

    def test_pre_push_has_encoding_check(self):
        path = PROJECT_ROOT / "scripts" / "git-hooks" / "pre-push"
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "check_encoding.py" in content

    def test_pre_push_has_version_sync(self):
        path = PROJECT_ROOT / "scripts" / "git-hooks" / "pre-push"
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "check_version_sync.py" in content

    def test_pre_push_has_pytest(self):
        path = PROJECT_ROOT / "scripts" / "git-hooks" / "pre-push"
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "pytest" in content

    def test_pre_push_has_verify_build(self):
        path = PROJECT_ROOT / "scripts" / "git-hooks" / "pre-push"
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "verify_desktop_build.py" in content
