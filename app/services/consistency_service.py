"""
AI World Engine - Consistency Service
Rule-based setting conflict checks.
"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from app.models import WorldRule, HistoricalEvent, Character, Faction


class ConsistencyService:
    """Service for checking setting consistency and conflicts."""

    @staticmethod
    def check_setting_conflicts(
        db: Session,
        world_id: int,
        content: str,
        check_types: List[str] = None,
    ) -> dict:
        """
        Check a piece of content for conflicts with existing world settings.

        Args:
            db: Database session
            world_id: World ID
            content: The content to check
            check_types: List of check types to run

        Returns:
            Dict with risk_level, conflicts, analysis, suggestions
        """
        if check_types is None:
            check_types = ["rule", "event", "character", "faction", "timeline"]

        conflicts = []
        suggestions = []

        # Get world data
        rules = db.query(WorldRule).filter(WorldRule.world_id == world_id).all()
        events = db.query(HistoricalEvent).filter(
            HistoricalEvent.world_id == world_id,
            HistoricalEvent.is_canon == True,
        ).all()
        characters = db.query(Character).filter(Character.world_id == world_id).all()
        factions = db.query(Faction).filter(Faction.world_id == world_id).all()

        content_lower = content.lower()

        # 1. Rule conflicts
        if "rule" in check_types:
            for rule in rules:
                conflict = ConsistencyService._check_rule_conflict(content, content_lower, rule)
                if conflict:
                    conflicts.append(conflict)
                    suggestions.append(f"建议检查是否违反规则「{rule.name}」：{rule.constraints or rule.content[:80]}")

        # 2. Event conflicts
        if "event" in check_types:
            for event in events:
                conflict = ConsistencyService._check_event_conflict(content, content_lower, event)
                if conflict:
                    conflicts.append(conflict)
                    suggestions.append(f"建议核实与正史事件「{event.title}」的一致性")

        # 3. Character status conflicts
        if "character" in check_types:
            for char in characters:
                conflict = ConsistencyService._check_character_conflict(content, content_lower, char)
                if conflict:
                    conflicts.append(conflict)
                    suggestions.append(f"建议核实角色「{char.name}」的当前状态（{char.current_status}）")

        # 4. Faction relationship conflicts
        if "faction" in check_types:
            for faction in factions:
                conflict = ConsistencyService._check_faction_conflict(content, content_lower, faction)
                if conflict:
                    conflicts.append(conflict)
                    suggestions.append(f"建议核实势力「{faction.name}」的关系设定")

        # 5. Timeline order check (simple)
        if "timeline" in check_types and events:
            conflict = ConsistencyService._check_timeline_conflict(content, events)
            if conflict:
                conflicts.append(conflict)

        # Determine risk level
        risk_level = ConsistencyService._assess_risk(conflicts)

        # Build analysis
        analysis = ConsistencyService._build_analysis(conflicts, risk_level)

        return {
            "risk_level": risk_level,
            "conflicts": conflicts,
            "analysis": analysis,
            "suggestions": suggestions[:5],  # Max 5 suggestions
            "check_types_used": check_types,
        }

    @staticmethod
    def _check_rule_conflict(content: str, content_lower: str, rule: WorldRule) -> Optional[str]:
        """Check if content conflicts with a world rule."""
        rule_text = (rule.name + " " + rule.content + " " + rule.constraints).lower()

        # Check for negation keywords in rule
        negation_keywords = ["不能", "禁止", "无法", "不可", "不允许", "cannot", "must not", "impossible"]
        for kw in negation_keywords:
            if kw in rule_text:
                # Extract what is negated
                parts = rule_text.split(kw)
                if len(parts) > 1:
                    restricted = parts[1][:50].strip()
                    if restricted and restricted in content_lower:
                        return f"内容可能违反规则「{rule.name}」：规则禁止「{restricted}」"

        # Check if content directly contradicts rule keywords
        rule_keywords = _extract_keywords(rule.content)
        content_keywords = _extract_keywords(content)
        for rk in rule_keywords:
            for ck in content_keywords:
                if _is_opposite(rk, ck):
                    return f"内容关键词「{ck}」与规则「{rule.name}」中的「{rk}」可能存在矛盾"

        return None

    @staticmethod
    def _check_event_conflict(content: str, content_lower: str, event: HistoricalEvent) -> Optional[str]:
        """Check if content conflicts with a canon event."""
        event_text = (event.title + " " + event.content).lower()
        event_keywords = _extract_keywords(event_text)
        content_keywords = _extract_keywords(content_lower)

        for ek in event_keywords:
            for ck in content_keywords:
                if _is_opposite(ek, ck):
                    return f"内容关键词「{ck}」与正史事件「{event.title}」可能存在矛盾"

        # Check if content references event time incorrectly
        if event.event_time and event.event_time in content:
            if "之前" in content and event.event_time in content:
                return f"内容时间可能与正史事件「{event.title}」（{event.event_time}）存在时间线矛盾"

        return None

    @staticmethod
    def _check_character_conflict(content: str, content_lower: str, character: Character) -> Optional[str]:
        """Check if content conflicts with a character's status."""
        # Dead characters cannot act
        if character.current_status in ["死亡", "dead"]:
            if character.name in content:
                return f"角色「{character.name}」当前状态为「{character.current_status}」，但内容中涉及该角色"

        # Missing characters
        if character.current_status in ["失踪", "missing"]:
            if character.name in content and ("出现" in content or "参战" in content or "行动" in content):
                return f"角色「{character.name}」当前状态为「{character.current_status}」，但内容描述其活跃行动"

        # Sealed characters
        if character.current_status in ["封印", "sealed"]:
            if character.name in content and ("解除" not in content and "破封" not in content):
                return f"角色「{character.name}」当前状态为「{character.current_status}」，但内容中涉及该角色自由行动"

        return None

    @staticmethod
    def _check_faction_conflict(content: str, content_lower: str, faction: Faction) -> Optional[str]:
        """Check if content conflicts with faction relationships."""
        if faction.enemies and faction.enemies != "[]":
            # Check if content describes alliance with enemies
            alliance_keywords = ["结盟", "联合", "合作", "联手", "alliance", "ally", "cooperate"]
            for kw in alliance_keywords:
                if kw in content_lower and faction.name in content:
                    return f"内容描述「{faction.name}」的结盟行为，但该势力存在敌对关系，请核实"

        return None

    @staticmethod
    def _check_timeline_conflict(content: str, events: List[HistoricalEvent]) -> Optional[str]:
        """Simple timeline order check."""
        # Check if content mentions a time earlier than existing events
        import re
        time_pattern = re.findall(r'(\d{4}-\d{2}-\d{2})', content)
        if time_pattern:
            new_time = time_pattern[0]
            for event in events:
                if event.event_time and event.event_time > new_time:
                    return f"内容时间「{new_time}」早于正史事件「{event.title}」（{event.event_time}），可能存在时间线顺序异常"
        return None

    @staticmethod
    def _assess_risk(conflicts: List[str]) -> str:
        """Assess overall risk level."""
        if not conflicts:
            return "low"
        if len(conflicts) >= 3:
            return "high"
        return "medium"

    @staticmethod
    def _build_analysis(conflicts: List[str], risk_level: str) -> str:
        """Build a human-readable analysis text."""
        if not conflicts:
            return "未发现明显矛盾。当前设定与待检查内容基本一致。"

        lines = [f"共发现 {len(conflicts)} 处潜在矛盾："]
        for i, c in enumerate(conflicts, 1):
            lines.append(f"{i}. {c}")

        lines.append(f"\n综合风险等级：{risk_level}")
        return "\n".join(lines)


def _extract_keywords(text: str) -> List[str]:
    """Extract meaningful keywords from text."""
    # Simple extraction: split by common delimiters, filter short words
    import re
    words = re.findall(r'[\u4e00-\u9fff\w]+', text)
    return [w for w in words if len(w) >= 2][:20]


def _is_opposite(word1: str, word2: str) -> bool:
    """Check if two words are opposites (simple keyword pairs)."""
    opposites = [
        ("和平", "战争"), ("战争", "和平"),
        ("结盟", "敌对"), ("敌对", "结盟"),
        ("生存", "死亡"), ("死亡", "生存"),
        ("创造", "毁灭"), ("毁灭", "创造"),
        ("统一", "分裂"), ("分裂", "统一"),
        ("和平", "冲突"), ("冲突", "和平"),
        ("光明", "黑暗"), ("黑暗", "光明"),
        ("正义", "邪恶"), ("邪恶", "正义"),
        ("秩序", "混乱"), ("混乱", "秩序"),
    ]
    w1_lower = word1.lower()
    w2_lower = word2.lower()
    for a, b in opposites:
        if (a in w1_lower and b in w2_lower) or (b in w1_lower and a in w2_lower):
            return True
    return False
