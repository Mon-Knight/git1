"""
Tests for Markdown file encoding integrity.
"""

import os
import subprocess
import sys


def test_check_encoding_script_exists():
    """Test that the encoding check script exists."""
    script_path = os.path.join("scripts", "check_encoding.py")
    assert os.path.exists(script_path), f"{script_path} not found"


def test_check_encoding_script_runs():
    """Test that the encoding check script runs and returns 0."""
    result = subprocess.run(
        [sys.executable, "scripts/check_encoding.py"],
        capture_output=True, text=True, cwd="f:/git"
    )
    assert result.returncode == 0, f"check_encoding.py failed:\n{result.stdout}\n{result.stderr}"


def test_readme_is_valid_utf8():
    """Test that README.md can be read as UTF-8 without errors."""
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
    assert len(content) > 0
    assert "AI World Engine" in content


def test_readme_no_replacement_chars():
    """Test that README.md contains no U+FFFD replacement characters."""
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
    assert "\ufffd" not in content, "README.md contains replacement characters"


def test_changelog_is_valid_utf8():
    """Test that CHANGELOG.md can be read as UTF-8."""
    with open("CHANGELOG.md", "r", encoding="utf-8") as f:
        content = f.read()
    assert len(content) > 0
    assert "\ufffd" not in content


def test_docs_files_are_valid_utf8():
    """Test that all docs/*.md files are valid UTF-8."""
    docs_dir = "docs"
    for filename in os.listdir(docs_dir):
        if filename.endswith(".md"):
            filepath = os.path.join(docs_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            assert "\ufffd" not in content, f"{filepath} contains replacement characters"


def test_copilot_instructions_is_valid_utf8():
    """Test that .github/copilot-instructions.md is valid UTF-8."""
    filepath = ".github/copilot-instructions.md"
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    assert len(content) > 0
    assert "\ufffd" not in content


def test_readme_contains_required_sections():
    """Test that README.md contains all required sections."""
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    required = [
        "AI World Engine",
        "v1.7.8.2",
        "技术栈",
        "当前核心能力",
        "快速开始",
        "Windows EXE",
        "页面入口",
        "AI 模式与配置",
        "核心规则",
        "当前版本路线",
        "项目结构",
        "测试与构建",
        "当前限制",
        "文档索引",
    ]
    for section in required:
        assert section in content, f"Missing section: {section}"
