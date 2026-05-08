"""
AI World Engine - World Context Service
Aggregates world setting data for AI simulation context.
"""

from typing import Dict, List
from sqlalchemy.orm import Session

from app.models import World, Character, Faction, Location, WorldRule, HistoricalEvent
from app.services.world_service import WorldService
from app.services.character_service import CharacterService
from app.services.faction_service import FactionService
from app.services.location_service import LocationService
from app.services.rule_service import RuleService
from app.services.event_service import EventService


class WorldContextService:
    """Service for building world context for AI simulation."""

    @staticmethod
    def build_world_context(db: Session, world_id: int) -> dict:
        """
        Build a comprehensive context dict for a world.
        Only includes data from the specified world.
        """
        world = WorldService.get_world(db, world_id)
        if not world:
            return {}

        characters = CharacterService.list_characters(db, world_id)
        factions = FactionService.list_factions(db, world_id)
        locations = LocationService.list_locations(db, world_id)
        rules = RuleService.list_rules(db, world_id)
        events = EventService.list_events(db, world_id)

        # Filter canon events only for context
        canon_events = [e for e in events if e.is_canon]

        context = {
            "world_name": world.name,
            "world_type": world.world_type or "",
            "description": world.description or "",
            "current_era": world.current_era or "",
            "tone": world.tone or "",
            "characters": [
                {
                    "name": c.name,
                    "role": c.role or "",
                    "personality": c.personality or "",
                    "goal": c.goal or "",
                    "abilities": c.abilities or "",
                    "current_status": c.current_status or "",
                    "faction_name": c.faction.name if c.faction else "",
                }
                for c in characters
            ],
            "factions": [
                {
                    "name": f.name,
                    "faction_type": f.faction_type or "",
                    "goal": f.goal or "",
                    "resources": f.resources or "",
                    "leader_name": f.leader.name if f.leader else "",
                }
                for f in factions
            ],
            "locations": [
                {
                    "name": loc.name,
                    "location_type": loc.location_type or "",
                    "region": loc.region or "",
                    "description": loc.description or "",
                }
                for loc in locations
            ],
            "rules": [
                {
                    "name": r.name,
                    "rule_type": r.rule_type or "",
                    "content": r.content or "",
                    "constraints": r.constraints or "",
                    "scope": r.scope or "",
                }
                for r in rules
            ],
            "events": [
                {
                    "title": e.title,
                    "event_time": e.event_time or "",
                    "content": e.content or "",
                    "consequences": e.consequences or "",
                }
                for e in canon_events
            ],
        }

        return context

    @staticmethod
    def build_context_snapshot(context: dict) -> str:
        """
        Convert a world context dict into a readable text snapshot.
        This snapshot is saved alongside simulation records for traceability.
        """
        lines = []

        lines.append(f"=== 世界设定快照 ===")
        lines.append(f"世界名称: {context.get('world_name', '未知')}")
        lines.append(f"世界类型: {context.get('world_type', '未知')}")
        lines.append(f"当前时代: {context.get('current_era', '未知')}")
        lines.append(f"世界基调: {context.get('tone', '未知')}")
        if context.get('description'):
            lines.append(f"简介: {context['description']}")

        characters = context.get('characters', [])
        if characters:
            lines.append(f"\n--- 角色 ({len(characters)}人) ---")
            for c in characters:
                parts = [f"  {c['name']}"]
                if c['role']:
                    parts.append(f"({c['role']})")
                if c['faction_name']:
                    parts.append(f"[{c['faction_name']}]")
                if c['personality']:
                    parts.append(f"性格:{c['personality']}")
                if c['goal']:
                    parts.append(f"目标:{c['goal']}")
                lines.append(" ".join(parts))

        factions = context.get('factions', [])
        if factions:
            lines.append(f"\n--- 势力 ({len(factions)}个) ---")
            for f in factions:
                parts = [f"  {f['name']}"]
                if f['faction_type']:
                    parts.append(f"({f['faction_type']})")
                if f['leader_name']:
                    parts.append(f"领袖:{f['leader_name']}")
                if f['goal']:
                    parts.append(f"目标:{f['goal']}")
                lines.append(" ".join(parts))

        locations = context.get('locations', [])
        if locations:
            lines.append(f"\n--- 地点 ({len(locations)}个) ---")
            for loc in locations:
                parts = [f"  {loc['name']}"]
                if loc['location_type']:
                    parts.append(f"({loc['location_type']})")
                if loc['region']:
                    parts.append(f"区域:{loc['region']}")
                lines.append(" ".join(parts))

        rules = context.get('rules', [])
        if rules:
            lines.append(f"\n--- 世界规则 ({len(rules)}条) ---")
            for r in rules:
                parts = [f"  {r['name']}"]
                if r['rule_type']:
                    parts.append(f"({r['rule_type']})")
                if r['content']:
                    parts.append(r['content'][:100])
                lines.append(" ".join(parts))

        events = context.get('events', [])
        if events:
            lines.append(f"\n--- 正史事件 ({len(events)}条) ---")
            for e in events:
                parts = [f"  [{e.get('event_time', '?')}] {e['title']}"]
                if e.get('content'):
                    parts.append(e['content'][:100])
                lines.append(" ".join(parts))

        return "\n".join(lines)
