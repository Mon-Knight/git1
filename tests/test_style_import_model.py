"""v2.4.0 — Style Import Model Tests"""
import pytest, json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import StyleProfile, StyleSourceAnalysis, World


@pytest.fixture
def db():
    e=create_engine("sqlite:///:memory:",connect_args={"check_same_thread":False})
    Base.metadata.create_all(bind=e)
    s=sessionmaker(bind=e)()
    try: yield s
    finally: s.close()


class TestStyleSourceAnalysis:
    def test_create(self, db):
        w=World(name="T");db.add(w);db.commit()
        a=StyleSourceAnalysis(world_id=w.id,source_filename="test.txt",source_file_hash="abc",chunk_count=3)        
        db.add(a);db.commit()
        assert a.id is not None; assert a.analysis_status=="pending"

    def test_source_filename(self, db):
        w=World(name="T");db.add(w);db.commit()
        a=StyleSourceAnalysis(world_id=w.id,source_filename="小说.txt")
        db.add(a);db.commit(); assert a.source_filename=="小说.txt"

    def test_chinese_json(self, db):
        w=World(name="T");db.add(w);db.commit()
        a=StyleSourceAnalysis(world_id=w.id,final_analysis_json=json.dumps({"name":"测试"},ensure_ascii=False))
        db.add(a);db.commit(); assert "测试" in a.final_analysis_json

    def test_cross_world(self, db):
        w1=World(name="W1");w2=World(name="W2");db.add_all([w1,w2]);db.commit()
        a=StyleSourceAnalysis(world_id=w1.id)
        db.add(a);db.commit()
        assert db.query(StyleSourceAnalysis).filter_by(id=a.id,world_id=w1.id).first() is not None
        assert db.query(StyleSourceAnalysis).filter_by(id=a.id,world_id=w2.id).first() is None


class TestStyleProfileTxtAnalysis:
    def test_source_type(self, db):
        w=World(name="T");db.add(w);db.commit()
        sp=StyleProfile(world_id=w.id,name="S",source_type="txt_analysis")
        db.add(sp);db.commit(); assert sp.source_type=="txt_analysis"

    def test_rules_json(self, db):
        w=World(name="T");db.add(w);db.commit()
        sp=StyleProfile(world_id=w.id,name="S",style_rules_json='["R1","R2"]',do_rules="D1\nD2",avoid_rules="A1\nA2")
        db.add(sp);db.commit()
        assert "R1" in sp.style_rules_json; assert "D1" in sp.do_rules

    def test_generation_snippet(self, db):
        w=World(name="T");db.add(w);db.commit()
        sp=StyleProfile(world_id=w.id,name="S",generation_prompt_snippet="GS")
        db.add(sp);db.commit(); assert sp.generation_prompt_snippet=="GS"

    def test_source_analysis_id(self, db):
        w=World(name="T");db.add(w);db.commit()
        sp=StyleProfile(world_id=w.id,name="S",source_type="txt_analysis",source_analysis_id=42)
        db.add(sp);db.commit(); assert sp.source_analysis_id==42
