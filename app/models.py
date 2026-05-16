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
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    world = relationship("World", back_populates="branches")
    simulation = relationship("SimulationRecord", foreign_keys=[simulation_id])

    def __repr__(self):
        return f"<Branch id={self.id} name='{self.branch_name}'>"


class AppSetting(Base):
    """Application configuration stored in database. Keys are unique."""
    __tablename__ = "app_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=True, default="")
    description = Column(String(300), nullable=True, default="")
    is_secret = Column(Boolean, default=False)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    def __repr__(self):
        return f"<AppSetting key='{self.key}'>"


class StyleProfile(Base):
    """A saved writing style profile. Can be global (world_id=None) or world-scoped."""
    __tablename__ = "style_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    world_id = Column(Integer, ForeignKey("worlds.id"), nullable=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, default="")
    genre = Column(String(200), default="")
    narrative_pov = Column(String(100), default="")
    pacing = Column(String(100), default="")
    sentence_style = Column(Text, default="")
    paragraph_style = Column(Text, default="")
    description_ratio = Column(String(50), default="")
    dialogue_style = Column(Text, default="")
    action_style = Column(Text, default="")
    psychology_style = Column(Text, default="")
    info_release_style = Column(Text, default="")
    conflict_style = Column(Text, default="")
    character_style = Column(Text, default="")
    battle_style = Column(Text, default="")
    emotion_style = Column(Text, default="")
    opening_style = Column(Text, default="")
    ending_hook_style = Column(Text, default="")
    forbidden_patterns = Column(Text, default="")
    extra_instructions = Column(Text, default="")
    # v2.4.0: TXT analysis source fields
    source_type = Column(String(30), default="manual")  # manual / txt_analysis / imported / system
    source_analysis_id = Column(Integer, nullable=True)
    style_rules_json = Column(Text, default="")
    do_rules = Column(Text, default="")
    avoid_rules = Column(Text, default="")
    generation_prompt_snippet = Column(Text, default="")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    world = relationship("World", foreign_keys=[world_id])

    def __repr__(self):
        return f"<StyleProfile id={self.id} name='{self.name}'>"


class StyleSourceAnalysis(Base):
    """Records the analysis process of a TXT source file for style extraction."""
    __tablename__ = "style_source_analyses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    world_id = Column(Integer, ForeignKey("worlds.id"), nullable=False)
    style_profile_id = Column(Integer, ForeignKey("style_profiles.id"), nullable=True)
    source_filename = Column(String(500), default="")
    source_file_hash = Column(String(64), default="")
    source_file_size = Column(Integer, default=0)
    source_char_count = Column(Integer, default=0)
    encoding = Column(String(20), default="")
    chunk_count = Column(Integer, default=0)
    sample_strategy = Column(String(100), default="")
    analysis_status = Column(String(20), default="pending")  # pending / analyzing / completed / failed / discarded
    chunk_summaries_json = Column(Text, default="")
    final_analysis_json = Column(Text, default="")
    raw_ai_summary = Column(Text, default="")
    error_message = Column(Text, default="")
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    world = relationship("World", foreign_keys=[world_id])

    def __repr__(self):
        return f"<StyleSourceAnalysis id={self.id} file='{self.source_filename}'>"


class PlotAnchor(Base):
    """A plot anchor recording current story progress within a world."""
    __tablename__ = "plot_anchors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    world_id = Column(Integer, ForeignKey("worlds.id"), nullable=False)
    name = Column(String(200), nullable=False)
    stage = Column(String(100), default="")
    volume_name = Column(String(200), default="")
    chapter_range = Column(String(100), default="")
    protagonist_age = Column(String(50), default="")
    current_time = Column(String(200), default="")
    current_location = Column(String(200), default="")
    occurred_events = Column(Text, default="")
    hidden_secrets = Column(Text, default="")
    current_conflict = Column(Text, default="")
    character_states = Column(Text, default="")
    faction_states = Column(Text, default="")
    current_goal = Column(Text, default="")
    next_goal = Column(Text, default="")
    forbidden_events = Column(Text, default="")
    notes = Column(Text, default="")
    is_locked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    world = relationship("World", foreign_keys=[world_id])

    def __repr__(self):
        return f"<PlotAnchor id={self.id} name='{self.name}'>"


