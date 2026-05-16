"""
AI World Engine - Desktop Build Verification Script
Validates that the PyInstaller dist contains correct templates and modules.
Run after building: python scripts/verify_desktop_build.py

Usage:
  python scripts/verify_desktop_build.py            # Check dist/ (default)
  python scripts/verify_desktop_build.py --src       # Check source files
  python scripts/verify_desktop_build.py --all       # Check both
"""

import os
import sys
import argparse

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST_DIR = os.path.join(PROJECT_ROOT, "dist", "AIWorldEngine")
INTERNAL_DIR = os.path.join(DIST_DIR, "_internal")

# Required keywords in homepage template
HOMEPAGE_KEYWORDS = [
    ("创作工作台", "Dashboard title"),
    ("数据概览", "Dashboard overview section"),
    ("/settings/ai", "AI settings link"),
    ("toggleSidebarGroup", "Sidebar JS function"),
    ("当前世界", "Current world section"),
]

# Required templates that must exist
REQUIRED_TEMPLATES = [
    "app/templates/index.html",
    "app/templates/base.html",
    "app/templates/settings/ai.html",
    "app/static/css/dashboard.css",
    "app/static/css/app-shell.css",
    "app/templates/simulation/index.html",
    "app/templates/novel/form.html",
    "app/templates/novel/evolution_form.html",
    "app/templates/novel/evolutions.html",
    "app/templates/novel/evolution_detail.html",
    "app/templates/data/index.html",
    "app/templates/data/import.html",
    "app/templates/data/backups.html",
    "app/templates/data/export_result.html",
    "app/templates/data/export.html",
    "app/static/js/export-center.js",
    "app/static/js/sidebar.js",
    "app/templates/context/index.html",
    "app/templates/context/styles.html",
    "app/templates/context/style_form.html",
    "app/templates/context/anchors.html",
    "app/templates/context/anchor_form.html",
    "app/templates/context/packages.html",
    "app/templates/context/package_form.html",
    "app/templates/context/package_detail.html",
    "app/templates/setting_suggestions/index.html",
    "app/templates/setting_suggestions/new.html",
    "app/templates/setting_suggestions/detail.html",
    "app/templates/setting_suggestions/edit_adopt.html",
    # v1.8.0 Volume Outlines
    "app/templates/volume_outlines/index.html",
    "app/templates/volume_outlines/new.html",
    "app/templates/volume_outlines/detail.html",
    "app/templates/volume_outlines/edit.html",
    # v1.9.0 Chapter Outlines
    "app/templates/chapter_outlines/index.html",
    "app/templates/chapter_outlines/new.html",
    "app/templates/chapter_outlines/detail.html",
    "app/templates/chapter_outlines/edit.html",
    # v2.0.0 Novel Drafts
    "app/templates/novel_drafts/index.html",
    "app/templates/novel_drafts/new.html",
    "app/templates/novel_drafts/detail.html",
    "app/templates/novel_drafts/edit.html",
    # v2.0.1 Novel Engineering Overview
    "app/templates/novel/overview.html",
    # v2.1.0 Novel Quality Reports
    "app/templates/novel_quality_reports/index.html",
    "app/templates/novel_quality_reports/draft_reports.html",
    "app/templates/novel_quality_reports/new.html",
    "app/templates/novel_quality_reports/detail.html",
    # v2.2.0 Novel Revisions
    "app/templates/novel_revisions/index.html",
    "app/templates/novel_revisions/draft_revisions.html",
    "app/templates/novel_revisions/new.html",
    "app/templates/novel_revisions/detail.html",
    "app/templates/novel_revisions/edit.html",
    # v2.3.0 Novel Versions
    "app/templates/novel_versions/draft_versions.html",
    "app/templates/novel_versions/compare.html",
    "app/templates/novel_versions/final_drafts.html",
    "app/templates/novel_versions/final_detail.html",
    # v2.4.0 Style Import
    "app/templates/context/style_import.html",
    "app/templates/context/style_detail.html",
]

