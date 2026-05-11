"""
AI World Engine - Setting Suggestion Adoption Service
Handles adopt, edit-adopt, and discard of AI-generated candidate settings.
v1.7.10: Adoption closure - NO auto-adoption, user-confirmed only.
"""

import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from app.models import SettingSuggestion, Character, Faction, Location, WorldRule


class SettingSuggestionAdoptionService:
    """Service for adopting, editing, and discarding setting suggestions."""

    VALID_STATUSES = ("pending", "adopted", "edited_adopted", "discarded")
    ADOPTABLE_TYPES = ("character", "faction", "location", "rule")

    @staticmethod
    def can_adopt(suggestion: SettingSuggestion) -> tuple:
        """Check if a suggestion can be adopted. Returns (can_adopt: bool, reason: str)."""
        if suggestion.status != "pending":
            return False, f"候选状态为 {suggestion.status}，只有 pending 状态的候选可以采纳"
        if suggestion.suggestion_type not in SettingSuggestionAdoptionService.ADOPTABLE_TYPES:
            return False, f"不支持的候选类型: {suggestion.suggestion_type}"
        if not suggestion.result_json:
            return False, "候选结果为空"
        return True, ""

    @staticmethod
    def extract_items(suggestion: SettingSuggestion) -> List[Dict[str, Any]]:
        """Extract candidate items from result_json."""
        try:
            data = json.loads(suggestion.result_json)
            if isinstance(data, dict):
                items = data.get("parsed", []) or data.get("items", [])
                if not items and "raw" in data:
                    return []
                return items if isinstance(items, list) else []
            if isinstance(data, list):
                return data
            return []
        except (json.JSONDecodeError, TypeError):
            return []

    @staticmethod
    def _map_to_character(db: Session, world_id: int, item: Dict[str, Any]) -> Character:
        """Map candidate item to Character model."""
        desc_parts = []
        for k in ("identity", "faction", "personality", "goal", "ability", "weakness",
                  "current_status", "plot_role", "relation_to_mainline"):
            if item.get(k):
                desc_parts.append(f"{k}: {item[k]}")
        desc = "\n".join(desc_parts) if desc_parts else ""
        char = Character(
            world_id=world_id,
            name=item.get("name", "未命名角色"),
            role=item.get("identity", ""),
            personality=item.get("personality", ""),
            goal=item.get("goal", ""),
            abilities=item.get("ability", ""),
            current_status=item.get("current_status", "存活"),
            notes=desc,
        )
        db.add(char)
        db.flush()
        return char

    @staticmethod
    def _map_to_faction(db: Session, world_id: int, item: Dict[str, Any]) -> Faction:
        """Map candidate item to Faction model."""
        desc_parts = []
        for k in ("core_goal", "resources", "allies", "enemies", "territory",
                  "internal_conflict", "plot_role"):
            if item.get(k):
                desc_parts.append(f"{k}: {item[k]}")
        desc = "\n".join(desc_parts) if desc_parts else ""
        faction = Faction(
            world_id=world_id,
            name=item.get("name", "未命名势力"),
            faction_type=item.get("faction_type", ""),
            goal=item.get("core_goal", ""),
            resources=item.get("resources", ""),
            enemies=item.get("enemies", "[]"),
            allies=item.get("allies", "[]"),
            notes=desc,
        )
        db.add(faction)
        db.flush()
        return faction

    @staticmethod
    def _map_to_location(db: Session, world_id: int, item: Dict[str, Any]) -> Location:
        """Map candidate item to Location model."""
        desc = item.get("description", "")
        extra = []
        for k in ("region", "danger_level", "important_resource", "key_history",
                  "possible_plot", "controlling_faction"):
            if item.get(k):
                extra.append(f"{k}: {item[k]}")
        full_desc = desc + ("\n\n" + "\n".join(extra) if extra else "")
        loc = Location(
            world_id=world_id,
            name=item.get("name", "未命名地点"),
            location_type=item.get("location_type", ""),
            region=item.get("region", ""),
            description=full_desc,
        )
        db.add(loc)
        db.flush()
        return loc

    @staticmethod
    def _map_to_rule(db: Session, world_id: int, item: Dict[str, Any]) -> WorldRule:
        """Map candidate item to WorldRule model."""
        desc_parts = []
        for k in ("limitation", "influence_scope", "possible_conflict", "plot_usage"):
            if item.get(k):
                desc_parts.append(f"{k}: {item[k]}")
        extra = "\n".join(desc_parts)
        rule = WorldRule(
            world_id=world_id,
            name=item.get("name", "未命名规则"),
            rule_type=item.get("rule_type", ""),
            content=item.get("content", ""),
            constraints=extra,
        )
        db.add(rule)
        db.flush()
        return rule

    @staticmethod
    def _get_mapper(suggestion_type: str):
        """Return the mapper function for a suggestion type."""
        mappers = {
            "character": SettingSuggestionAdoptionService._map_to_character,
            "faction": SettingSuggestionAdoptionService._map_to_faction,
            "location": SettingSuggestionAdoptionService._map_to_location,
            "rule": SettingSuggestionAdoptionService._map_to_rule,
        }
        return mappers.get(suggestion_type)

    @staticmethod
    def adopt(
        db: Session, world_id: int, suggestion_id: int, item_index: int = 0
    ) -> Dict[str, Any]:
        """Adopt a specific candidate item as a formal setting record."""
        suggestion = db.query(SettingSuggestion).filter(
            SettingSuggestion.id == suggestion_id,
            SettingSuggestion.world_id == world_id,
        ).first()

        if not suggestion:
            return {"ok": False, "error": "候选记录不存在"}

        can_adopt, reason = SettingSuggestionAdoptionService.can_adopt(suggestion)
        if not can_adopt:
            return {"ok": False, "error": reason}

        items = SettingSuggestionAdoptionService.extract_items(suggestion)
        if not items:
            return {"ok": False, "error": "无法解析候选内容"}
        if item_index < 0 or item_index >= len(items):
            return {"ok": False, "error": f"item_index {item_index} 不合法，共 {len(items)} 条候选"}

        item = items[item_index]
        mapper = SettingSuggestionAdoptionService._get_mapper(suggestion.suggestion_type)
        if not mapper:
            return {"ok": False, "error": f"不支持的类型: {suggestion.suggestion_type}"}

        try:
            target = mapper(db, world_id, item)
            suggestion.status = "adopted"
            suggestion.adopted_target_id = target.id
            suggestion.adopted_target_type = suggestion.suggestion_type
            suggestion.adopted_at = datetime.now(timezone.utc)
            db.commit()
            return {
                "ok": True,
                "target_id": target.id,
                "target_type": suggestion.suggestion_type,
                "status": "adopted",
            }
        except Exception as e:
            db.rollback()
            return {"ok": False, "error": f"创建正式记录失败: {str(e)}"}

    @staticmethod
    def adopt_with_edit(
        db: Session, world_id: int, suggestion_id: int,
        item_index: int, edited_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Adopt a candidate item with user edits."""
        suggestion = db.query(SettingSuggestion).filter(
            SettingSuggestion.id == suggestion_id,
            SettingSuggestion.world_id == world_id,
        ).first()

        if not suggestion:
            return {"ok": False, "error": "候选记录不存在"}

        can_adopt, reason = SettingSuggestionAdoptionService.can_adopt(suggestion)
        if not can_adopt:
            return {"ok": False, "error": reason}

        # Validate required fields
        name = edited_data.get("name", "").strip()
        if not name:
            return {"ok": False, "error": "名称不能为空"}

        mapper = SettingSuggestionAdoptionService._get_mapper(suggestion.suggestion_type)
        if not mapper:
            return {"ok": False, "error": f"不支持的类型: {suggestion.suggestion_type}"}

        try:
            target = mapper(db, world_id, edited_data)
            suggestion.status = "edited_adopted"
            suggestion.adopted_target_id = target.id
            suggestion.adopted_target_type = suggestion.suggestion_type
            suggestion.adopted_at = datetime.now(timezone.utc)
            db.commit()
            return {
                "ok": True,
                "target_id": target.id,
                "target_type": suggestion.suggestion_type,
                "status": "edited_adopted",
            }
        except Exception as e:
            db.rollback()
            return {"ok": False, "error": f"创建正式记录失败: {str(e)}"}

    @staticmethod
    def discard(db: Session, world_id: int, suggestion_id: int) -> Dict[str, Any]:
        """Discard a setting suggestion."""
        suggestion = db.query(SettingSuggestion).filter(
            SettingSuggestion.id == suggestion_id,
            SettingSuggestion.world_id == world_id,
        ).first()

        if not suggestion:
            return {"ok": False, "error": "候选记录不存在"}

        if suggestion.status != "pending":
            return {"ok": False, "error": f"候选状态为 {suggestion.status}，无法废弃"}

        suggestion.status = "discarded"
        db.commit()
        return {"ok": True, "status": "discarded"}

    @staticmethod
    def build_adoption_preview(suggestion: SettingSuggestion) -> Dict[str, Any]:
        """Build a preview showing what will be adopted."""
        items = SettingSuggestionAdoptionService.extract_items(suggestion)
        target_tables = {
            "character": "角色 (characters)",
            "faction": "势力 (factions)",
            "location": "地点 (locations)",
            "rule": "规则 (world_rules)",
        }
        return {
            "suggestion_type": suggestion.suggestion_type,
            "target_table": target_tables.get(suggestion.suggestion_type, "未知"),
            "item_count": len(items),
            "items": items,
        }