class ContextPackage(Base):
    """A creative context package combining simulation records, style profiles, and plot anchors."""
    __tablename__ = "context_packages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    world_id = Column(Integer, ForeignKey("worlds.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, default="")
    simulation_record_id = Column(Integer, ForeignKey("simulation_records.id"), nullable=True)
    style_profile_id = Column(Integer, ForeignKey("style_profiles.id"), nullable=True)
    plot_anchor_id = Column(Integer, ForeignKey("plot_anchors.id"), nullable=True)
    generation_type = Column(String(50), default="")
    strict_canon = Column(Boolean, default=True)
    strict_style = Column(Boolean, default=True)
    include_branches = Column(Boolean, default=False)
    include_non_canon = Column(Boolean, default=False)
    target_words = Column(String(50), default="")
    extra_requirements = Column(Text, default="")
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    world = relationship("World", foreign_keys=[world_id])
    simulation_record = relationship("SimulationRecord", foreign_keys=[simulation_record_id])
    style_profile = relationship("StyleProfile", foreign_keys=[style_profile_id])
    plot_anchor = relationship("PlotAnchor", foreign_keys=[plot_anchor_id])

    def __repr__(self):
        return f"<ContextPackage id={self.id} name='{self.name}'>"


class SettingSuggestion(Base):
    """AI-generated candidate setting suggestions for characters, factions, locations, rules."""
    __tablename__ = "setting_suggestions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    world_id = Column(Integer, ForeignKey("worlds.id"), nullable=False)
    suggestion_type = Column(String(20), nullable=False)  # character/faction/location/rule
    world_type = Column(String(50), default="")
    reference_style = Column(String(50), default="")
    generation_count = Column(Integer, default=3)
    user_requirement = Column(Text, default="")
    prompt = Column(Text, default="")
    result_json = Column(Text, default="")
    status = Column(String(20), default="pending")  # pending/adopted/edited_adopted/discarded
    adopted_target_id = Column(Integer, nullable=True)
    adopted_target_type = Column(String(20), nullable=True)  # character/faction/location/rule
    adopted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    world = relationship("World", foreign_keys=[world_id])

    def __repr__(self):
        return f"<SettingSuggestion id={self.id} type='{self.suggestion_type}'>"


class NovelVolumeOutline(Base):
    """AI-generated volume outline for novel engineering."""
    __tablename__ = "novel_volume_outlines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    world_id = Column(Integer, ForeignKey("worlds.id"), nullable=False)
    title = Column(String(300), nullable=False, default="")
    source_evolution_id = Column(Integer, ForeignKey("simulation_records.id"), nullable=True)
    style_profile_id = Column(Integer, ForeignKey("style_profiles.id"), nullable=True)
    plot_anchor_id = Column(Integer, ForeignKey("plot_anchors.id"), nullable=True)
    context_package_id = Column(Integer, ForeignKey("context_packages.id"), nullable=True)
    generation_requirement = Column(Text, default="")
    volume_count = Column(Integer, default=0)
    prompt = Column(Text, default="")
    result_json = Column(Text, default="")
    raw_text = Column(Text, default="")
    status = Column(String(20), default="candidate")  # candidate / main / discarded
    is_main = Column(Boolean, default=False)
    confirmed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    world = relationship("World", foreign_keys=[world_id])
    source_evolution = relationship("SimulationRecord", foreign_keys=[source_evolution_id])
    style_profile = relationship("StyleProfile", foreign_keys=[style_profile_id])
    plot_anchor = relationship("PlotAnchor", foreign_keys=[plot_anchor_id])
    context_package = relationship("ContextPackage", foreign_keys=[context_package_id])

    def __repr__(self):
        return f"<NovelVolumeOutline id={self.id} status='{self.status}'>"


