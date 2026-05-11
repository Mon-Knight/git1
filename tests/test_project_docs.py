"""
AI World Engine - Test Project Documentation
Ensures required project docs exist and contain required content.
"""

import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read_doc(filename: str) -> str:
    path = os.path.join(PROJECT_ROOT, "docs", filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _read_root(filename: str) -> str:
    path = os.path.join(PROJECT_ROOT, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class TestDocExistence:
    """Tests that required documentation files exist."""

    def test_development_rules_exists(self):
        path = os.path.join(PROJECT_ROOT, "docs", "project", "development-rules.md")
        assert os.path.isfile(path), "docs/project/development-rules.md not found"

    def test_version_roadmap_exists(self):
        path = os.path.join(PROJECT_ROOT, "docs", "project", "version-roadmap.md")
        assert os.path.isfile(path), "docs/project/version-roadmap.md not found"

    def test_ui_information_architecture_exists(self):
        path = os.path.join(PROJECT_ROOT, "docs", "project", "ui-information-architecture.md")
        assert os.path.isfile(path), "docs/project/ui-information-architecture.md not found"

    def test_agent_task_rules_exists(self):
        path = os.path.join(PROJECT_ROOT, "docs", "project", "agent-task-rules.md")
        assert os.path.isfile(path), "docs/project/agent-task-rules.md not found"

    def test_module_boundaries_exists(self):
        path = os.path.join(PROJECT_ROOT, "docs", "project", "module-boundaries.md")
        assert os.path.isfile(path), "docs/project/module-boundaries.md not found"


class TestDocContent:
    """Tests that documentation contains required content."""

    def test_readme_contains_version(self):
        content = _read_root("README.md")
        assert "v1.7.8.2" in content, "README.md missing v1.7.8.2"

    def test_changelog_contains_version(self):
        content = _read_root("CHANGELOG.md")
        assert "v1.7.8.2" in content, "CHANGELOG.md missing v1.7.8.2"

    def test_version_roadmap_contains_v172(self):
        content = _read_doc("project/version-roadmap.md")
        assert "v1.7.2" in content, "version-roadmap.md missing v1.7.2"

    def test_version_roadmap_contains_v173(self):
        content = _read_doc("project/version-roadmap.md")
        assert "v1.7.3" in content, "version-roadmap.md missing v1.7.3"

    def test_version_roadmap_contains_v176(self):
        content = _read_doc("project/version-roadmap.md")
        assert "v1.7.8.2" in content, "version-roadmap.md missing v1.7.8.2"

    def test_version_roadmap_contains_v180(self):
        content = _read_doc("project/version-roadmap.md")
        assert "v1.8.0" in content, "version-roadmap.md missing v1.8.0"

    def test_development_rules_has_no_auto_canon(self):
        content = _read_doc("project/development-rules.md")
        assert "AI 生成结果不能自动写入正史" in content or "AI 结果不能自动写入正史" in content, \
            "development-rules.md missing auto-canon prohibition"

    def test_agent_task_rules_has_no_delete_routes(self):
        content = _read_doc("project/agent-task-rules.md")
        assert "旧路由不能删除" in content or "不能删除旧路由" in content, \
            "agent-task-rules.md missing route deletion prohibition"

    def test_development_rules_has_no_delete_tests(self):
        content = _read_doc("project/development-rules.md")
        assert "旧测试不能删除" in content, \
            "development-rules.md missing test deletion prohibition"
