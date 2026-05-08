"""
Tests for database initialization and models.
"""

from sqlalchemy import inspect

from app.database import Base
from app.models import (
    World, Character, Faction, Location,
    WorldRule, HistoricalEvent, SimulationRecord, Branch,
)
from tests.conftest import test_engine


def test_database_init():
    """Test that init_db() creates all tables without error."""
    inspector = inspect(test_engine)
    table_names = inspector.get_table_names()

    expected_tables = [
        "worlds", "characters", "factions", "locations",
        "world_rules", "historical_events", "simulation_records", "branches",
    ]

    for table in expected_tables:
        assert table in table_names, f"Table '{table}' not found in database"


def test_world_model_columns():
    """Test that World model has expected columns."""
    inspector = inspect(test_engine)
    columns = {col["name"] for col in inspector.get_columns("worlds")}

    expected = {"id", "name", "world_type", "description", "current_era",
                "tone", "created_at", "updated_at"}
    assert expected.issubset(columns)


def test_character_model_columns():
    """Test that Character model has expected columns."""
    inspector = inspect(test_engine)
    columns = {col["name"] for col in inspector.get_columns("characters")}

    expected = {"id", "world_id", "name", "role", "faction_id", "personality",
                "goal", "abilities", "current_status", "notes", "created_at", "updated_at"}
    assert expected.issubset(columns)


def test_simulation_record_model_columns():
    """Test that SimulationRecord model has expected columns."""
    inspector = inspect(test_engine)
    columns = {col["name"] for col in inspector.get_columns("simulation_records")}

    expected = {"id", "world_id", "question", "ai_response", "status",
                "ai_model", "is_mock", "created_at"}
    assert expected.issubset(columns)


def test_historical_event_model_columns():
    """Test that HistoricalEvent has is_canon field."""
    inspector = inspect(test_engine)
    columns = {col["name"] for col in inspector.get_columns("historical_events")}

    assert "is_canon" in columns
    assert "source_type" in columns
    assert "source_id" in columns