class NovelChapterOutline(Base):
    """AI-generated chapter outline for novel engineering, bound to a volume outline."""
    __tablename__ = "novel_chapter_outlines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    world_id = Column(Integer, ForeignKey("worlds.id"), nullable=False)
    volume_outline_id = Column(Integer, ForeignKey("novel_volume_outlines.id"), nullable=False)
    volume_index = Column(Integer, nullable=False, default=0)
    volume_title = Column(String(300), default="")
    title = Column(String(300), nullable=False, default="")
    style_profile_id = Column(Integer, ForeignKey("style_profiles.id"), nullable=True)
    plot_anchor_id = Column(Integer, ForeignKey("plot_anchors.id"), nullable=True)
    context_package_id = Column(Integer, ForeignKey("context_packages.id"), nullable=True)
    generation_requirement = Column(Text, default="")
    prompt = Column(Text, default="")
    result_json = Column(Text, default="")
    raw_text = Column(Text, default="")
    chapter_count = Column(Integer, default=0)
    status = Column(String(20), default="candidate")  # candidate / main / discarded
    is_main = Column(Boolean, default=False)
    confirmed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    world = relationship("World", foreign_keys=[world_id])
    volume_outline = relationship("NovelVolumeOutline", foreign_keys=[volume_outline_id])
    style_profile = relationship("StyleProfile", foreign_keys=[style_profile_id])
    plot_anchor = relationship("PlotAnchor", foreign_keys=[plot_anchor_id])
    context_package = relationship("ContextPackage", foreign_keys=[context_package_id])

    def __repr__(self):
        return f"<NovelChapterOutline id={self.id} status='{self.status}'>"


class NovelDraft(Base):
    """AI-generated novel draft for a single chapter."""
    __tablename__ = "novel_drafts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    world_id = Column(Integer, ForeignKey("worlds.id"), nullable=False)
    chapter_outline_id = Column(Integer, ForeignKey("novel_chapter_outlines.id"), nullable=False)
    volume_index = Column(Integer, default=0)
    volume_title = Column(String(300), default="")
    chapter_index = Column(Integer, default=0)
    chapter_title = Column(String(300), default="")
    title = Column(String(300), default="")
    style_profile_id = Column(Integer, ForeignKey("style_profiles.id"), nullable=True)
    context_package_id = Column(Integer, ForeignKey("context_packages.id"), nullable=True)
    plot_anchor_id = Column(Integer, ForeignKey("plot_anchors.id"), nullable=True)
    generation_requirement = Column(Text, default="")
    prompt = Column(Text, default="")
    content = Column(Text, default="")
    raw_text = Column(Text, default="")
    notes = Column(Text, default="")
    word_count = Column(Integer, default=0)
    status = Column(String(20), default="candidate")  # candidate / accepted / discarded
    is_accepted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)
    accepted_at = Column(DateTime, nullable=True)

    world = relationship("World", foreign_keys=[world_id])
    chapter_outline = relationship("NovelChapterOutline", foreign_keys=[chapter_outline_id])
    style_profile = relationship("StyleProfile", foreign_keys=[style_profile_id])
    context_package = relationship("ContextPackage", foreign_keys=[context_package_id])
    plot_anchor = relationship("PlotAnchor", foreign_keys=[plot_anchor_id])

    def __repr__(self):
        return f"<NovelDraft id={self.id} status='{self.status}'>"


