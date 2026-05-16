"""v2.4.0 — Style Import UI Adaptation Tests"""
import pytest
from io import BytesIO
from app.database import SessionLocal
from app.services.world_service import WorldService
from app.models import StyleProfile


class TestStyleImportUI:
    def test_import_form_layout(self, client):
        db=SessionLocal()
        try:
            w=WorldService.create_world(db,name="SU",world_type="F",description="T",current_era="E1",tone="A");db.commit()
            r=client.get(f"/worlds/{w.id}/context/styles/import")
            assert "app-shell-body" in r.text; assert "file" in r.text.lower()
        finally:db.rollback();db.close()

    def test_import_has_warnings(self, client):
        db=SessionLocal()
        try:
            w=WorldService.create_world(db,name="SU2",world_type="F",description="T",current_era="E1",tone="A");db.commit()
            r=client.get(f"/worlds/{w.id}/context/styles/import")
            assert "不会" in r.text or "不复制" in r.text or "抽象" in r.text
        finally:db.rollback();db.close()

    def test_detail_uses_dashboard(self, client):
        db=SessionLocal()
        try:
            w=WorldService.create_world(db,name="SU3",world_type="F",description="T",current_era="E1",tone="A");db.commit()
            sp=StyleProfile(world_id=w.id,name="UD",source_type="txt_analysis")
            db.add(sp);db.commit()
            r=client.get(f"/worlds/{w.id}/context/styles/{sp.id}")
            assert "app-main-inner" in r.text
        finally:db.rollback();db.close()

    def test_detail_shows_source(self, client):
        db=SessionLocal()
        try:
            w=WorldService.create_world(db,name="SU4",world_type="F",description="T",current_era="E1",tone="A");db.commit()
            sp=StyleProfile(world_id=w.id,name="UD2",source_type="txt_analysis")
            db.add(sp);db.commit()
            r=client.get(f"/worlds/{w.id}/context/styles/{sp.id}")
            assert "TXT" in r.text or "分析" in r.text or "导入" in r.text
        finally:db.rollback();db.close()
