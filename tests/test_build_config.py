"""
AI World Engine - Test Build Configuration
Tests to verify that PyInstaller spec and build scripts include
all necessary AI service modules and templates.
"""

import os
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read_file(rel_path: str) -> str:
    path = os.path.join(PROJECT_ROOT, rel_path)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def test_spec_includes_ai_templates():
    """AIWorldEngine.spec should include app/templates in datas."""
    content = _read_file("packaging/AIWorldEngine.spec")
    assert "app/templates" in content


def test_spec_includes_static():
    """AIWorldEngine.spec should include app/static in datas."""
    content = _read_file("packaging/AIWorldEngine.spec")
    assert "app/static" in content


def test_spec_includes_ai_hidden_imports():
    """AIWorldEngine.spec should include AI service hidden imports."""
    content = _read_file("packaging/AIWorldEngine.spec")
    required_imports = [
        "app.services.ai",
        "app.services.ai.base",
        "app.services.ai.mock_client",
        "app.services.ai.openai_compatible_client",
        "app.services.ai.model_router",
        "app.services.ai.prompt_builder",
        "app.services.ai.response_parser",
        "app.services.settings_service",
    ]
    for imp in required_imports:
        assert imp in content, f"hidden import '{imp}' missing from spec file"


def test_spec_includes_basic_hidden_imports():
    """AIWorldEngine.spec should include uvicorn and sqlalchemy hidden imports."""
    content = _read_file("packaging/AIWorldEngine.spec")
    assert "uvicorn.logging" in content
    assert "uvicorn.loops.auto" in content
    assert "sqlalchemy.sql.default_comparator" in content


def test_build_script_includes_ai_modules():
    """build_exe.ps1 should include AI service hidden imports."""
    content = _read_file("packaging/build_exe.ps1")
    required_imports = [
        "app.services.ai",
        "app.services.ai.base",
        "app.services.ai.model_router",
        "app.services.settings_service",
    ]
    for imp in required_imports:
        assert imp in content, f"hidden import '{imp}' missing from build_exe.ps1"


def test_build_script_includes_dlls():
    """build_exe.ps1 should include required DLL binaries."""
    content = _read_file("packaging/build_exe.ps1")
    assert "libssl" in content
    assert "libcrypto" in content
    assert "sqlite3.dll" in content


def test_build_script_cleans_old_build():
    """build_exe.ps1 should have a clean step."""
    content = _read_file("packaging/build_exe.ps1")
    assert "Remove-Item" in content or "clean" in content.lower()
    assert "build" in content


def test_desktop_launcher_includes_ai_imports():
    """desktop_launcher.py should import all AI services for PyInstaller analysis."""
    content = _read_file("desktop_launcher.py")
    required_imports = [
        "app.services.ai.base",
        "app.services.ai.mock_client",
        "app.services.ai.openai_compatible_client",
        "app.services.ai.model_router",
        "app.services.ai.prompt_builder",
        "app.services.ai.response_parser",
        "app.services.settings_service",
        "app.routes.settings",
    ]
    for imp in required_imports:
        assert imp in content, f"PyInstaller import '{imp}' missing from desktop_launcher.py"


def test_dist_not_in_gitignore():
    """dist/ and build/ should be in .gitignore."""
    content = _read_file(".gitignore")
    assert "dist/" in content
    assert "build/" in content


def test_env_not_in_gitignore():
    """.env should be in .gitignore."""
    content = _read_file(".gitignore")
    assert ".env" in content


def test_db_not_in_gitignore():
    """"*.db" should be in .gitignore."""
    content = _read_file(".gitignore")
    assert "*.db" in content


def test_project_backups_in_gitignore():
    """.project_backups/ should be in .gitignore."""
    content = _read_file(".gitignore")
    assert ".project_backups/" in content


def test_desktop_readme_exists():
    """README-Desktop.txt should exist in packaging/."""
    path = os.path.join(PROJECT_ROOT, "packaging", "README-Desktop.txt")
    assert os.path.isfile(path), "README-Desktop.txt missing from packaging/"


def test_desktop_readme_contains_key_info():
    """README-Desktop.txt should contain essential distribution info."""
    content = _read_file("packaging/README-Desktop.txt")
    assert "AIWorldEngine.exe" in content
    assert "AppData" in content
    assert "AI 设置" in content or "settings/ai" in content
    assert "Mock AI" in content
    assert "error.log" in content
