"""v2.4.0 — Style Import Routes Tests"""
import pytest
from io import BytesIO
from app.database import SessionLocal
from app.services.world_service import WorldService
from app.models import StyleProfile
from fastapi.testclient import TestClient


class TestStyleImportRoutes:
    def test_import_page_200(self, client):
        db=SessionLocal()
        try:
            w=WorldService.create_world(db,name="SR",world_type="F",description="T",current_era="E1",tone="A");db.commit()
            r=client.get(f"/worlds/{w.id}/context/styles/import")
            assert r.status_code==200; assert "TXT" in r.text or "导入" in r.text
        finally:db.rollback();db.close()

    def test_upload_creates_profile(self, client):
        db=SessionLocal()
        try:
            w=WorldService.create_world(db,name="SR2",world_type="F",description="T",current_era="E1",tone="A");db.commit()
            text="第一章\n"+"测试正文。"*300
            files={"file":("test.txt",BytesIO(text.encode('utf-8')),"text/plain")}
            r=client.post(f"/worlds/{w.id}/context/styles/import",files=files,data={"profile_name":"TP"},follow_redirects=False)
            assert r.status_code==303
        finally:db.rollback();db.close()

    def test_detail_page_200(self, client):
        db=SessionLocal()
        try:
            w=WorldService.create_world(db,name="SR3",world_type="F",description="T",current_era="E1",tone="A");db.commit()
            sp=StyleProfile(world_id=w.id,name="SD",source_type="txt_analysis")
            db.add(sp);db.commit()
            r=client.get(f"/worlds/{w.id}/context/styles/{sp.id}")
            assert r.status_code==200; assert "SD" in r.text
        finally:db.rollback();db.close()

    def test_set_active(self, client):
        db=SessionLocal()
        try:
            w=WorldService.create_world(db,name="SR4",world_type="F",description="T",current_era="E1",tone="A");db.commit()
            sp=StyleProfile(world_id=w.id,name="SA")
            db.add(sp);db.commit()
            r=client.post(f"/worlds/{w.id}/context/styles/{sp.id}/set-active",follow_redirects=False)
            assert r.status_code==303
        finally:db.rollback();db.close()

    def test_404_world(self, client):
        r=client.get("/worlds/99999/context/styles/import")
        assert r.status_code==404

    def test_extends_base(self, client):
        db=SessionLocal()
        try:
            w=WorldService.create_world(db,name="SR5",world_type="F",description="T",current_era="E1",tone="A");db.commit()
            r=client.get(f"/worlds/{w.id}/context/styles/import")
            assert "app-shell-body" in r.text
        finally:db.rollback();db.close()

    def test_no_none_links(self, client):
        db=SessionLocal()
        try:
            w=WorldService.create_world(db,name="SR6",world_type="F",description="T",current_era="E1",tone="A");db.commit()
            for p in [f"/worlds/{w.id}/context/styles/import",f"/worlds/{w.id}/context/styles"]:
                r=client.get(p)
                assert "/worlds/None" not in r.text; assert "/worlds//" not in r.text
        finally:db.rollback();db.close()
