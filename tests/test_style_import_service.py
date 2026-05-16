"""v2.4.0 — Style Import Service Tests"""
import pytest, json, codecs
from io import BytesIO
from app.database import SessionLocal
from app.services.world_service import WorldService
from app.services.style_import_service import StyleImportService
from app.models import StyleProfile


class TestEncoding:
    def test_detect_utf8(self):
        b="测试中文".encode('utf-8')
        assert StyleImportService.detect_text_encoding(b)=='utf-8'

    def test_detect_utf8_sig(self):
        b = codecs.BOM_UTF8 + '测试'.encode('utf-8')
        assert StyleImportService.detect_text_encoding(b)=='utf-8-sig'

    def test_detect_gbk(self):
        b="测试中文".encode('gbk')
        assert StyleImportService.detect_text_encoding(b)=='gbk'


class TestTextProcessing:
    def test_clean_removes_ads(self):
        text="正文内容。\n更多小说请访问www.example.com\n继续正文。"
        c=StyleImportService.clean_style_source_text(text)
        assert "www.example.com" not in c

    def test_split_returns_chunks(self):
        text="第一段内容" * 300
        chunks=StyleImportService.split_text_for_style_analysis(text)
        assert len(chunks)>0
        for c in chunks: assert len(c)>0

    def test_chunk_prompt_forbids_copy(self):
        p=StyleImportService.build_chunk_style_prompt("测试",0,1)
        assert "抽象" in p or "不得复制" in p

    def test_final_prompt_requires_json(self):
        p=StyleImportService.build_final_style_profile_prompt(["S"])
        assert "JSON" in p


class TestStyleImportMock:
    def test_mock_returns_profile(self):
        db=SessionLocal()
        try:
            w=WorldService.create_world(db,name="SW",world_type="F",description="T",current_era="E1",tone="A");db.commit()
            text="第一章 开始\n"+"测试正文内容。"*200
            file=BytesIO(text.encode('utf-8'))
            profile,analysis=StyleImportService.generate_style_profile_from_txt(db,w.id,file,"test.txt",{"profile_name":"MP"})
            assert profile.id is not None
            assert profile.source_type=="txt_analysis"
            assert analysis.analysis_status=="completed"
        finally:db.rollback();db.close()

    def test_mock_profile_has_fields(self):
        db=SessionLocal()
        try:
            w=WorldService.create_world(db,name="SW2",world_type="F",description="T",current_era="E1",tone="A");db.commit()
            text="正文内容。"*300
            file=BytesIO(text.encode('utf-8'))
            profile,_=StyleImportService.generate_style_profile_from_txt(db,w.id,file,"test.txt",{"profile_name":""})
            assert profile.name
            assert profile.generation_prompt_snippet or profile.description
        finally:db.rollback();db.close()

    def test_apply_style_to_prompt(self):
        db=SessionLocal()
        try:
            w=WorldService.create_world(db,name="SW3",world_type="F",description="T",current_era="E1",tone="A");db.commit()
            sp=StyleProfile(world_id=w.id,name="S",generation_prompt_snippet="GS",narrative_pov="3rd")
            db.add(sp);db.commit()
            result=StyleImportService.apply_style_profile_to_prompt(sp)
            assert "GS" in result; assert "3rd" in result
        finally:db.rollback();db.close()

    def test_empty_file_error(self):
        db=SessionLocal()
        try:
            w=WorldService.create_world(db,name="SE",world_type="F",description="T",current_era="E1",tone="A");db.commit()
            with pytest.raises(ValueError,match="空"):
                StyleImportService.generate_style_profile_from_txt(db,w.id,BytesIO(b""),"test.txt",{})
        finally:db.rollback();db.close()

    def test_non_txt_handled_in_route(self):
        # The service doesn't check extension — routes do
        pass
