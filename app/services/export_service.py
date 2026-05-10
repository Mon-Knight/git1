"""
AI World Engine - Export Service
Serializes a single world plus all its children to a JSON-safe dict.
"""

import json
import re
from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.config import settings


# Non-serializable sentinel (exclude from export)
_EXCLUDE = object()


def _row_to_dict(row) -> Dict[str, Any]:
    """Convert an ORM row to a plain dict, skipping relationships."""
    result = {}
    for col in row.__table__.columns:
        val = getattr(row, col.name)
        if isinstance(val, datetime):
            val = val.isoformat()
        result[col.name] = val
    return result


def sanitize_filename(name: str) -> str:
    """Replace characters invalid in Windows filenames."""
    return re.sub(r'[<>:"/\\|?*]', '_', name).strip()[:100]


def export_world_to_dict(db: Session, world_id: int) -> Dict[str, Any]:
    """Export a single world + all children as a JSON-safe dict.

    Raises ValueError if world not found.
    """
    from app.models import (
        World, Character, Faction, Location, WorldRule,
        HistoricalEvent, SimulationRecord, Branch,
    )

    world = db.query(World).filter(World.id == world_id).first()
    if not world:
        raise ValueError(f"World not found: world_id={world_id}")

    characters = db.query(Character).filter(Character.world_id == world_id).all()
    factions = db.query(Faction).filter(Faction.world_id == world_id).all()
    locations = db.query(Location).filter(Location.world_id == world_id).all()
    rules = db.query(WorldRule).filter(WorldRule.world_id == world_id).all()
    events = db.query(HistoricalEvent).filter(HistoricalEvent.world_id == world_id).all()
    records = db.query(SimulationRecord).filter(SimulationRecord.world_id == world_id).all()
    branches = db.query(Branch).filter(Branch.world_id == world_id).all()

    has_novel_evolution = any(r.simulation_type == "novel_evolution" for r in records)

    payload = {
        "export_version": "1.0",
        "export_type": "single_world",
        "app_name": "AI World Engine",
        "app_version": settings.VERSION,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "source": {
            "world_id": world.id,
            "world_name": world.name,
        },
        "data": {
            "world": _row_to_dict(world),
            "characters": [_row_to_dict(c) for c in characters],
            "factions": [_row_to_dict(f) for f in factions],
            "locations": [_row_to_dict(l) for l in locations],
            "rules": [_row_to_dict(r) for r in rules],
            "historical_events": [_row_to_dict(e) for e in events],
            "simulation_records": [_row_to_dict(r) for r in records],
            "branches": [_row_to_dict(b) for b in branches],
        },
        "metadata": {
            "counts": {
                "characters": len(characters),
                "factions": len(factions),
                "locations": len(locations),
                "rules": len(rules),
                "historical_events": len(events),
                "simulation_records": len(records),
                "branches": len(branches),
            },
            "contains_novel_evolution": has_novel_evolution,
            "contains_branches": len(branches) > 0,
            "contains_simulation_records": len(records) > 0,
        },
    }
    return payload


def export_world_json(db: Session, world_id: int) -> str:
    """Export a world as a formatted JSON string (UTF-8, readable)."""
    payload = export_world_to_dict(db, world_id)
    return json.dumps(payload, ensure_ascii=False, indent=2)


def make_export_filename(world_name: str) -> str:
    """Generate a safe export filename."""
    safe_name = sanitize_filename(world_name)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"AIWorldEngine-world-{safe_name}-v{settings.VERSION}-{timestamp}.json"
