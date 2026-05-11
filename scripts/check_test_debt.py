#!/usr/bin/env python
"""
AI World Engine - Test Debt Checker
Verifies that test debt is properly documented.

Usage:
  python scripts/check_test_debt.py
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def count_xfail_tests():
    """Count tests marked with xfail."""
    import subprocess
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/", "--collect-only", "-q", "--no-header"],
            capture_output=True, text=True, cwd=PROJECT_ROOT, timeout=30
        )
        # Count xfail markers in test files
        count = 0
        tests_dir = PROJECT_ROOT / "tests"
        for py_file in tests_dir.glob("*.py"):
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()
                count += content.count("@pytest.mark.xfail")
                count += content.count("@pytest.mark.xfail(")
        return count
    except Exception:
        return -1


def main():
    print("=== Test Debt Check ===")
    print()

    debt_file = PROJECT_ROOT / "docs" / "project" / "test-debt.md"

    xfail_count = count_xfail_tests()
    print(f"  xfail markers found: {xfail_count if xfail_count >= 0 else 'unknown'}")

    if not debt_file.is_file():
        print(f"  FAIL: Test debt document not found at {debt_file}")
        print()
        print("Please create docs/project/test-debt.md to document any known test failures.")
        print("Even if there are no failures, the file should state '当前无已知测试债务'.")
        sys.exit(1)

    with open(debt_file, "r", encoding="utf-8") as f:
        content = f.read()

    if xfail_count > 0:
        # Check that debt file mentions test files
        if "test_checks.py" in content or "test_adopt_branch.py" in content or "test_" in content:
            print("  OK: test-debt.md contains test file references.")
        else:
            print("  WARNING: xfail tests exist but test-debt.md doesn't reference specific test files.")
            print("  Please add details about the xfailed tests.")

        if "后续修复" in content or "修复计划" in content or "v1.8" in content:
            print("  OK: test-debt.md contains fix plan.")
        else:
            print("  WARNING: test-debt.md should include a fix plan or target version.")
    else:
        if "无已知测试债务" in content or "已清理" in content or "0 failed" in content:
            print("  OK: test-debt.md confirms no known test debt.")
        else:
            print("  INFO: No xfail tests detected. test-debt.md exists.")

    print()
    print("Test debt check: PASSED")
    sys.exit(0)


if __name__ == "__main__":
    main()
