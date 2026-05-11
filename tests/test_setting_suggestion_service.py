"""
AI World Engine - Test Setting Suggestion Service
Tests for prompt building, mock generation, save/list/get, and parsing.
"""

import json
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base
from app.models import World
from app.services.setting_suggestion_service import SettingSuggestionService

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


class TestBuildPrompt:
    def test_prompt_contains_world_name(self, db):
        w = World(name="TestWorld")
        db.add(w); db.commit()
        req = {"suggestion_type": "character", "world_type": "western_fantasy", "reference_style": "heroic_epic", "generation_count": 3, "user_requirement": ""}
        prompt = SettingSuggestionService.build_setting_suggestion_prompt(db, w.id, req)
        assert "TestWorld" in prompt

    def test_prompt_contains_originality_requirement(self, db):
        w = World(name="W")
        db.add(w); db.commit()
        req = {"suggestion_type": "character", "world_type": "western_fantasy", "reference_style": "heroic_epic", "generation_count": 3, "user_requirement": ""}
        prompt = SettingSuggestionService.build_setting_suggestion_prompt(db, w.id, req)
        assert "原创" in prompt

    def test_prompt_contains_candidate_note(self, db):
        w = World(name="W")
        db.add(w); db.commit()
        req = {"suggestion_type": "character", "world_type": "western_fantasy", "reference_style": "heroic_epic", "generation_count": 3, "user_requirement": ""}
        prompt = SettingSuggestionService.build_setting_suggestion_prompt(db, w.id, req)
        assert "候选" in prompt

    def test_prompt_contains_no_ip_copy(self, db):
        w = World(name="W")
        db.add(w); db.commit()
        req = {"suggestion_type": "character", "world_type": "western_fantasy", "reference_style": "heroic_epic", "generation_count": 3, "user_requirement": ""}
        prompt = SettingSuggestionService.build_setting_suggestion_prompt(db, w.id, req)
        assert "不得直接使用" in prompt


class TestMockGenerate:
    def test_mock_character_returns_list(self):
        result = SettingSuggestionService.mock_generate("character", 3)
        assert isinstance(result, list)
        assert len(result) == 3
        assert "name" in result[0]

    def test_mock_faction_returns_list(self):
        result = SettingSuggestionService.mock_generate("faction", 2)
        assert len(result) == 2

    def test_mock_location_returns_list(self):
        result = SettingSuggestionService.mock_generate("location", 5)
        assert len(result) == 5

    def test_mock_rule_returns_list(self):
        result = SettingSuggestionService.mock_generate("rule", 1)
        assert len(result) == 1


class TestSaveAndList:
    def test_save_and_retrieve(self, db):
        w = World(name="W")
        db.add(w); db.commit()
        req = {"suggestion_type": "character", "world_type": "x", "reference_style": "y", "generation_count": 2, "user_requirement": ""}
        mock = json.dumps(SettingSuggestionService.mock_generate("character", 2), ensure_ascii=False)
        record = SettingSuggestionService.save_setting_suggestion(db, w.id, req, "test prompt", mock)
        assert record.id is not None
        suggestions = SettingSuggestionService.list_setting_suggestions(db, w.id)
        assert len(suggestions) == 1

    def test_list_only_returns_current_world(self, db):
        w1 = World(name="W1")
        w2 = World(name="W2")
        db.add_all([w1, w2]); db.commit()
        req = {"suggestion_type": "character", "world_type": "x", "reference_style": "y", "generation_count": 1, "user_requirement": ""}
        mock = json.dumps([{"name": "X"}])
        SettingSuggestionService.save_setting_suggestion(db, w1.id, req, "p", mock)
        suggestions_w2 = SettingSuggestionService.list_setting_suggestions(db, w2.id)
        assert len(suggestions_w2) == 0

    def test_cross_world_access_blocked(self, db):
        w1 = World(name="W1")
        w2 = World(name="W2")
        db.add_all([w1, w2]); db.commit()
        req = {"suggestion_type": "character", "world_type": "x", "reference_style": "y", "generation_count": 1, "user_requirement": ""}
        mock = json.dumps([{"name": "X"}])
        r = SettingSuggestionService.save_setting_suggestion(db, w1.id, req, "p", mock)
        # Try to access from w2
        result = SettingSuggestionService.get_setting_suggestion(db, w2.id, r.id)
        assert result is None


class TestParseResponse:
    def test_parse_valid_json_array(self):
        raw = '[{"name":"A","identity":"B"}]'
        result = SettingSuggestionService.parse_ai_response(raw, "character")
        assert len(result["parsed"]) == 1
        assert result["parsed"][0]["name"] == "A"

    def test_parse_non_json_fallback(self):
        raw = "This is not JSON at all."
        result = SettingSuggestionService.parse_ai_response(raw, "character")
        assert result["parse_warning"] is not None
        assert result["raw"] == raw
