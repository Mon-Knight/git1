"""
AI World Engine - Import Service
Validates and imports a world from an export JSON payload.
All imports create a NEW world (never overwrites existing).
Uses database transactions for safety.
"""

import re
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.models import (
    World, Character, Faction, Location, WorldRule,
    HistoricalEvent, SimulationRecord, Branch,
)

SUPPORTED_EXPORT_VERSIONS = {"1.0"}


def _row_to_model(model_class, data: dict):
    """Create a model instance from a dict, skipping id (auto-increment)."""
    instance = model_class()
    allowed = {col.name for col in model_class.__table__.columns}
    for key, val in data.items():
        if key in allowed and key != "id":
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

    # Generate unique name
    new_name = _generate_unique_world_name(db, original_name)

    # Create new world
    new_world = World(name=new_name)
    for key in ("world_type", "description", "current_era", "tone"):
        if key in world_data:
            setattr(new_world, key, world_data.get(key, ""))
    db.add(new_world)
    db.flush()  # get new_world.id

    counts = {
        "characters": _import_list(db, Character, data.get("characters", []), new_world.id),
        "factions": _import_list(db, Faction, data.get("factions", []), new_world.id),
        "locations": _import_list(db, Location, data.get("locations", []), new_world.id),
        "rules": _import_list(db, WorldRule, data.get("rules", []), new_world.id),
        "historical_events": _import_list(db, HistoricalEvent, data.get("historical_events", []), new_world.id),
        "simulation_records": _import_sim_records(db, data.get("simulation_records", []), new_world.id),
        "branches": _import_branches(db, data.get("branches", []), new_world.id),
    }

    has_novel = any(
        r.simulation_type == "novel_evolution"
        for r in db.query(SimulationRecord).filter(SimulationRecord.world_id == new_world.id).all()
    )

    return {
        "new_world_id": new_world.id,
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


def _import_sim_records(db: Session, items: list, new_world_id: int) -> int:
    """Import simulation_records with world_id remap."""
    return _import_list(db, SimulationRecord, items, new_world_id)


def _import_branches(db: Session, items: list, new_world_id: int) -> int:
    """Import branches with world_id remap."""
    return _import_list(db, Branch, items, new_world_id)