class NovelDraftQualityReport(Base):
    """AI-generated quality check report for a novel draft."""
    __tablename__ = "novel_draft_quality_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    world_id = Column(Integer, ForeignKey("worlds.id"), nullable=False)
    draft_id = Column(Integer, ForeignKey("novel_drafts.id"), nullable=False)
    chapter_outline_id = Column(Integer, ForeignKey("novel_chapter_outlines.id"), nullable=True)
    volume_index = Column(Integer, default=0)
    chapter_index = Column(Integer, default=0)
    title = Column(String(300), default="")
    prompt = Column(Text, default="")
    result_json = Column(Text, default="")
    raw_text = Column(Text, default="")
    overall_score = Column(Integer, default=0)
    outline_alignment_score = Column(Integer, default=0)
    world_consistency_score = Column(Integer, default=0)
    character_consistency_score = Column(Integer, default=0)
    plot_coherence_score = Column(Integer, default=0)
    pacing_score = Column(Integer, default=0)
    prose_score = Column(Integer, default=0)
    hook_score = Column(Integer, default=0)
    status = Column(String(20), default="candidate")  # candidate / current / discarded
    is_current = Column(Boolean, default=False)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)
    confirmed_at = Column(DateTime, nullable=True)

    world = relationship("World", foreign_keys=[world_id])
    draft = relationship("NovelDraft", foreign_keys=[draft_id])
    chapter_outline = relationship("NovelChapterOutline", foreign_keys=[chapter_outline_id])

    def __repr__(self):
        return f"<NovelDraftQualityReport id={self.id} status='{self.status}'>"


class NovelDraftRevision(Base):
    """AI-generated polished revision candidate for a novel draft."""
    __tablename__ = "novel_draft_revisions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    world_id = Column(Integer, ForeignKey("worlds.id"), nullable=False)
    draft_id = Column(Integer, ForeignKey("novel_drafts.id"), nullable=False)
    quality_report_id = Column(Integer, ForeignKey("novel_draft_quality_reports.id"), nullable=True)
    chapter_outline_id = Column(Integer, ForeignKey("novel_chapter_outlines.id"), nullable=True)
    volume_index = Column(Integer, default=0)
    chapter_index = Column(Integer, default=0)
    title = Column(String(300), default="")
    original_title = Column(String(300), default="")
    original_content_snapshot = Column(Text, default="")
    prompt = Column(Text, default="")
    content = Column(Text, default="")
    raw_text = Column(Text, default="")
    word_count = Column(Integer, default=0)
    revision_summary = Column(Text, default="")
    applied_suggestions_json = Column(Text, default="")
    status = Column(String(20), default="candidate")  # candidate / accepted / discarded
    is_accepted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)
    accepted_at = Column(DateTime, nullable=True)

    world = relationship("World", foreign_keys=[world_id])
    draft = relationship("NovelDraft", foreign_keys=[draft_id])
    quality_report = relationship("NovelDraftQualityReport", foreign_keys=[quality_report_id])
    chapter_outline = relationship("NovelChapterOutline", foreign_keys=[chapter_outline_id])

    def __repr__(self):
        return f"<NovelDraftRevision id={self.id} status='{self.status}'>"


class NovelFinalDraft(Base):
    """User-confirmed final adopted version for a novel draft chapter."""
    __tablename__ = "novel_final_drafts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    world_id = Column(Integer, ForeignKey("worlds.id"), nullable=False)
    draft_id = Column(Integer, ForeignKey("novel_drafts.id"), nullable=False)
    source_type = Column(String(20), nullable=False)  # draft / revision
    source_id = Column(Integer, nullable=False)
    chapter_outline_id = Column(Integer, ForeignKey("novel_chapter_outlines.id"), nullable=True)
    volume_index = Column(Integer, default=0)
    chapter_index = Column(Integer, default=0)
    title = Column(String(300), default="")
    content_snapshot = Column(Text, default="")
    word_count = Column(Integer, default=0)
    source_title = Column(String(300), default="")
    source_status = Column(String(20), default="")
    note = Column(Text, default="")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)
    accepted_at = Column(DateTime, default=_utcnow)
    revoked_at = Column(DateTime, nullable=True)

    world = relationship("World", foreign_keys=[world_id])
    draft = relationship("NovelDraft", foreign_keys=[draft_id])
    chapter_outline = relationship("NovelChapterOutline", foreign_keys=[chapter_outline_id])

    def __repr__(self):
        return f"<NovelFinalDraft id={self.id} active={self.is_active}>"