# v2.0.1: Sidebar navigation keywords (base.html)
SIDEBAR_KEYWORDS_V201 = [
    ("小说工程", "Novel Engineering in sidebar"),
    ("世界设定", "World Settings in sidebar"),
    ("质量检查", "Quality Check in sidebar"),
    ("数据与导出", "Data & Export in sidebar"),
    ("创作资产", "Creative Assets in sidebar"),
    ("AI 推演", "AI Simulation in sidebar"),
    ("后续开放", "Future items indicator"),
]

# Sidebar related checks (in base.html)
SIDEBAR_CHECKS = [
    ("sidebar-subnav-divider", "Sidebar subnav divider"),
    ("showSettingsCategory", "Settings category JS function"),
    ("onclick=\"showSettingsCategory", "Settings category onclick handler"),
]

# Settings page checks (in settings/ai.html)
SETTINGS_PAGE_CHECKS = [
    ("settings-cat-section", "Settings category section class"),
    ("data-settings-cat", "Settings category data attributes"),
]

# Required hidden import modules
AI_MODULES = [
    "app/services/ai/__init__.py",
    "app/services/ai/base.py",
    "app/services/ai/errors.py",
    "app/services/ai/mock_client.py",
    "app/services/ai/openai_compatible_client.py",
    "app/services/ai/model_router.py",
    "app/services/ai/prompt_builder.py",
    "app/services/ai/response_parser.py",
    # v1.8.0 Volume Outlines
    "app/routes/volume_outlines.py",
    "app/services/volume_outline_service.py",
    # v1.9.0 Chapter Outlines
    "app/routes/chapter_outlines.py",
    "app/services/chapter_outline_service.py",
    # v2.0.0 Novel Drafts
    "app/routes/novel_drafts.py",
    "app/services/novel_draft_service.py",
    # v2.1.0 Novel Quality Reports
    "app/routes/novel_quality_reports.py",
    "app/services/novel_quality_service.py",
    # v2.2.0 Novel Revisions
    "app/routes/novel_revisions.py",
    "app/services/novel_revision_service.py",
    # v2.3.0 Novel Versions
    "app/routes/novel_versions.py",
    "app/services/novel_version_service.py",
    # v2.5.0 Novel Continuity
    "app/services/novel_continuity_service.py",
    "app/routes/novel_continuity.py",
    "app/templates/novel_continuity/index.html",
    "app/templates/novel_continuity/new.html",
    "app/templates/novel_continuity/detail.html",
    # v2.6.0 Volume Exports
    "app/services/novel_volume_export_service.py",
    "app/routes/novel_volume_exports.py",
    "app/templates/novel_volume_exports/index.html",
    "app/templates/novel_volume_exports/detail.html",
    "app/templates/novel_volume_exports/preview.html",
    "app/templates/novel_volume_exports/exports.html",
    "app/templates/novel_volume_exports/export_detail.html",
    # v2.4.0 Style Import
    "app/services/style_import_service.py",
    # v2.4.2 Model Formatters
    "app/services/model_formatters.py",
]


