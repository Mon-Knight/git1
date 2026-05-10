"""
AI World Engine - Import Service
Validates and imports a world from an export JSON payload.
All imports create a NEW world (never overwrites existing).
Uses database transactions for safety.
"""

import re
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.models import (
    World, Character, Faction, Location, WorldRule,
    HistoricalEvent, SimulationRecord, Branch,
    StyleProfile, PlotAnchor, ContextPackage,
)

SUPPORTED_EXPORT_VERSIONS = {"1.0"}


def _row_to_model(model_class, data: dict):
    """Create a model instance from a dict, skipping id (auto-increment).
    Converts ISO datetime strings back to datetime objects for DateTime columns.
    """
    from sqlalchemy import DateTime
    instance = model_class()
    allowed = {col.name for col in model_class.__table__.columns}
    datetime_cols = {col.name for col in model_class.__table__.columns if isinstance(col.type, DateTime)}
    for key, val in data.items():
        if key in allowed and key != "id":
            if key in datetime_cols and isinstance(val, str):
                try:
                    # Handle ISO format with/without timezone
                    val = val.replace("Z", "+00:00")
                    val = datetime.fromisoformat(val)
                    # Strip timezone info (SQLite doesn't support it)
                    if val.tzinfo is not None:
                        val = val.replace(tzinfo=None)
                except (ValueError, TypeError):
                    pass  # Keep as-is if parsing fails
            setattr(instance, key, val)
    return instance


def validate_export_payload(payload: dict) -> None:
    """Validate the top-level structure of an export JSON.
    Raises ValueError with a human-readable message on failure."""
    if not isinstance(payload, dict):
        raise ValueError("文件格式无效：不是合法的 JSON 对象。")

    export_type = payload.get("export_type", "")
    if export_type != "single_world":
        raise ValueError(f"不支持的文件类型：{export_type}。只支持 single_world 导出文件。")

    export_version = payload.get("export_version", "")
    if export_version not in SUPPORTED_EXPORT_VERSIONS:
        raise ValueError(f"不支持的导出版本：{export_version}。支持的版本：{', '.join(SUPPORTED_EXPORT_VERSIONS)}")

    data = payload.get("data")
    if not data or not data.get("world"):
        raise ValueError("文件缺少 world 数据，无法导入。")


def _generate_unique_world_name(db: Session, original_name: str) -> str:
    """Generate a unique world name, appending ' - 导入副本 N' if needed."""
    base = original_name
    candidate = base + " - 导入副本"
    existing = db.query(World).filter(World.name == candidate).first()
    if not existing:
        return candidate
    n = 2
    while True:
        candidate = f"{base} - 导入副本 {n}"
        if not db.query(World).filter(World.name == candidate).first():
            return candidate
        n += 1


def import_world_from_payload(db: Session, payload: dict) -> Dict[str, Any]:
    """Import a world from an export payload.
    Creates a new world, remaps all IDs. Operates in a transaction.
    Returns a result dict with counts.
    """
    validate_export_payload(payload)

    data = payload["data"]

    # Get original world name
    world_data = data["world"]
    original_name = world_data.get("name", "导入世界")
    old_world_id = world_data.get("id", 0)

    # Generate unique name
    new_name = _generate_unique_world_name(db, original_name)

    # Create new world
    new_world = World(name=new_name)
    for key in ("world_type", "description", "current_era", "tone"):
        if key in world_data:
            setattr(new_world, key, world_data.get(key, ""))
    db.add(new_world)
    db.flush()  # get new_world.id

    new_world_id = new_world.id

    # ID maps: old_id -> new_id
    sim_id_map = {}  # old sim record id -> new sim record id
    style_id_map = {}  # old style profile id -> new style profile id
    anchor_id_map = {}  # old plot anchor id -> new plot anchor id

    counts = {
        "characters": _import_list(db, Character, data.get("characters", []), new_world_id),
        "factions": _import_list(db, Faction, data.get("factions", []), new_world_id),
        "locations": _import_list(db, Location, data.get("locations", []), new_world_id),
        "rules": _import_list(db, WorldRule, data.get("rules", []), new_world_id),
        "historical_events": _import_list(db, HistoricalEvent, data.get("historical_events", []), new_world_id),
        "simulation_records": _import_sim_records(db, data.get("simulation_records", []), new_world_id, sim_id_map),
        "branches": _import_branches(db, data.get("branches", []), new_world_id, sim_id_map),
        "style_profiles": _import_style_profiles(db, data.get("style_profiles", []), new_world_id, old_world_id, style_id_map),
        "plot_anchors": _import_plot_anchors(db, data.get("plot_anchors", []), new_world_id, anchor_id_map),
    }

    # Import context_packages with ID remapping
    counts["context_packages"] = _import_context_packages(
        db, data.get("context_packages", []), new_world_id,
        sim_id_map, style_id_map, anchor_id_map,
    )

    has_novel = any(
        r.simulation_type == "novel_evolution"
        for r in db.query(SimulationRecord).filter(SimulationRecord.world_id == new_world_id).all()
    )

    return {
        "new_world_id": new_world_id,
        "new_world_name": new_name,
        "counts": counts,
        "contains_novel_evolution": has_novel,
    }


