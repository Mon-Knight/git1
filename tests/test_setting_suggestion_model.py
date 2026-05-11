"""
AI World Engine - Test Setting Suggestion Model
Tests for SettingSuggestion model creation and basic properties.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base
from app.models import World, SettingSuggestion
import json

_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
_Session = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


@pytest.fixture()
def db():
    Base.metadata.create_all(bind=_engine)
    session = _Session()
    yield session
    session.rollback()
    session.close()
    Base.metadata.drop_all(bind=_engine)


class TestSettingSuggestionModel:
    def test_create_suggestion(self, db):
        w = World(name="Test")
        db.add(w); db.commit()
        s = SettingSuggestion(world_id=w.id, suggestion_type="character", status="pending")
        db.add(s); db.commit()
        assert s.id is not None
        assert s.status == "pending"

    def test_default_status_pending(self, db):
        w = World(name="Test")
        db.add(w); db.commit()
        s = SettingSuggestion(world_id=w.id, suggestion_type="faction")
        db.add(s); db.commit()
        assert s.status == "pending"

    def test_type_character(self, db):
        w = World(name="Test")
        db.add(w); db.commit()
        s = SettingSuggestion(world_id=w.id, suggestion_type="character")
        db.add(s); db.commit()
        assert s.suggestion_type == "character"

    def test_type_faction(self, db):
        w = World(name="Test")
        db.add(w); db.commit()
        s = SettingSuggestion(world_id=w.id, suggestion_type="faction")
        db.add(s); db.commit()
        assert s.suggestion_type == "faction"

    def test_type_location(self, db):
        w = World(name="Test")
        db.add(w); db.commit()
        s = SettingSuggestion(world_id=w.id, suggestion_type="location")
        db.add(s); db.commit()
        assert s.suggestion_type == "location"

    def test_type_rule(self, db):
        w = World(name="Test")
        db.add(w); db.commit()
        s = SettingSuggestion(world_id=w.id, suggestion_type="rule")
        db.add(s); db.commit()
        assert s.suggestion_type == "rule"

    def test_result_json_utf8(self, db):
        w = World(name="Test")
        db.add(w); db.commit()
        data = json.dumps([{"name": "测试角色", "identity": "流浪剑客"}], ensure_ascii=False)
        s = SettingSuggestion(world_id=w.id, suggestion_type="character", result_json=data)
        db.add(s); db.commit()
        assert "测试角色" in s.result_json

    def test_world_relation(self, db):
        w = World(name="Test")
        db.add(w); db.commit()
        s = SettingSuggestion(world_id=w.id, suggestion_type="character")
        db.add(s); db.commit()
        assert s.world_id == w.id

    def test_cross_world_isolation(self, db):
        w1 = World(name="W1")
        w2 = World(name="W2")
        db.add_all([w1, w2]); db.commit()
        s = SettingSuggestion(world_id=w1.id, suggestion_type="character")
        db.add(s); db.commit()
        # Query should only return from w1
        results = db.query(SettingSuggestion).filter(SettingSuggestion.world_id == w2.id).all()
        assert len(results) == 0
