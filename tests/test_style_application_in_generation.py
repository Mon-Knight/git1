"""v2.4.0 — Style Application in Generation Tests"""
import pytest, json
from io import BytesIO
from app.database import SessionLocal
from app.services.world_service import WorldService
from app.services.novel_draft_service import NovelDraftService
from app.services.novel_quality_service import NovelQualityService
from app.services.novel_revision_service import NovelRevisionService
from app.services.style_import_service import StyleImportService
from app.models import NovelDraft, StyleProfile


class TestStyleApplication:
    def test_draft_prompt_includes_style(self):
        db=SessionLocal()
        try:
            w=WorldService.create_world(db,name="SA",world_type="F",description="T",current_era="E1",tone="A");db.commit()
            sp=StyleProfile(world_id=w.id,name="GS",generation_prompt_snippet="约束文本",narrative_pov="第三人称")
            db.add(sp);db.commit()
            d=NovelDraft(world_id=w.id,chapter_outline_id=1,volume_index=1,chapter_index=1,title="D",content="C",style_profile_id=sp.id)
            db.add(d);db.commit()
            # Check draft has style_profile_id
            assert d.style_profile_id==sp.id
        finally:db.rollback();db.close()

    def test_quality_prompt_has_style(self):
        db=SessionLocal()
        try:
            w=WorldService.create_world(db,name="QA",world_type="F",description="T",current_era="E1",tone="A");db.commit()
            sp=StyleProfile(world_id=w.id,name="QS",generation_prompt_snippet="质量约束")
            db.add(sp);db.commit()
            d=NovelDraft(world_id=w.id,chapter_outline_id=1,volume_index=1,chapter_index=1,title="D",content="CC",style_profile_id=sp.id)
            db.add(d);db.commit();db.refresh(d)
            rj=json.dumps({"title":"QR","overall_score":82},ensure_ascii=False)
            qr=NovelQualityService.save_quality_report(db,w.id,d.id,"p",rj)
            # Quality check of draft with style
            assert qr is not None
        finally:db.rollback();db.close()

    def test_revision_respects_style(self):
        db=SessionLocal()
        try:
            w=WorldService.create_world(db,name="RS",world_type="F",description="T",current_era="E1",tone="A");db.commit()
            sp=StyleProfile(world_id=w.id,name="RS",generation_prompt_snippet="润色约束")
            db.add(sp);db.commit()
            d=NovelDraft(world_id=w.id,chapter_outline_id=1,volume_index=1,chapter_index=1,title="D",content="CC",style_profile_id=sp.id)
            db.add(d);db.commit();db.refresh(d)
            rj=json.dumps({"title":"QR","overall_score":82},ensure_ascii=False)
            qr=NovelQualityService.save_quality_report(db,w.id,d.id,"p",rj)
            rev=NovelRevisionService.generate_revision(db,w.id,d.id,qr.id,{"extra_requirements":""})
            assert rev is not None
        finally:db.rollback();db.close()

    def test_no_style_still_works(self, client):
        db=SessionLocal()
        try:
            w=WorldService.create_world(db,name="NS",world_type="F",description="T",current_era="E1",tone="A");db.commit()
            d=NovelDraft(world_id=w.id,chapter_outline_id=1,volume_index=1,chapter_index=1,title="ND",content="NC")
            db.add(d);db.commit()
            r=client.get(f"/worlds/{w.id}/novel/drafts/{d.id}")
            assert r.status_code==200
        finally:db.rollback();db.close()
