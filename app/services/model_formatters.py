"""
AI World Engine - Model Formatters
Safe formatting functions for models used in Prompt building and page rendering.
All field accesses use getattr with fallback to avoid 500 errors on missing fields.
"""


def safe_get(obj, *names, default=""):
    """Get the first available attribute from a list of candidate names.
    Returns default if none are found or all are None/empty.
    """
    for name in names:
        if hasattr(obj, name):
            value = getattr(obj, name)
            if value is not None:
                return value
    return default


def format_character_for_prompt(character) -> dict:
    """Build a safe dict of character fields for Prompt generation."""
    return {
        "name": safe_get(character, "name"),
        "role": safe_get(character, "role", "identity", "position"),
        "personality": safe_get(character, "personality"),
        "goal": safe_get(character, "goal", "motivation"),
        "abilities": safe_get(character, "abilities", "ability"),
        "current_status": safe_get(character, "current_status", "status"),
        "notes": safe_get(character, "notes", "description", "background", "summary"),
    }


def format_character_summary(character) -> str:
    """Build a one-line summary for a character, safe for Prompt."""
    name = safe_get(character, "name")
    role = safe_get(character, "role", "identity", "position")
    personality = safe_get(character, "personality")
    parts = [name]
    if role:
        parts.append(role)
    if personality:
        parts.append(personality)
    return f"- {name}（{role}，{personality}）" if role else f"- {name}"


def format_faction_for_prompt(faction) -> dict:
    """Build a safe dict of faction fields for Prompt generation."""
    return {
        "name": safe_get(faction, "name"),
        "faction_type": safe_get(faction, "faction_type"),
        "leader": safe_get(faction, "leader"),
        "goal": safe_get(faction, "goal"),
        "resources": safe_get(faction, "resources"),
        "allies": safe_get(faction, "allies"),
        "enemies": safe_get(faction, "enemies"),
        "notes": safe_get(faction, "notes"),
    }


def format_faction_summary(faction) -> str:
    """Build a one-line summary for a faction."""
    name = safe_get(faction, "name")
    ftype = safe_get(faction, "faction_type")
    leader = faction.leader.name if getattr(faction, "leader", None) else "无"
    return f"- {name}（{ftype}，领袖：{leader}）"


def format_location_for_prompt(location) -> dict:
    """Build a safe dict of location fields."""
    return {
        "name": safe_get(location, "name"),
        "location_type": safe_get(location, "location_type"),
        "region": safe_get(location, "region"),
        "description": safe_get(location, "description"),
        "important_events": safe_get(location, "important_events"),
    }


def format_location_summary(location) -> str:
    """Build a one-line summary for a location."""
    name = safe_get(location, "name")
    ltype = safe_get(location, "location_type")
    region = safe_get(location, "region")
    return f"- {name}（{ltype}，{region}）"


def format_rule_for_prompt(rule) -> dict:
    """Build a safe dict of rule fields."""
    return {
        "name": safe_get(rule, "name"),
        "rule_type": safe_get(rule, "rule_type"),
        "content": safe_get(rule, "content"),
        "constraints": safe_get(rule, "constraints"),
        "scope": safe_get(rule, "scope"),
    }


def format_rule_summary(rule) -> str:
    """Build a one-line summary for a rule."""
    name = safe_get(rule, "name")
    rtype = safe_get(rule, "rule_type")
    return f"- {name}（{rtype}）"


def format_event_for_prompt(event) -> dict:
    """Build a safe dict of event fields."""
    return {
        "title": safe_get(event, "title", "name"),
        "description": safe_get(event, "description", "summary"),
        "era": safe_get(event, "era", "period"),
        "is_canon": safe_get(event, "is_canon", default=False),
    }


def format_style_profile_for_prompt(profile) -> dict:
    """Build a safe dict of style profile fields."""
    return {
        "name": safe_get(profile, "name"),
        "description": safe_get(profile, "description"),
        "genre": safe_get(profile, "genre"),
        "narrative_pov": safe_get(profile, "narrative_pov"),
        "pacing": safe_get(profile, "pacing"),
        "dialogue_style": safe_get(profile, "dialogue_style"),
        "conflict_style": safe_get(profile, "conflict_style"),
        "do_rules": safe_get(profile, "do_rules"),
        "avoid_rules": safe_get(profile, "avoid_rules"),
        "style_rules_json": safe_get(profile, "style_rules_json"),
    }


def format_context_package_for_prompt(package) -> dict:
    """Build a safe dict of context package fields."""
    return {
        "name": safe_get(package, "name"),
        "description": safe_get(package, "description"),
        "evolution_id": safe_get(package, "evolution_id", "source_evolution_id"),
        "style_profile_id": safe_get(package, "style_profile_id"),
        "plot_anchor_id": safe_get(package, "plot_anchor_id"),
    }
