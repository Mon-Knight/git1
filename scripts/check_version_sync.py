#!/usr/bin/env python
"""
AI World Engine - Version Consistency Checker
Verifies that VERSION in app/config.py matches all documentation files.

Usage:
  python scripts/check_version_sync.py
"""

import os
import sys
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def get_config_version():
    """Extract VERSION from app/config.py."""
    config_path = PROJECT_ROOT / "app" / "config.py"
    if not config_path.is_file():
        print(f"ERROR: app/config.py not found at {config_path}")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Match: VERSION: str = "1.7.11.2"
    match = re.search(r'VERSION\s*:\s*str\s*=\s*"([^"]+)"', content)
    if not match:
        print("ERROR: Could not find VERSION in app/config.py")
        sys.exit(1)

    return match.group(1)


def check_file_for_version(filepath, version):
    """Check if a file contains the version string."""
    if not filepath.is_file():
        return False, "File not found"

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return False, f"Error reading file: {e}"

    if version in content:
        return True, "OK"
    else:
        return False, f"Version '{version}' not found in {filepath}"


def main():
    version = get_config_version()
    print(f"Current VERSION: {version}")
    print()

    checks = [
        (PROJECT_ROOT / "README.md", "README.md"),
        (PROJECT_ROOT / "CHANGELOG.md", "CHANGELOG.md"),
        (PROJECT_ROOT / "docs" / "dev-log.md", "docs/dev-log.md"),
        (PROJECT_ROOT / "docs" / "project" / "version-roadmap.md", "docs/project/version-roadmap.md"),
    ]

    all_ok = True
    for filepath, label in checks:
        ok, msg = check_file_for_version(filepath, version)
        if ok:
            print(f"  OK: {label} contains '{version}'")
        else:
            print(f"  FAIL: {label} - {msg}")
            all_ok = False

    print()
    if all_ok:
        print("Version consistency check: PASSED")
        sys.exit(0)
    else:
        print("Version consistency check: FAILED")
        print(f"Please update the above files to include version '{version}'.")
        sys.exit(1)


if __name__ == "__main__":
    main()
