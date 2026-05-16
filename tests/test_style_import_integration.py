"""v2.4.0 — Style Import Integration Tests"""
import pytest, json
from io import BytesIO
from app.database import SessionLocal
from app.services.world_service import WorldService
from app.models import StyleProfile, NovelDraft


def _setup(db):
    w=WorldService.create_world(db,name="SI",world_type="F",description="T",current_era="E1",tone="A");db.commit()
    text="第一章\n"+"测试正文。"*300
    from app.services.style_import_service import StyleImportService
    sp,_=StyleImportService.generate_style_profile_from_txt(db,w.id,BytesIO(text.encode('utf-8')),"test.txt",{"profile_name":"IP"})
    d=NovelDraft(world_id=w.id,chapter_outline_id=1,volume_index=1,chapter_index=1,title="ID",content="C",status="candidate",style_profile_id=sp.id)
    db.add(d);db.commit();db.refresh(d)
    return w.id,d.id,sp.id


class TestStyleIntegration:
    def test_context_has_style_entry(self, client):
        db=SessionLocal()
        try:
            wid,_,_=_setup(db)
            r=client.get(f"/worlds/{wid}/context")
            assert "风格" in r.text or "styles" in r.text
        finally:db.rollback();db.close()

    def test_import_page_current_world(self, client):
        db=SessionLocal()
        try:
            wid,_,_=_setup(db)
            r=client.get(f"/worlds/{wid}/context/styles/import")
            assert "请先选择世界" not in r.text
        finally:db.rollback();db.close()

    def test_existing_features_ok(self, client):
        db=SessionLocal()
        try:
            wid,_,_=_setup(db)
            assert client.get("/").status_code==200
            assert client.get(f"/worlds/{wid}").status_code==200
            assert client.get(f"/worlds/{wid}/context").status_code==200
            assert client.get(f"/worlds/{wid}/simulation").status_code==200
            assert client.get(f"/worlds/{wid}/checks").status_code==200
            assert client.get(f"/worlds/{wid}/novel/quality-reports").status_code==200
            assert client.get(f"/worlds/{wid}/novel/revisions").status_code==200
            assert client.get(f"/worlds/{wid}/novel/final-drafts").status_code==200
            assert client.get("/settings/ai").status_code==200
        finally:db.rollback();db.close()

    def test_v2013_sidebar(self, client):
        db=SessionLocal()
        try:
            wid,_,_=_setup(db)
            r=client.get(f"/worlds/{wid}/context")
            assert "请先选择世界以管理创作资产" not in r.text
            assert f"/worlds/{wid}/simulation" in r.text
        finally:db.rollback();db.close()