def check_source_templates():
    """Check that source templates contain required content."""
    print("\n=== Source Template Check ===")
    errors = []
    for keyword, desc in HOMEPAGE_KEYWORDS:
        # Check both index.html and base.html
        src_path = os.path.join(PROJECT_ROOT, "app", "templates", "index.html")
        base_path = os.path.join(PROJECT_ROOT, "app", "templates", "base.html")
        with open(src_path, "r", encoding="utf-8") as f:
            content = f.read()
        if os.path.isfile(base_path):
            with open(base_path, "r", encoding="utf-8") as f:
                content += f.read()
        if keyword in content:
            print(f"  OK: {desc} → '{keyword}'")
        else:
            print(f"  FAIL: {desc} → '{keyword}' NOT found")
            errors.append(f"Source missing: {keyword}")

    for tpl in REQUIRED_TEMPLATES:
        path = os.path.join(PROJECT_ROOT, tpl)
        if os.path.isfile(path):
            print(f"  OK: {tpl} exists")
        else:
            print(f"  FAIL: {tpl} missing")
            errors.append(f"Missing source template: {tpl}")

    # Check required python modules
    for module_path in AI_MODULES:
        path = os.path.join(PROJECT_ROOT, module_path)
        if os.path.isfile(path):
            print(f"  OK: {module_path} exists")
        else:
            print(f"  FAIL: {module_path} missing")
            errors.append(f"Missing module: {module_path}")

    # Check world detail page has module groups
    detail_path = os.path.join(PROJECT_ROOT, "app", "templates", "worlds", "detail.html")
    if os.path.isfile(detail_path):
        with open(detail_path, "r", encoding="utf-8") as f:
            detail_html = f.read()
        # Check module group navigation
        module_group_checks = [
            ("功能分组导航", "module group nav section"),
            ("设定库", "world library group"),
            ("剧情历史", "story history group"),
            ("AI 推演", "AI simulation group"),
            ("小说工程", "novel engineering group"),
            ("正文草稿", "novel drafts entry"),
            ("创作资产", "creative assets group"),
            ("质量检查", "checks group"),
            ("数据与设置", "data & settings group"),
            ("module-group-link disabled", "disabled future link class"),
            ("dashboard-subnav", "secondary navigation"),
        ]
        for keyword, desc in module_group_checks:
            if keyword in detail_html:
                print(f"  OK: world detail page has '{desc}'")
            else:
                print(f"  FAIL: world detail page missing '{desc}'")
                errors.append(f"World detail missing: {keyword}")
        if "/novel" in detail_html or "/全书演化" in detail_html:
            print("  OK: world detail page has novel engineering entry")
        else:
            print("  FAIL: world detail page missing novel engineering entry")
            errors.append("World detail missing /novel entry")
        if "/context" in detail_html and "创作上下文" in detail_html:
            print("  OK: world detail page has creative context entry")
        else:
            print("  FAIL: world detail page missing creative context entry")
            errors.append("World detail missing /context entry")
        # v1.9.0 Chapter Outlines
        if "章节大纲" in detail_html:
            print("  OK: world detail page has chapter outlines entry")
        else:
            print("  FAIL: world detail page missing chapter outlines entry")
            errors.append("World detail missing: 章节大纲")
        # v2.0.0 Novel Drafts
        if "正文草稿" in detail_html:
            print("  OK: world detail page has novel drafts entry")
        else:
            print("  FAIL: world detail page missing novel drafts entry")
            errors.append("World detail missing: 正文草稿")

    # Check sidebar and settings features
    base_path = os.path.join(PROJECT_ROOT, "app", "templates", "base.html")
    if os.path.isfile(base_path):
        with open(base_path, "r", encoding="utf-8") as f:
            base_html = f.read()
        for keyword, desc in SIDEBAR_CHECKS:
            if keyword in base_html:
                print(f"  OK: base.html has '{desc}'")
            else:
                print(f"  FAIL: base.html missing '{desc}'")
                errors.append(f"base.html missing: {keyword}")

        # v2.0.1: Check new navigation terms
        for keyword, desc in SIDEBAR_KEYWORDS_V201:
            if keyword in base_html:
                print(f"  OK: base.html has '{desc}'")
            else:
                print(f"  FAIL: base.html missing '{desc}'")
                errors.append(f"base.html v2.0.1 missing: {keyword}")

        # v2.0.1: No bad links
        if "/None/" in base_html:
            print("  FAIL: base.html contains /None/ links")
            errors.append("base.html contains /None/ links")
        else:
            print("  OK: base.html has no /None/ links")

    sidebar_js_path = os.path.join(PROJECT_ROOT, "app", "static", "js", "sidebar.js")
    if os.path.isfile(sidebar_js_path):
        with open(sidebar_js_path, "r", encoding="utf-8") as f:
            sidebar_js = f.read()
        if "showSettingsCategory" in sidebar_js:
            print("  OK: sidebar.js has showSettingsCategory")
        else:
            print("  FAIL: sidebar.js missing showSettingsCategory")
            errors.append("sidebar.js missing showSettingsCategory")

    # Check settings page for category sections
    settings_path = os.path.join(PROJECT_ROOT, "app", "templates", "settings", "ai.html")
    if os.path.isfile(settings_path):
        with open(settings_path, "r", encoding="utf-8") as f:
            settings_html = f.read()
        for keyword, desc in SETTINGS_PAGE_CHECKS:
            if keyword in settings_html:
                print(f"  OK: settings/ai.html has '{desc}'")
            else:
                print(f"  FAIL: settings/ai.html missing '{desc}'")
                errors.append(f"settings/ai.html missing: {keyword}")

    return errors


