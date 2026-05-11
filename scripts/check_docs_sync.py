#!/usr/bin/env python
"""
AI World Engine - Documentation Sync Checker
Checks whether staged changes require corresponding documentation updates.

Usage:
  python scripts/check_docs_sync.py --staged    # Check staged files
  python scripts/check_docs_sync.py --all        # Check all project files (for pre-push)
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# File paths that trigger doc sync requirements
TRIGGER_PATTERNS = [
    "app/**/*.py",
    "app/templates/**/*.html",
    "app/static/**/*.css",
    "app/static/**/*.js",
    "tests/**/*.py",
    "scripts/**/*.py",
    "packaging/**/*.ps1",
    "packaging/**/*.spec",
    "desktop_launcher.py",
    "requirements.txt",
    "app/config.py",
    "docs/**/*.md",
]

# Documentation files
DOC_FILES = [
    "CHANGELOG.md",
    "docs/dev-log.md",
    "README.md",
    "docs/project/version-roadmap.md",
    "docs/project/ui-information-architecture.md",
    "docs/project/test-debt.md",
    "docs/project/git-hooks.md",
    "docs/design/novel-evolution.md",
    "docs/design/context-assets.md",
    "docs/design/setting-suggestions.md",
    "docs/user/quick-start.md",
    "docs/user/desktop-usage.md",
    "docs/user/ai-settings.md",
    "docs/user/data-import-export.md",
    "docs/user/workflow-guide.md",
    "docs/technical/architecture.md",
    "docs/technical/desktop-build.md",
    "docs/technical/deployment.md",
    "docs/technical/database.md",
    "docs/technical/testing.md",
    "docs/technical/api-routes.md",
]


def get_staged_files():
    """Get list of staged files from git."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True, cwd=PROJECT_ROOT, timeout=10
        )
        return [f.strip() for f in result.stdout.split("\n") if f.strip()]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []


def get_all_tracked_files():
    """Get list of all tracked files."""
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            capture_output=True, text=True, cwd=PROJECT_ROOT, timeout=10
        )
        return [f.strip() for f in result.stdout.split("\n") if f.strip()]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []


def matches_pattern(filepath, pattern):
    """Simple glob matching."""
    import fnmatch
    return fnmatch.fnmatch(filepath, pattern)


def is_code_file(filepath):
    """Check if file is a code file that triggers doc sync."""
    for pattern in TRIGGER_PATTERNS:
        if matches_pattern(filepath, pattern):
            return True
    return False


def is_doc_file(filepath):
    """Check if file is a documentation file."""
    for doc in DOC_FILES:
        if filepath == doc or filepath.replace("\\", "/") == doc:
            return True
    return False


def check_docs_sync(changed_files, mode="staged"):
    """Check if changed code files have corresponding doc updates."""
    code_files = [f for f in changed_files if is_code_file(f)]
    doc_files = [f for f in changed_files if is_doc_file(f)]

    if not code_files:
        if mode == "staged":
            print("No code files in staged changes. Skipping doc sync check.")
        return True, []

    # Check for version change
    config_changed = any("app/config.py" in f.replace("\\", "/") for f in code_files)

    required_docs = set()
    warnings = []

    # Basic rule: if code changes, at least CHANGELOG.md or dev-log.md should be updated
    if code_files:
        has_changelog = any("CHANGELOG.md" in f for f in doc_files)
        has_devlog = any("dev-log.md" in f for f in doc_files)
        if not has_changelog and not has_devlog:
            required_docs.add("CHANGELOG.md or docs/dev-log.md")
            warnings.append("Code files modified but CHANGELOG.md and docs/dev-log.md not updated.")

    # Version change: must update all version-bearing docs
    if config_changed:
        for doc in ["CHANGELOG.md", "docs/dev-log.md", "README.md", "docs/project/version-roadmap.md"]:
            has_doc = any(doc in f for f in doc_files)
            if not has_doc:
                required_docs.add(doc)
                warnings.append(f"VERSION changed in app/config.py but {doc} not updated.")

    # UI changes
    ui_patterns = ["templates", "static/css", "static/js"]
    ui_changed = any(
        any(pattern in f for pattern in ui_patterns) for f in code_files
    )
    if ui_changed:
        has_ui_doc = any("ui-information-architecture" in f for f in doc_files)
        if not has_ui_doc:
            warnings.append("UI files modified but docs/project/ui-information-architecture.md not updated.")

    if warnings:
        print("DOCUMENTATION SYNC WARNING:")
        for w in warnings:
            print(f"  - {w}")
        if required_docs:
            print(f"  Required docs: {', '.join(sorted(required_docs))}")
        print()
        print("Please update the relevant documentation files before committing.")
        print("To bypass (emergency only): git commit --no-verify")
        return False, warnings
    else:
        if doc_files and code_files:
            print(f"OK: {len(doc_files)} doc file(s) updated alongside code changes.")
        return True, []


def main():
    parser = argparse.ArgumentParser(description="Check documentation synchronization")
    parser.add_argument("--staged", action="store_true", help="Check staged files only")
    parser.add_argument("--all", action="store_true", help="Check all tracked files")
    args = parser.parse_args()

    if args.staged:
        files = get_staged_files()
        if not files:
            print("No staged files. Skipping doc sync check.")
            sys.exit(0)
        mode = "staged"
    elif args.all:
        files = get_all_tracked_files()
        mode = "all"
        print(f"Checking {len(files)} tracked files...")
    else:
        print("ERROR: Use --staged or --all")
        sys.exit(1)

    ok, warnings = check_docs_sync(files, mode)
    if not ok:
        sys.exit(1)
    else:
        print("Documentation sync check: PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