def _import_list(db: Session, model_class, items: list, new_world_id: int) -> int:
    """Import a list of items, setting world_id to new_world_id. Returns count."""
    count = 0
    for item in items:
        if not isinstance(item, dict):
            continue
        instance = _row_to_model(model_class, item)
        instance.id = None  # ensure auto-increment
        instance.world_id = new_world_id
        db.add(instance)
        count += 1
    db.flush()
    return count


def _import_sim_records(
    db: Session, items: list, new_world_id: int, id_map: dict = None
) -> int:
    """Import simulation_records with world_id remap and ID mapping."""
    count = 0
    for item in items:
        if not isinstance(item, dict):
            continue
        old_id = item.get("id")
        instance = _row_to_model(SimulationRecord, item)
        instance.id = None
        instance.world_id = new_world_id
        db.add(instance)
        db.flush()  # get new id
        if id_map is not None and old_id is not None:
            id_map[old_id] = instance.id
        count += 1
    return count


def _import_branches(
    db: Session, items: list, new_world_id: int, sim_id_map: dict = None
) -> int:
    """Import branches with world_id remap and simulation_id remap."""
    count = 0
    for item in items:
        if not isinstance(item, dict):
            continue
        instance = _row_to_model(Branch, item)
        instance.id = None
        instance.world_id = new_world_id
        # Remap simulation_id
        old_sim_id = item.get("simulation_id")
        if old_sim_id and sim_id_map and old_sim_id in sim_id_map:
            instance.simulation_id = sim_id_map[old_sim_id]
        db.add(instance)
        count += 1
    db.flush()
    return count


def _import_style_profiles(
    db: Session, items: list, new_world_id: int, old_world_id: int, id_map: dict
) -> int:
    """Import style profiles with ID remapping. Global profiles kept global."""
    count = 0
    for item in items:
        if not isinstance(item, dict):
            continue
        old_id = item.get("id")
        old_item_world_id = item.get("world_id")

        instance = _row_to_model(StyleProfile, item)
        instance.id = None

        # If the original style was world-specific (world_id == old_world_id), remap to new_world_id
        if old_item_world_id is not None and old_item_world_id == old_world_id:
            instance.world_id = new_world_id
        elif old_item_world_id is None:
            # Global style: check if a global style with same name already exists
            existing = (
                db.query(StyleProfile)
                .filter(StyleProfile.world_id.is_(None))
                .filter(StyleProfile.name == instance.name)
                .first()
            )
            if existing:
                if old_id is not None:
                    id_map[old_id] = existing.id
                continue  # Skip importing duplicate global style
            instance.world_id = None
        else:
            instance.world_id = new_world_id

        db.add(instance)
        db.flush()
        if old_id is not None:
            id_map[old_id] = instance.id
        count += 1
    return count


def _import_plot_anchors(
    db: Session, items: list, new_world_id: int, id_map: dict
) -> int:
    """Import plot anchors with world_id and ID remapping."""
    count = 0
    for item in items:
        if not isinstance(item, dict):
            continue
        old_id = item.get("id")
        instance = _row_to_model(PlotAnchor, item)
        instance.id = None
        instance.world_id = new_world_id
        db.add(instance)
        db.flush()
        if old_id is not None:
            id_map[old_id] = instance.id
        count += 1
    return count


def _import_context_packages(
    db: Session, items: list, new_world_id: int,
    sim_id_map: dict, style_id_map: dict, anchor_id_map: dict,
) -> int:
    """Import context packages with full ID remapping for all references."""
    count = 0
    for item in items:
        if not isinstance(item, dict):
            continue
        instance = _row_to_model(ContextPackage, item)
        instance.id = None
        instance.world_id = new_world_id

        # Remap simulation_record_id
        old_sim_id = item.get("simulation_record_id")
        if old_sim_id and sim_id_map and old_sim_id in sim_id_map:
            instance.simulation_record_id = sim_id_map[old_sim_id]
        else:
            instance.simulation_record_id = None

        # Remap style_profile_id
        old_style_id = item.get("style_profile_id")
        if old_style_id and style_id_map and old_style_id in style_id_map:
            instance.style_profile_id = style_id_map[old_style_id]
        else:
            instance.style_profile_id = None

        # Remap plot_anchor_id
        old_anchor_id = item.get("plot_anchor_id")
        if old_anchor_id and anchor_id_map and old_anchor_id in anchor_id_map:
            instance.plot_anchor_id = anchor_id_map[old_anchor_id]
        else:
            instance.plot_anchor_id = None

        db.add(instance)
        count += 1
    db.flush()
    return count
