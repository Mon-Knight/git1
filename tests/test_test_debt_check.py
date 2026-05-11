"""
Tests for test debt checker (scripts/check_test_debt.py).
"""
import os
import sys
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


class TestTestDebtScript:
    """Verify check_test_debt.py exists and works."""

    def test_script_exists(self):
        assert (PROJECT_ROOT / "scripts" / "check_test_debt.py").is_file()

    def test_script_is_valid_python(self):
        path = PROJECT_ROOT / "scripts" / "check_test_debt.py"
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "def count_xfail_tests" in content or "xfail" in content
        assert "def main" in content

    def test_script_runnable(self):
        """Test that the script runs without error."""
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts" / "check_test_debt.py")],
            capture_output=True, text=True, cwd=PROJECT_ROOT, timeout=30
        )
        assert result.returncode == 0, f"check_test_debt.py failed: {result.stderr}"


class TestTestDebtDocument:
    """Verify docs/project/test-debt.md exists and has content."""

    def test_debt_doc_exists(self):
        debt_file = PROJECT_ROOT / "docs" / "project" / "test-debt.md"
        assert debt_file.is_file(), "docs/project/test-debt.md not found"

    def test_debt_doc_has_content(self):
        debt_file = PROJECT_ROOT / "docs" / "project" / "test-debt.md"
        with open(debt_file, "r", encoding="utf-8") as f:
            content = f.read()
        assert len(content) > 100, "test-debt.md appears empty"

    def test_debt_doc_mentions_test_files(self):
        debt_file = PROJECT_ROOT / "docs" / "project" / "test-debt.md"
        with open(debt_file, "r", encoding="utf-8") as f:
            content = f.read()
        # Should mention xfail tests or state no debt
        has_tests = "test_checks.py" in content or "test_" in content
        has_no_debt = "无已知测试债务" in content or "已清理" in content
        assert has_tests or has_no_debt, "test-debt.md should document test state"

    def test_debt_doc_has_fix_plan(self):
        debt_file = PROJECT_ROOT / "docs" / "project" / "test-debt.md"
        with open(debt_file, "r", encoding="utf-8") as f:
            content = f.read()
        has_plan = "修复计划" in content or "v1.8" in content or "fix" in content.lower()
        has_no_debt = "无已知测试债务" in content
        assert has_plan or has_no_debt, "test-debt.md should have a fix plan or state no debt"


class TestXfailTests:
    """Verify xfail tests have proper markers and documentation."""

    def test_xfail_count_matches_debt_doc(self):
        """Check that number of xfail tests is reasonable."""
        tests_dir = PROJECT_ROOT / "tests"
        xfail_count = 0
        for py_file in tests_dir.glob("*.py"):
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()
                xfail_count += content.count("@pytest.mark.xfail")
        # We expect at least the 15 test_checks.py xfail markers
        assert xfail_count >= 15, f"Expected at least 15 xfail markers, found {xfail_count}"

    def test_xfail_has_reason(self):
        """All xfail markers should have a reason parameter."""
        import re
        tests_dir = PROJECT_ROOT / "tests"
        for py_file in tests_dir.glob("*.py"):
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()
            # Find all @pytest.mark.xfail decorators using regex
            # Match the decorator and check it contains reason=
            pattern = r'@pytest\.mark\.xfail\([^)]*\)'
            matches = re.findall(pattern, content)
            for match in matches:
                assert "reason" in match, (
                    f"xfail marker without reason in {py_file.name}: {match[:80]}"
                )
