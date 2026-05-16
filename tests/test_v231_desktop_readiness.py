"""
v2.3.1 — Desktop Readiness Tests
验证 EXE 必要资源、关键模板、路由注册和安全性。
"""

import os, pytest
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent


class TestDesktopReadiness:
    def test_verify_script_exists(self):
        """verify_desktop_build.py 脚本存在."""
        assert (PROJECT_ROOT / "scripts" / "verify_desktop_build.py").exists()

    def test_all_critical_templates_exist(self):
        """所有关键模板文件存在."""
        templates = [
            "app/templates/base.html",
            "app/templates/index.html",
            "app/templates/worlds/list.html",
            "app/templates/worlds/detail.html",
            "app/templates/worlds/new.html",
            "app/templates/worlds/edit.html",
            "app/templates/characters/list.html",
            "app/templates/factions/list.html",
            "app/templates/locations/list.html",
            "app/templates/rules/list.html",
            "app/templates/events/list.html",
            "app/templates/simulation/index.html",
            "app/templates/checks/index.html",
            "app/templates/context/index.html",
            "app/templates/novel/overview.html",
            "app/templates/novel/evolution_form.html",
            "app/templates/novel/evolutions.html",
            "app/templates/volume_outlines/index.html",
            "app/templates/chapter_outlines/index.html",
            "app/templates/novel_drafts/index.html",
            "app/templates/novel_drafts/detail.html",
            "app/templates/novel_quality_reports/index.html",
            "app/templates/novel_quality_reports/detail.html",
            "app/templates/novel_revisions/index.html",
            "app/templates/novel_revisions/detail.html",
            "app/templates/novel_versions/draft_versions.html",
            "app/templates/novel_versions/compare.html",
            "app/templates/novel_versions/final_drafts.html",
            "app/templates/novel_versions/final_detail.html",
            "app/templates/settings/ai.html",
            "app/templates/data/index.html",
        ]
        for t in templates:
            path = PROJECT_ROOT / t
            assert path.exists(), f"缺失关键模板: {t}"

    def test_all_critical_services_exist(self):
        """所有关键服务文件存在."""
        services = [
            "app/services/world_service.py",
            "app/services/dashboard_service.py",
            "app/services/world_dashboard_service.py",
            "app/services/novel_draft_service.py",
            "app/services/novel_quality_service.py",
            "app/services/novel_revision_service.py",
            "app/services/novel_version_service.py",
            "app/services/template_context_service.py",
            "app/services/simulation_service.py",
            "app/services/check_service.py",
            "app/services/character_service.py",
            "app/services/faction_service.py",
            "app/services/location_service.py",
            "app/services/rule_service.py",
            "app/services/event_service.py",
            "app/services/settings_service.py",
        ]
        for s in services:
            assert (PROJECT_ROOT / s).exists(), f"缺失关键服务: {s}"

    def test_base_html_has_version(self, client):
        """base.html 包含版本号."""
        resp = client.get("/")
        assert resp.status_code == 200
        import re
        assert re.search(r'v\d+\.\d+\.\d+', resp.text), "HTML应包含版本号"

    def test_base_html_has_sidebar(self, client):
        """base.html 包含侧边栏."""
        resp = client.get("/")
        assert "sidebar" in resp.text
        assert "app-shell-body" in resp.text

    def test_confidential_info_not_leaked(self, client):
        """不泄露实际 API Key（placeholder sk- 提示不算泄露）."""
        for path in ["/", "/settings/ai", "/worlds"]:
            resp = client.get(path)
            # Check that there's no actual API key value (only placeholder="sk-..." is OK)
            import re
            # Remove placeholder attributes before checking
            cleaned = re.sub(r'placeholder="sk-[^"]*"', '', resp.text)
            assert "sk-" not in cleaned, f"{path} 泄露了真实 API Key 格式内容"
            assert "Authorization" not in resp.text, f"{path} 泄露了 Authorization header"
