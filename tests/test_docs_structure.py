"""
AI World Engine - Test Documentation Structure
Ensures the docs directory has the expected structure after v1.7.6 restructuring.
"""

import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read_root(filename: str) -> str:
    path = os.path.join(PROJECT_ROOT, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _path_exists(rel_path: str) -> bool:
    return os.path.exists(os.path.join(PROJECT_ROOT, rel_path))


class TestDocsStructure:
    """Tests that the restructured docs directory has the expected files."""

    # --- Root-level docs ---

    def test_readme_contains_v176(self):
        content = _read_root("README.md")
        assert "v1.7.9" in content, "README.md missing v1.7.9"

    def test_changelog_contains_v176(self):
        content = _read_root("CHANGELOG.md")
        assert "v1.7.9" in content, "CHANGELOG.md missing v1.7.9"

    def test_changelog_contains_v175(self):
        content = _read_root("CHANGELOG.md")
        assert "v1.7.5" in content, "CHANGELOG.md missing v1.7.5"

    # --- Docs index ---

    def test_docs_readme_exists(self):
        assert _path_exists("docs/README.md"), "docs/README.md not found"

    # --- User docs ---

    def test_docs_user_dir_exists(self):
        assert _path_exists("docs/user"), "docs/user directory not found"

    def test_docs_user_quick_start_exists(self):
        assert _path_exists("docs/user/quick-start.md"), "docs/user/quick-start.md not found"

    def test_docs_user_desktop_usage_exists(self):
        assert _path_exists("docs/user/desktop-usage.md"), "docs/user/desktop-usage.md not found"

    def test_docs_user_ai_settings_exists(self):
        assert _path_exists("docs/user/ai-settings.md"), "docs/user/ai-settings.md not found"

    def test_docs_user_data_import_export_exists(self):
        assert _path_exists("docs/user/data-import-export.md"), "docs/user/data-import-export.md not found"

    def test_docs_user_workflow_guide_exists(self):
        assert _path_exists("docs/user/workflow-guide.md"), "docs/user/workflow-guide.md not found"

    # --- Project docs ---

    def test_docs_project_dir_exists(self):
        assert _path_exists("docs/project"), "docs/project directory not found"

    def test_docs_project_version_roadmap_exists(self):
        assert _path_exists("docs/project/version-roadmap.md"), "docs/project/version-roadmap.md not found"

    def test_docs_project_module_boundaries_exists(self):
        assert _path_exists("docs/project/module-boundaries.md"), "docs/project/module-boundaries.md not found"

    def test_docs_project_ui_info_architecture_exists(self):
        assert _path_exists("docs/project/ui-information-architecture.md"), "docs/project/ui-information-architecture.md not found"

    def test_docs_project_development_rules_exists(self):
        assert _path_exists("docs/project/development-rules.md"), "docs/project/development-rules.md not found"

    def test_docs_project_agent_task_rules_exists(self):
        assert _path_exists("docs/project/agent-task-rules.md"), "docs/project/agent-task-rules.md not found"

    def test_docs_project_release_history_exists(self):
        assert _path_exists("docs/project/release-history.md"), "docs/project/release-history.md not found"

    # --- Technical docs ---

    def test_docs_technical_dir_exists(self):
        assert _path_exists("docs/technical"), "docs/technical directory not found"

    def test_docs_technical_desktop_build_exists(self):
        assert _path_exists("docs/technical/desktop-build.md"), "docs/technical/desktop-build.md not found"

    def test_docs_technical_deployment_exists(self):
        assert _path_exists("docs/technical/deployment.md"), "docs/technical/deployment.md not found"

    def test_docs_technical_database_exists(self):
        assert _path_exists("docs/technical/database.md"), "docs/technical/database.md not found"

    def test_docs_technical_testing_exists(self):
        assert _path_exists("docs/technical/testing.md"), "docs/technical/testing.md not found"

    def test_docs_technical_api_routes_exists(self):
        assert _path_exists("docs/technical/api-routes.md"), "docs/technical/api-routes.md not found"

    # --- Design docs ---

    def test_docs_design_dir_exists(self):
        assert _path_exists("docs/design"), "docs/design directory not found"

    def test_docs_design_context_assets_exists(self):
        assert _path_exists("docs/design/context-assets.md"), "docs/design/context-assets.md not found"

    def test_docs_design_novel_engineering_exists(self):
        assert _path_exists("docs/design/novel-engineering.md"), "docs/design/novel-engineering.md not found"

    def test_docs_design_setting_suggestions_exists(self):
        assert _path_exists("docs/design/setting-suggestions.md"), "docs/design/setting-suggestions.md not found"

    def test_docs_design_future_interactive_story_exists(self):
        assert _path_exists("docs/design/future-interactive-story.md"), "docs/design/future-interactive-story.md not found"
