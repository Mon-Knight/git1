"""
v2.3.1 — Full Creation Flow Smoke Test
验证从新建世界到最终采用稿的完整链路关键页面均可访问。
"""

import pytest, json
from app.database import SessionLocal
from app.services.world_service import WorldService
from app.services.novel_quality_service import NovelQualityService
from app.services.novel_revision_service import NovelRevisionService
from app.services.novel_version_service import NovelVersionService
from app.models import NovelDraft


def _setup_full_chain(db):
    """Create a world with draft -> quality report -> revision -> final draft."""
    w = WorldService.create_world(db, name="验收世界", world_type="科幻", description="全链路验收", current_era="纪元1", tone="冒险")
    db.commit()
    d = NovelDraft(world_id=w.id, chapter_outline_id=1, volume_index=1, chapter_index=1,
                   title="验收草稿", content="验收正文内容。主角出发冒险。", status="candidate")
    db.add(d); db.commit(); db.refresh(d)
    rj = json.dumps({"title":"验收报告","overall_score":85}, ensure_ascii=False)
    qr = NovelQualityService.save_quality_report(db, w.id, d.id, "p", rj)
    rev = NovelRevisionService.save_revision(db, w.id, d.id, qr.id, "p", "润色后正文内容")
    final = NovelVersionService.set_final_version(db, w.id, d.id, "draft", d.id)
    return w.id, d.id, qr.id, rev.id, final.id


class TestFullCreationFlowSmoke:
    """Validate the complete creation chain pages return 200."""

    def test_world_creation(self, client):
        """新建世界可创建."""
        db = SessionLocal()
        try:
            w = WorldService.create_world(db, name="烟雾测试世界", world_type="魔幻", description="T", current_era="纪元1", tone="黑暗")
            db.commit()
            resp = client.get(f"/worlds/{w.id}")
            assert resp.status_code == 200
            assert "烟雾测试世界" in resp.text
        finally: db.rollback(); db.close()

    def test_all_key_pages_200(self, client):
        """完整链路关键页面均返回200."""
        db = SessionLocal()
        try:
            wid, did, qid, rid, fid = _setup_full_chain(db)
            pages = [
                ("/", "首页"),
                ("/worlds", "世界列表"),
                (f"/worlds/{wid}", "世界详情"),
                (f"/worlds/{wid}/characters", "角色"),
                (f"/worlds/{wid}/factions", "势力"),
                (f"/worlds/{wid}/locations", "地点"),
                (f"/worlds/{wid}/rules", "规则"),
                (f"/worlds/{wid}/events", "事件"),
                (f"/worlds/{wid}/context", "创作资产"),
                (f"/worlds/{wid}/simulation", "AI推演"),
                (f"/worlds/{wid}/checks", "检查中心"),
                (f"/worlds/{wid}/novel", "小说工程"),
                (f"/worlds/{wid}/novel/drafts", "正文草稿列表"),
                (f"/worlds/{wid}/novel/drafts/{did}", "正文草稿详情"),
                (f"/worlds/{wid}/novel/quality-reports", "质量报告列表"),
                (f"/worlds/{wid}/novel/quality-reports/{qid}", "质量报告详情"),
                (f"/worlds/{wid}/novel/revisions", "润色候选列表"),
                (f"/worlds/{wid}/novel/revisions/{rid}", "润色候选详情"),
                (f"/worlds/{wid}/novel/drafts/{did}/versions", "版本管理"),
                (f"/worlds/{wid}/novel/final-drafts", "最终稿列表"),
                (f"/worlds/{wid}/novel/final-drafts/{fid}", "最终稿详情"),
                ("/settings/ai", "设置中心"),
                ("/data", "数据管理"),
            ]
            for path, label in pages:
                resp = client.get(path)
                assert resp.status_code == 200, f"{label} ({path}) 应返回200, 实际 {resp.status_code}"
        finally: db.rollback(); db.close()

    def test_no_broken_links(self, client):
        """关键页面不生成 /worlds/None 或 /worlds//."""
        db = SessionLocal()
        try:
            wid, _, _, _, _ = _setup_full_chain(db)
            paths = [
                f"/worlds/{wid}", f"/worlds/{wid}/context",
                f"/worlds/{wid}/novel", f"/worlds/{wid}/novel/drafts",
                f"/worlds/{wid}/novel/quality-reports",
                f"/worlds/{wid}/novel/revisions",
                f"/worlds/{wid}/novel/final-drafts",
            ]
            for p in paths:
                resp = client.get(p)
                assert "/worlds/None" not in resp.text, f"{p} 含 /worlds/None"
                assert "/worlds//" not in resp.text, f"{p} 含 /worlds//"
        finally: db.rollback(); db.close()

    def test_404_for_nonexistent(self, client):
        """不存在的资源返回404."""
        db = SessionLocal()
        try:
            wid, _, _, _, _ = _setup_full_chain(db)
            assert client.get(f"/worlds/{wid}/novel/drafts/99999").status_code == 404
            assert client.get(f"/worlds/{wid}/novel/quality-reports/99999").status_code == 404
            assert client.get(f"/worlds/{wid}/novel/revisions/99999").status_code == 404
            assert client.get(f"/worlds/{wid}/novel/final-drafts/99999").status_code == 404
        finally: db.rollback(); db.close()
