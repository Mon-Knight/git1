"""
AI World Engine - Application Constants
Centralized definitions for simulation types and other common values.
"""

# Simulation types used in simulation_records and AI routing
SIMULATION_TYPES = {
    "general": "普通推演",
    "world_simulation": "世界推演",
    "protagonist_route": "主角路线推演",
    "novel_evolution": "小说工程推演",
    "world_reaction": "世界反应推演",
}

# Default simulation type when not specified
DEFAULT_SIMULATION_TYPE = "general"

# Novel engineering constant
SIMULATION_TYPE_NOVEL_EVOLUTION = "novel_evolution"

# Friendly name map for display (includes Chinese legacy types for backward compat)
SIMULATION_TYPE_LABELS = {
    "": "普通推演",
    "general": "普通推演",
    "world_simulation": "世界推演",
    "protagonist_route": "主角路线推演",
    "novel_evolution": "小说工程推演",
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


# Novel engineering form field names (for build_novel_evolution_prompt)
NOVEL_FORM_FIELDS = [
    "protagonist_name",
    "protagonist_identity",
    "protagonist_power",
    "protagonist_start",
    "main_story_direction",
    "core_conflict",
    "genre",
    "target_word_count",
    "volume_count",
    "writing_style",
    "pacing_preference",
    "conflict_density",
    "dialogue_ratio",
    "description_density",
    "information_release",
    "banned_patterns",
    "extra_requirements",
]

# Chinese display labels for novel form fields
NOVEL_FORM_LABELS = {
    "protagonist_name": "主角姓名",
    "protagonist_identity": "主角身份",
    "protagonist_power": "主角特殊能力",
    "protagonist_start": "主角初始处境",
    "main_story_direction": "主线方向",
    "core_conflict": "核心冲突",
    "genre": "题材类型",
    "target_word_count": "目标字数",
    "volume_count": "预计卷数",
    "writing_style": "写作风格",
    "pacing_preference": "节奏偏好",
    "conflict_density": "冲突密度",
    "dialogue_ratio": "对话比例",
    "description_density": "描写密度",
    "information_release": "信息释放方式",
    "banned_patterns": "禁用写法",
    "extra_requirements": "补充要求",
}
