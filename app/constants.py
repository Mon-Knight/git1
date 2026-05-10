"""
AI World Engine - Application Constants
Centralized definitions for simulation types and other common values.

v1.4.0 will introduce novel_evolution type for Novel Engineering mode.
"""

# Simulation types used in simulation_records and AI routing
SIMULATION_TYPES = {
    "general": "普通推演",
    "world_simulation": "世界推演",
    "protagonist_route": "主角路线推演",
    "novel_evolution": "小说演化推演",
    "world_reaction": "世界反应推演",
}

# Default simulation type when not specified
DEFAULT_SIMULATION_TYPE = "general"

# Friendly name map for display (includes Chinese legacy types for backward compat)
SIMULATION_TYPE_LABELS = {
    "": "普通推演",
    "general": "普通推演",
    "world_simulation": "世界推演",
    "protagonist_route": "主角路线推演",
    "novel_evolution": "小说演化推演",
    "world_reaction": "世界反应推演",
    # Legacy Chinese types (from earlier versions)
    "剧情发展": "剧情发展",
    "角色行动": "角色行动",
    "势力冲突": "势力冲突",
    "世界规则影响": "世界规则影响",
    "历史事件后果": "历史事件后果",
}

# Snapshot metadata structure version
CONTEXT_SNAPSHOT_VERSION = 1


def get_simulation_type_label(type_value: str) -> str:
    """Return a human-friendly label for a simulation type value."""
    return SIMULATION_TYPE_LABELS.get(type_value, type_value or "普通推演")
