"""
AI World Engine - Export File Service
Handles export filename generation, payload building, file writing,
and security validation for desktop mode saves.
"""

import os
import re
import json
from datetime import datetime
from typing import Dict, Any, Optional, List


class ExportFileService:
    """Service for building export payloads, generating filenames, and writing files."""

    @staticmethod
    def build_export_filename(
        export_type: str,
        world_name: Optional[str] = None,
        ext: str = "json",
    ) -> str:
        """Generate a safe export filename.

        Naming pattern: AIWorldEngine_{type}_{name}_{timestamp}.{ext}
        """
        # Sanitize world_name: strip illegal Windows filename chars
        if world_name:
            safe_name = re.sub(r'[<>:"/\\|?*]', '_', world_name)
            safe_name = safe_name.strip().replace(' ', '_')
            # Truncate long names
            if len(safe_name) > 40:
                safe_name = safe_name[:40]
        else:
            safe_name = None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        parts = ["AIWorldEngine", export_type]
        if safe_name:
            parts.append(safe_name)
        parts.append(timestamp)

        filename = "_".join(parts) + "." + ext.lstrip('.')
        return filename

    @staticmethod
    def build_world_export_payload(db, world_id: int) -> Dict[str, Any]:
        """Build the JSON payload for a single world export."""
        from app.models import (
            World, Character, Faction, Location, WorldRule,
            HistoricalEvent, SimulationRecord, Branch,
        )

        world = db.query(World).filter(World.id == world_id).first()
        if not world:
            return {}

        characters = db.query(Character).filter(Character.world_id == world_id).all()
        factions = db.query(Faction).filter(Faction.world_id == world_id).all()
        locations = db.query(Location).filter(Location.world_id == world_id).all()
        rules = db.query(WorldRule).filter(WorldRule.world_id == world_id).all()
        events = db.query(HistoricalEvent).filter(HistoricalEvent.world_id == world_id).all()
        simulations = db.query(SimulationRecord).filter(SimulationRecord.world_id == world_id).all()
        branches = db.query(Branch).filter(Branch.world_id == world_id).all()

        return {
            "metadata": {
                "app_version": "1.7.8",
                "export_type": "world",
                "exported_at": datetime.utcnow().isoformat() + "Z",
                "world_id": world.id,
                "world_name": world.name,
                "record_count": len(characters) + len(factions) + len(locations) + len(rules) + len(events) + len(simulations),
            },
            "world": {
                "id": world.id,
                "name": world.name,
                "world_type": world.world_type,
                "description": world.description,
                "current_era": world.current_era,
                "tone": world.tone,
            },
            "characters": [_row_to_dict(c) for c in characters],
            "factions": [_row_to_dict(f) for f in factions],
            "locations": [_row_to_dict(l) for l in locations],
            "rules": [_row_to_dict(r) for r in rules],
            "historical_events": [_row_to_dict(e) for e in events],
            "simulation_records": [_row_to_dict(s) for s in simulations],
            "branches": [_row_to_dict(b) for b in branches],
        }

    @staticmethod
    def build_context_assets_payload(db, world_id: int) -> Dict[str, Any]:
        """Build JSON payload for context assets export."""
        from app.models import ContextPackage, StyleProfile, PlotAnchor

        world = db.query(db).first()  # placeholder, need World model
        from app.models import World
        world_obj = db.query(World).filter(World.id == world_id).first()
        if not world_obj:
            return {}

        packages = db.query(ContextPackage).filter(ContextPackage.world_id == world_id).all()
        styles = db.query(StyleProfile).filter(
            (StyleProfile.world_id == world_id) | (StyleProfile.world_id.is_(None))
        ).all()
        anchors = db.query(PlotAnchor).filter(PlotAnchor.world_id == world_id).all()

        return {
            "metadata": {
                "app_version": "1.7.8",
                "export_type": "context_assets",
                "exported_at": datetime.utcnow().isoformat() + "Z",
                "world_id": world_id,
                "world_name": world_obj.name,
            },
            "style_profiles": [_row_to_dict(s) for s in styles],
            "plot_anchors": [_row_to_dict(a) for a in anchors],
            "context_packages": [_row_to_dict(p) for p in packages],
        }

    @staticmethod
    def write_export_file(path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Write JSON payload to a file. Returns result dict."""
        try:
            path = os.path.abspath(path)
            dirname = os.path.dirname(path)
            if dirname and not os.path.exists(dirname):
                os.makedirs(dirname, exist_ok=True)

            with open(path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2, default=str)

            return {"ok": True, "path": path}
        except OSError as e:
            return {"ok": False, "error": str(e)}

    @staticmethod
    def validate_desktop_export_path(path: str) -> Dict[str, Any]:
        """Validate a desktop-mode export save path. Returns result dict."""
        if not path or not path.strip():
            return {"ok": False, "error": "路径不能为空"}

        # Normalize
        try:
            path = os.path.abspath(path)
        except Exception:
            return {"ok": False, "error": "路径无效"}

        # Must not be a directory
        if os.path.isdir(path):
            return {"ok": False, "error": "路径指向目录，请指定文件名"}

        # Block path traversal
        normalized = path.replace("\\", "/")
        if ".." in normalized.split("/"):
            return {"ok": False, "error": "路径不允许包含 .."}

        return {"ok": True, "path": path}

    @staticmethod
    def sanitize_payload_for_export(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive fields from export payload."""
        sensitive_keys = {
            "api_key", "secret", "token", "password", "env",
            "log_path", "server_log", "crash_log", "authorization",
        }

        def _clean(obj):
            if isinstance(obj, dict):
                return {
                    k: _clean(v)
                    for k, v in obj.items()
                    if k.lower() not in sensitive_keys and not any(
                        sk in k.lower() for sk in sensitive_keys
                    )
                }
            elif isinstance(obj, list):
                return [_clean(item) for item in obj]
            return obj

        return _clean(payload)


def _row_to_dict(row) -> Dict[str, Any]:
    """Convert a SQLAlchemy model row to a dict, excluding _sa_instance_state."""
    if row is None:
        return {}
    result = {}
    for col in row.__table__.columns:
        result[col.name] = getattr(row, col.name)
    return result