def check_dist_templates():
    """Check that dist/ packed templates contain required content."""
    print("\n=== Dist Template Check ===")
    errors = []

    if not os.path.isdir(DIST_DIR):
        print(f"  SKIP: dist directory not found: {DIST_DIR}")
        print(f"  Run build_exe.ps1 first to generate dist/")
        return []

    # Check index.html + base.html content
    dist_index = os.path.join(INTERNAL_DIR, "app", "templates", "index.html")
    dist_base = os.path.join(INTERNAL_DIR, "app", "templates", "base.html")
    combined_content = ""
    if os.path.isfile(dist_index):
        with open(dist_index, "r", encoding="utf-8") as f:
            combined_content = f.read()
    if os.path.isfile(dist_base):
        with open(dist_base, "r", encoding="utf-8") as f:
            combined_content += f.read()
    if combined_content:
        for keyword, desc in HOMEPAGE_KEYWORDS:
            if keyword in combined_content:
                print(f"  OK: {desc} → '{keyword}'")
            else:
                print(f"  FAIL: {desc} → '{keyword}' NOT found in packed templates")
                errors.append(f"Packed template missing: {keyword}")
    elif os.path.isfile(dist_index):
        print(f"  OK: app/templates/index.html packed (base.html not found)")
    else:
        print(f"  FAIL: Packed index.html not found at {dist_index}")
        errors.append("Packed index.html not found")

    # Check required templates exist in dist
    for tpl in REQUIRED_TEMPLATES:
        dist_path = os.path.join(INTERNAL_DIR, tpl)
        if os.path.isfile(dist_path):
            print(f"  OK: {tpl} packed")
        else:
            print(f"  FAIL: {tpl} NOT in dist")
            errors.append(f"Missing packed template: {tpl}")

    # Check settings/ai.html content
    settings_path = os.path.join(INTERNAL_DIR, "app", "templates", "settings", "ai.html")
    if os.path.isfile(settings_path):
        with open(settings_path, "r", encoding="utf-8") as f:
            settings_content = f.read()
        if "AI 设置" in settings_content:
            print(f"  OK: settings/ai.html contains 'AI 设置'")
        else:
            print(f"  FAIL: settings/ai.html missing 'AI 设置'")
            errors.append("settings/ai.html missing content")

    return errors


def check_dist_exe():
    """Check that the EXE exists."""
    print("\n=== EXE Check ===")
    exe_path = os.path.join(DIST_DIR, "AIWorldEngine.exe")
    if os.path.isfile(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"  OK: {exe_path} ({size_mb:.1f} MB)")
        return []
    else:
        print(f"  FAIL: EXE not found at {exe_path}")
        return ["EXE not found"]


def main():
    parser = argparse.ArgumentParser(description="Verify AI World Engine desktop build")
    parser.add_argument("--src", action="store_true", help="Check source templates only")
    parser.add_argument("--dist", action="store_true", help="Check dist templates only")
    parser.add_argument("--all", action="store_true", help="Check both source and dist")
    args = parser.parse_args()

    all_errors = []

    if args.src or args.all or not (args.dist):
        all_errors.extend(check_source_templates())

    if args.dist or args.all:
        all_errors.extend(check_dist_exe())
        all_errors.extend(check_dist_templates())

    print("\n" + "=" * 50)
    if all_errors:
        print(f"VERIFICATION FAILED: {len(all_errors)} error(s)")
        for err in all_errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("ALL CHECKS PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
