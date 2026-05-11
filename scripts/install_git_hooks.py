#!/usr/bin/env python
"""
AI World Engine - Git Hook Installer
Installs pre-commit and pre-push hooks from scripts/git-hooks/ to .git/hooks/.
Usage: python scripts/install_git_hooks.py
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
HOOKS_SRC_DIR = PROJECT_ROOT / "scripts" / "git-hooks"
HOOKS_TARGET_DIR = PROJECT_ROOT / ".git" / "hooks"

HOOKS = ["pre-commit", "pre-push"]


def main():
    print("=== AI World Engine - Git Hook Installer ===")
    print()

    if not (PROJECT_ROOT / ".git").is_dir():
        print("ERROR: .git directory not found. Are you in the project root?")
        print(f"Expected .git at: {PROJECT_ROOT / '.git'}")
        sys.exit(1)

    HOOKS_TARGET_DIR.mkdir(parents=True, exist_ok=True)

    installed = 0
    for hook_name in HOOKS:
        src = HOOKS_SRC_DIR / hook_name
        dst = HOOKS_TARGET_DIR / hook_name

        if not src.is_file():
            print(f"WARNING: Hook source not found: {src}")
            continue

        # Backup existing hook
        if dst.exists():
            backup_name = f"{hook_name}.bak-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            backup_path = HOOKS_TARGET_DIR / backup_name
            shutil.copy2(dst, backup_path)
            print(f"  Backed up existing hook to: {backup_name}")

        # Copy hook
        shutil.copy2(src, dst)
        # Ensure executable (POSIX) - Windows Git Bash reads the shebang
        try:
            dst.chmod(0o755)
        except (OSError, PermissionError):
            pass  # Windows doesn't support chmod, but Git Bash handles .sh with shebang

        print(f"  Installed: {dst}")
        installed += 1

    print()
    if installed == len(HOOKS):
        print(f"SUCCESS: {installed} hook(s) installed.")
    else:
        print(f"WARNING: Only {installed}/{len(HOOKS)} hooks installed.")

    print()
    print("Hook check contents:")
    print("  pre-commit: Lightweight checks (encoding, version sync, docs sync, compileall)")
    print("  pre-push:    Full quality gate (compileall, encoding, version sync, docs sync,")
    print("               verify_desktop_build, pytest)")
    print()
    print("To skip hooks temporarily:")
    print("  git commit --no-verify")
    print("  git push --no-verify")
    print("(Only use in emergencies or when hooks themselves are broken)")


if __name__ == "__main__":
    main()
