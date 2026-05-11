"""
AI World Engine - Test Setting Suggestion Adoption Service
Tests for adopt, edit-adopt, discard, cross-world isolation.
"""

import json
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base
from app.models import World, SettingSuggestion, Character, Faction, Location, WorldRule
from app.services.setting_suggestion_adoption_service import SettingSuggestionAdoptionService

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


def _make_suggestion(db, world_id, stype="character", status="pending", result=None):
    if result is None:
        result = json.dumps({"parsed": [{"name": f"Test {stype}", "identity": "Tester"}]})
    s = SettingSuggestion(world_id=world_id, suggestion_type=stype, status=status, result_json=result, generation_count=1)
    db.add(s); db.commit(); db.refresh(s)
    return s


class TestCanAdopt:
    def test_pending_can_adopt(self, db):
        w = World(name="W"); db.add(w); db.commit()
        s = _make_suggestion(db, w.id, "character", "pending")
        ok, _ = SettingSuggestionAdoptionService.can_adopt(s)
        assert ok

    def test_adopted_cannot_adopt(self, db):
        w = World(name="W"); db.add(w); db.commit()
        s = _make_suggestion(db, w.id, "character", "adopted")
        ok, reason = SettingSuggestionAdoptionService.can_adopt(s)
        assert not ok

    def test_discarded_cannot_adopt(self, db):
        w = World(name="W"); db.add(w); db.commit()
        s = _make_suggestion(db, w.id, "character", "discarded")
        ok, _ = SettingSuggestionAdoptionService.can_adopt(s)
        assert not ok

    def test_edited_adopted_cannot_adopt(self, db):
        w = World(name="W"); db.add(w); db.commit()
        s = _make_suggestion(db, w.id, "character", "edited_adopted")
        ok, _ = SettingSuggestionAdoptionService.can_adopt(s)
        assert not ok


class TestAdopt:
    def test_adopt_character_creates_record(self, db):
        w = World(name="W"); db.add(w); db.commit()
        s = _make_suggestion(db, w.id, "character")
        result = SettingSuggestionAdoptionService.adopt(db, w.id, s.id, 0)
        assert result["ok"]
        assert result["target_type"] == "character"
        db.refresh(s)
        assert s.status == "adopted"
        assert s.adopted_target_id is not None
        assert db.query(Character).filter(Character.world_id == w.id).count() == 1

    def test_adopt_faction_creates_record(self, db):
        w = World(name="W"); db.add(w); db.commit()
        s = _make_suggestion(db, w.id, "faction", result=json.dumps({"parsed": [{"name": "TestF", "faction_type": "Guild"}]}))
        result = SettingSuggestionAdoptionService.adopt(db, w.id, s.id, 0)
        assert result["ok"]
        assert db.query(Faction).filter(Faction.world_id == w.id).count() == 1

    def test_adopt_location_creates_record(self, db):
        w = World(name="W"); db.add(w); db.commit()
        s = _make_suggestion(db, w.id, "location", result=json.dumps({"parsed": [{"name": "TestL", "location_type": "Forest"}]}))
        result = SettingSuggestionAdoptionService.adopt(db, w.id, s.id, 0)
        assert result["ok"]
        assert db.query(Location).filter(Location.world_id == w.id).count() == 1

    def test_adopt_rule_creates_record(self, db):
        w = World(name="W"); db.add(w); db.commit()
        s = _make_suggestion(db, w.id, "rule", result=json.dumps({"parsed": [{"name": "TestR", "rule_type": "Magic"}]}))
        result = SettingSuggestionAdoptionService.adopt(db, w.id, s.id, 0)
        assert result["ok"]
        assert db.query(WorldRule).filter(WorldRule.world_id == w.id).count() == 1

    def test_cross_world_adopt_blocked(self, db):
        w1 = World(name="W1"); w2 = World(name="W2")
        db.add_all([w1, w2]); db.commit()
        s = _make_suggestion(db, w1.id, "character")
        result = SettingSuggestionAdoptionService.adopt(db, w2.id, s.id, 0)
        assert not result["ok"]

    def test_bad_item_index(self, db):
        w = World(name="W"); db.add(w); db.commit()
        s = _make_suggestion(db, w.id, "character")
        result = SettingSuggestionAdoptionService.adopt(db, w.id, s.id, 99)
        assert not result["ok"]


class TestDiscard:
    def test_discard_pending(self, db):
        w = World(name="W"); db.add(w); db.commit()
        s = _make_suggestion(db, w.id, "character")
        result = SettingSuggestionAdoptionService.discard(db, w.id, s.id)
        assert result["ok"]
        db.refresh(s)
        assert s.status == "discarded"

    def test_discard_already_adopted(self, db):
        w = World(name="W"); db.add(w); db.commit()
        s = _make_suggestion(db, w.id, "character", "adopted")
        result = SettingSuggestionAdoptionService.discard(db, w.id, s.id)
        assert not result["ok"]


class TestEditAdopt:
    def test_edit_adopt_success(self, db):
        w = World(name="W"); db.add(w); db.commit()
        s = _make_suggestion(db, w.id, "character")
        result = SettingSuggestionAdoptionService.adopt_with_edit(db, w.id, s.id, 0, {"name": "EditedHero", "identity": "Custom"})
        assert result["ok"]
        db.refresh(s)
        assert s.status == "edited_adopted"
        assert db.query(Character).filter(Character.name == "EditedHero").count() == 1
