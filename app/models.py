"""
AI World Engine - SQLAlchemy Data Models
Defines all database tables for the world-building system.
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship

from app.database import Base


def _utcnow():
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


class World(Base):
    """A fictional world project."""
    __tablename__ = "worlds"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    world_type = Column(String(100), default="")
    description = Column(Text, default="")
    current_era = Column(String(100), default="")
    tone = Column(String(100), default="")
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    # Relationships
    characters = relationship("Character", back_populates="world", cascade="all, delete-orphan")
    factions = relationship("Faction", back_populates="world", cascade="all, delete-orphan")
    locations = relationship("Location", back_populates="world", cascade="all, delete-orphan")
    rules = relationship("WorldRule", back_populates="world", cascade="all, delete-orphan")
    events = relationship("HistoricalEvent", back_populates="world", cascade="all, delete-orphan")
    simulations = relationship("SimulationRecord", back_populates="world", cascade="all, delete-orphan")
    branches = relationship("Branch", back_populates="world", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<World id={self.id} name='{self.name}'>"


class Character(Base):
    """A character in a world."""
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    world_id = Column(Integer, ForeignKey("worlds.id"), nullable=False)
    name = Column(String(200), nullable=False)
    role = Column(String(200), default="")
    faction_id = Column(Integer, ForeignKey("factions.id", use_alter=True), nullable=True)
    personality = Column(Text, default="")
    goal = Column(Text, default="")
    abilities = Column(Text, default="")
    current_status = Column(String(100), default="存活")
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    world = relationship("World", back_populates="characters")
    faction = relationship("Faction", back_populates="members", foreign_keys=[faction_id])

    def __repr__(self):
        return f"<Character id={self.id} name='{self.name}'>"


class Faction(Base):
    """A faction (organization, nation, etc.) in a world."""
    __tablename__ = "factions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    world_id = Column(Integer, ForeignKey("worlds.id"), nullable=False)
    name = Column(String(200), nullable=False)
    faction_type = Column(String(100), default="")
    leader_id = Column(Integer, ForeignKey("characters.id", use_alter=True), nullable=True)
    goal = Column(Text, default="")
    resources = Column(Text, default="")
    enemies = Column(Text, default="[]")  # JSON array of faction IDs
    allies = Column(Text, default="[]")   # JSON array of faction IDs
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    world = relationship("World", back_populates="factions")
    leader = relationship("Character", foreign_keys=[leader_id])
    members = relationship("Character", back_populates="faction", foreign_keys=[Character.faction_id])

    def __repr__(self):
        return f"<Faction id={self.id} name='{self.name}'>"


class Location(Base):
    """A location in a world."""
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    world_id = Column(Integer, ForeignKey("worlds.id"), nullable=False)
    name = Column(String(200), nullable=False)
    location_type = Column(String(100), default="")
    region = Column(String(200), default="")
    description = Column(Text, default="")
    controlling_faction_id = Column(Integer, ForeignKey("factions.id"), nullable=True)
    important_events = Column(Text, default="")
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    world = relationship("World", back_populates="locations")
    controlling_faction = relationship("Faction", foreign_keys=[controlling_faction_id])

    def __repr__(self):
        return f"<Location id={self.id} name='{self.name}'>"


class WorldRule(Base):
    """A rule that governs a world (physics, magic, society, etc.)."""
    __tablename__ = "world_rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    world_id = Column(Integer, ForeignKey("worlds.id"), nullable=False)
    name = Column(String(200), nullable=False)
    rule_type = Column(String(100), default="")
    content = Column(Text, default="")
    constraints = Column(Text, default="")
    scope = Column(Text, default="")
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    world = relationship("World", back_populates="rules")

    def __repr__(self):
        return f"<WorldRule id={self.id} name='{self.name}'>"


class HistoricalEvent(Base):
    """A canon (or non-canon) historical event in a world's timeline."""
    __tablename__ = "historical_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    world_id = Column(Integer, ForeignKey("worlds.id"), nullable=False)
    title = Column(String(300), nullable=False)
    event_time = Column(String(200), default="")
    involved_characters = Column(Text, default="[]")  # JSON array
    involved_factions = Column(Text, default="[]")    # JSON array
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    content = Column(Text, default="")
    consequences = Column(Text, default="")
    is_canon = Column(Boolean, default=True)
    source_type = Column(String(50), default="manual")  # manual / simulation
    source_id = Column(Integer, nullable=True)  # FK to simulation_records if from AI
    created_at = Column(DateTime, default=_utcnow)

    world = relationship("World", back_populates="events")
    location = relationship("Location", foreign_keys=[location_id])

    def __repr__(self):
        return f"<HistoricalEvent id={self.id} title='{self.title}' canon={self.is_canon}>"


class SimulationRecord(Base):
    """An AI-generated simulation result, pending user review."""
    __tablename__ = "simulation_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    world_id = Column(Integer, ForeignKey("worlds.id"), nullable=False)
    question = Column(Text, default="")
    simulation_type = Column(String(50), default="")
    context_snapshot = Column(Text, default="")
    ai_response = Column(Text, default="")
    status = Column(String(50), default="pending")  # pending / adopted / branched / discarded
    ai_model = Column(String(100), default="")
    is_mock = Column(Boolean, default=False)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    world = relationship("World", back_populates="simulations")

    def __repr__(self):
        return f"<SimulationRecord id={self.id} status='{self.status}'>"


class Branch(Base):
    """A branch timeline created from an un-adopted simulation."""
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    world_id = Column(Integer, ForeignKey("worlds.id"), nullable=False)
    simulation_id = Column(Integer, ForeignKey("simulation_records.id"), nullable=False)
    branch_name = Column(String(200), default="")
    description = Column(Text, default="")
    events_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=_utcnow)

    world = relationship("World", back_populates="branches")
    simulation = relationship("SimulationRecord", foreign_keys=[simulation_id])

    def __repr__(self):
        return f"<Branch id={self.id} name='{self.branch_name}'>"
