"""
AI World Engine - Behavior Service
Rule-based character behavior reasonableness checks.
"""

from typing import Optional
from sqlalchemy.orm import Session, joinedload

from app.models import Character


class BehaviorService:
    """Service for checking character behavior reasonableness."""

    @staticmethod
    def check_character_behavior(
        db: Session,
        character_id: int,
        world_id: int,
        behavior: str,
        context: str = "",
    ) -> dict:
        """
        Check if a character's described behavior is reasonable.

        Args:
            db: Database session
            character_id: Character ID
            world_id: World ID (for cross-world validation)
            behavior: Description of the character's behavior
            context: Optional background context

        Returns:
            Dict with reasonableness, checks, analysis, suggestions
        """
        character = (
            db.query(Character)
            .options(joinedload(Character.faction))
            .filter(Character.id == character_id)
            .first()
        )

        if not character or character.world_id != world_id:
            return {
                "error": "角色不存在或不属于当前世界",
                "reasonableness": "unknown",
            }

        checks = []
        suggestions = []
        behavior_lower = behavior.lower()

        # 1. Personality match
        personality_result = BehaviorService.evaluate_personality_match(character, behavior_lower)
        checks.append(personality_result)
        if personality_result["level"] != "reasonable":
            suggestions.append(personality_result["suggestion"])

        # 2. Goal match
        goal_result = BehaviorService.evaluate_goal_match(character, behavior_lower)
        checks.append(goal_result)
        if goal_result["level"] != "reasonable":
            suggestions.append(goal_result["suggestion"])

        # 3. Ability match
        ability_result = BehaviorService.evaluate_ability_match(character, behavior_lower)
        checks.append(ability_result)
        if ability_result["level"] != "reasonable":
            suggestions.append(ability_result["suggestion"])

        # 4. Status match
        status_result = BehaviorService.evaluate_status_match(character, behavior_lower)
        checks.append(status_result)
        if status_result["level"] != "reasonable":
            suggestions.append(status_result["suggestion"])

        # 5. Faction alignment
        if character.faction:
            faction_result = BehaviorService._check_faction_alignment(character, behavior_lower)
            checks.append(faction_result)
            if faction_result["level"] != "reasonable":
                suggestions.append(faction_result["suggestion"])

        # Determine overall reasonableness
        overall = BehaviorService._determine_overall(checks)

        # Build analysis
        analysis = BehaviorService._build_behavior_analysis(character, checks, overall)

        return {
            "reasonableness": overall,
            "character_name": character.name,
            "checks": checks,
            "analysis": analysis,
            "suggestions": suggestions[:5],
        }

    @staticmethod
    def evaluate_personality_match(character: Character, behavior_lower: str) -> dict:
        """Check if behavior matches character personality."""
        if not character.personality:
            return {"dimension": "性格匹配", "level": "reasonable",
                    "detail": "未设定性格，无法评估"}

        personality_lower = character.personality.lower()

        # Personality-behavior keyword pairs
        personality_checks = [
            (["谨慎", "cautious", "小心"], ["鲁莽", "冲动", "独自冲入", "无计划", "reckless"]),
            (["勇敢", "brave", "无畏"], ["逃跑", "退缩", "畏惧", "flee", "retreat"]),
            (["善良", "kind", "仁慈"], ["屠杀", "虐待", "残忍", "slaughter", "cruel"]),
            (["邪恶", "evil", "残忍"], ["救助", "牺牲自己", "无私奉献", "sacrifice"]),
            (["智慧", "wise", "聪明"], ["愚蠢", "鲁莽决定", "foolish"]),
            (["忠诚", "loyal"], ["背叛", "出卖", "betray"]),
            (["自私", "selfish"], ["无私奉献", "舍己为人"]),
            (["冷静", "calm"], ["暴怒", "失控", "rage"]),
        ]

        for pos_traits, neg_behaviors in personality_checks:
            has_trait = any(t in personality_lower for t in pos_traits)
            has_conflict = any(b in behavior_lower for b in neg_behaviors)
            if has_trait and has_conflict:
                return {
                    "dimension": "性格匹配",
                    "level": "questionable",
                    "detail": f"角色性格偏「{pos_traits[0]}」，但行为表现出相反倾向",
                    "suggestion": f"建议考虑角色性格中的「{pos_traits[0]}」特质是否允许此行为",
                }

        return {"dimension": "性格匹配", "level": "reasonable",
                "detail": "行为与已设定性格无明显冲突"}

    @staticmethod
    def evaluate_goal_match(character: Character, behavior_lower: str) -> dict:
        """Check if behavior aligns with character goal."""
        if not character.goal:
            return {"dimension": "目标匹配", "level": "reasonable",
                    "detail": "未设定目标，无法评估"}

        goal_lower = character.goal.lower()

        # Goal-behavior conflict keywords
        goal_conflicts = [
            (["保护", "protect", "守卫"], ["破坏", "摧毁", "出卖", "destroy", "betray"]),
            (["复仇", "revenge"], ["原谅", "和解", "forgive", "reconcile"]),
            (["统治", "rule", "征服"], ["放弃权力", "退位", "abdicate"]),
            (["和平", "peace"], ["发动战争", "挑起冲突", "war"]),
            (["财富", "wealth", "宝藏"], ["散尽家财", "放弃财产"]),
            (["力量", "power", "变强"], ["放弃修炼", "自废武功"]),
        ]

        for goal_kw, conflict_kw in goal_conflicts:
            has_goal = any(g in goal_lower for g in goal_kw)
            has_conflict = any(c in behavior_lower for c in conflict_kw)
            if has_goal and has_conflict:
                return {
                    "dimension": "目标匹配",
                    "level": "unreasonable",
                    "detail": f"角色目标涉及「{goal_kw[0]}」，但行为与此目标明显冲突",
                    "suggestion": f"建议重新考虑此行为是否与角色目标「{character.goal[:50]}」一致",
                }

        return {"dimension": "目标匹配", "level": "reasonable",
                "detail": "行为与已设定目标无明显冲突"}

    @staticmethod
    def evaluate_ability_match(character: Character, behavior_lower: str) -> dict:
        """Check if behavior is within character's abilities."""
        if not character.abilities:
            return {"dimension": "能力匹配", "level": "reasonable",
                    "detail": "未设定能力，无法评估"}

        abilities_lower = character.abilities.lower()

        # High-power abilities that might be beyond scope
        high_power_actions = [
            ("复活", ["复活死者", "起死回生", "resurrect"]),
            ("传送", ["瞬间移动", "空间传送", "teleport"]),
            ("时间", ["时间停止", "回到过去", "time travel"]),
            ("毁灭世界", ["毁灭世界", "灭世", "destroy the world"]),
            ("创造生命", ["创造生命", "create life"]),
            ("飞行", ["飞行", "飞翔", "fly"]),
            ("隐身", ["隐身", "隐形", "invisible"]),
            ("读心", ["读心", "心灵感应", "telepathy"]),
        ]

        for ability_name, action_kw in high_power_actions:
            has_action = any(a in behavior_lower for a in action_kw)
            has_ability = ability_name in abilities_lower
            if has_action and not has_ability:
                return {
                    "dimension": "能力匹配",
                    "level": "questionable",
                    "detail": f"行为涉及「{ability_name}」相关能力，但角色能力设定中未包含",
                    "suggestion": f"建议确认角色是否具备「{ability_name}」能力，或修改行为描述",
                }

        return {"dimension": "能力匹配", "level": "reasonable",
                "detail": "行为在角色已设定能力范围内"}

    @staticmethod
    def evaluate_status_match(character: Character, behavior_lower: str) -> dict:
        """Check if behavior is consistent with character's current status."""
        status = character.current_status

        status_actions = {
            "死亡": (["行动", "说话", "战斗", "出现"], "unreasonable",
                     f"角色当前状态为「{status}」，不应有主动行为"),
            "dead": (["act", "speak", "fight", "appear"], "unreasonable",
                     f"角色当前状态为「{status}」，不应有主动行为"),
            "重伤": (["战斗", "长途跋涉", "全力"], "questionable",
                     f"角色当前状态为「{status}」，高强度行为可能不合理"),
            "昏迷": (["行动", "说话", "战斗", "思考"], "unreasonable",
                     f"角色当前状态为「{status}」，无法进行有意识行为"),
            "封印": (["自由行动", "离开", "逃脱"], "unreasonable",
                     f"角色当前状态为「{status}」，无法自由行动"),
            "失踪": (["公开露面", "领导", "指挥"], "questionable",
                     f"角色当前状态为「{status}」，公开行为可能不合理"),
        }

        for st, (actions, level, detail) in status_actions.items():
            if status and st in status:
                for action in actions:
                    if action in behavior_lower:
                        return {
                            "dimension": "状态匹配",
                            "level": level,
                            "detail": detail,
                            "suggestion": f"建议先更新角色「{character.name}」的状态，或调整行为描述",
                        }

        return {"dimension": "状态匹配", "level": "reasonable",
                "detail": f"行为与当前状态「{status}」无明显冲突"}

    @staticmethod
    def _check_faction_alignment(character: Character, behavior_lower: str) -> dict:
        """Check if behavior aligns with faction stance."""
        faction = character.faction
        if not faction:
            return {"dimension": "势力立场", "level": "reasonable", "detail": "无势力归属"}

        faction_name = faction.name
        betrayal_kw = ["背叛", "出卖", "投敌", "betray"]
        for kw in betrayal_kw:
            if kw in behavior_lower and faction_name in behavior_lower:
                return {
                    "dimension": "势力立场",
                    "level": "questionable",
                    "detail": f"行为涉及背叛所属势力「{faction_name}」",
                    "suggestion": f"建议考虑角色与势力「{faction_name}」的关系是否允许此行为",
                }

        return {"dimension": "势力立场", "level": "reasonable",
                "detail": f"行为与所属势力「{faction_name}」无明显冲突"}

    @staticmethod
    def _determine_overall(checks: list) -> str:
        """Determine overall reasonableness from individual checks."""
        levels = [c["level"] for c in checks if "level" in c]
        if "unreasonable" in levels:
            return "unreasonable"
        if "questionable" in levels:
            return "questionable"
        return "reasonable"

    @staticmethod
    def _build_behavior_analysis(character: Character, checks: list, overall: str) -> str:
        """Build human-readable analysis text."""
        lines = [f"角色「{character.name}」行为合理性分析：\n"]

        for check in checks:
            if "dimension" in check:
                icon = {"reasonable": "✅", "questionable": "⚠️", "unreasonable": "❌"}.get(check["level"], "❓")
                lines.append(f"{icon} {check['dimension']}：{check.get('detail', '')}")

        level_text = {"reasonable": "合理", "questionable": "存疑", "unreasonable": "不合理"}
        lines.append(f"\n综合评估：{level_text.get(overall, overall)}")
        return "\n".join(lines)
