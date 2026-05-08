#!/usr/bin/env python
"""
Check Markdown files for encoding issues (mojibake/garbled characters).
Scans README.md, CHANGELOG.md, docs/*.md, .github/copilot-instructions.md.
Exits with code 1 if any issues found, 0 if all clean.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FILES = [
    "README.md",
    "CHANGELOG.md",
    "docs/dev-log.md",
    "docs/architecture.md",
    "docs/todo.md",
    "docs/security-review.md",
    "docs/decision-log.md",
    ".github/copilot-instructions.md",
]

# Common garbled character patterns found in mojibake
GARBLED_PATTERNS = [
    "\ufffd",   # U+FFFD replacement character
    "\ufffe",   # U+FFFE byte order mark (reversed)
    "\u951f\u65a4\u62f7",  # 锟斤拷
    "\u9489",   # 鈥 (common in GBK->UTF-8 mis-decode)
    "\u9422",   # 鐢
    "\u9716",   # 霖
    "\u7487",   # 璇
    "\u95c8",   # 闈
    "\u93c3",   # 鏃
    "\u6d93",   # 涓
    "\u93c4",   # 鏄
]


def check_file(filepath: str) -> list:
    """Check a file for encoding issues. Returns list of issues found."""
    issues = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
    except UnicodeDecodeError as e:
        return [f"Cannot decode as UTF-8: {e}"]
    except Exception as e:
        return [f"Error reading file: {e}"]

    for pattern in GARBLED_PATTERNS:
        if pattern in text:
            count = text.count(pattern)
            issues.append(f"Found garbled pattern (U+{ord(pattern):04X}) {count} time(s)")

    return issues


def main():
    all_ok = True
    for rel_path in FILES:
        filepath = os.path.join(BASE_DIR, rel_path)
        if not os.path.exists(filepath):
            print(f"SKIP (not found): {rel_path}")
            continue

        issues = check_file(filepath)
        if issues:
            all_ok = False
            print(f"FAIL: {rel_path}")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print(f"OK: {rel_path}")

    if all_ok:
        print("\nAll Markdown files passed encoding check.")
        return 0
    else:
        print("\nSome files have encoding issues. Please fix them.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
