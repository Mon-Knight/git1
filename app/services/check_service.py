"""
AI World Engine - Check Service
Orchestrates setting consistency and behavior checks.
"""

from typing import Optional
from sqlalchemy.orm import Session

from app.services.consistency_service import ConsistencyService
from app.services.behavior_service import BehaviorService
from app.services.ai_service import ai_service


class CheckService:
    """Service that orchestrates all check operations."""

    @staticmethod
    def run_conflict_check(
        db: Session,
        world_id: int,
        content: str,
        check_types: list = None,
        use_ai: bool = False,
    ) -> dict:
        """
        Run a setting conflict check.

        Returns a dict with results suitable for template rendering.
        """
        # Run rule-based check
        result = ConsistencyService.check_setting_conflicts(
            db, world_id, content, check_types
        )

        # Optionally enhance with AI analysis
        if use_ai:
            try:
                ai_context = {
                    "world_name": f"world_{world_id}",
                    "check_content": content,
                    "rule_based_result": result,
                }
                ai_analysis = ai_service.generate_simulation(
                    ai_context,
                    f"请分析以下设定的矛盾风险：{content[:200]}"
                )
                result["ai_analysis"] = ai_analysis
                result["ai_used"] = True
            except Exception:
                result["ai_analysis"] = "AI 辅助分析暂时不可用"
                result["ai_used"] = False
        else:
            result["ai_used"] = False

        return result

    @staticmethod
    def run_behavior_check(
        db: Session,
        world_id: int,
        character_id: int,
        behavior: str,
        context: str = "",
        use_ai: bool = False,
    ) -> dict:
        """
        Run a character behavior reasonableness check.

        Returns a dict with results suitable for template rendering.
        """
        result = BehaviorService.check_character_behavior(
            db, character_id, world_id, behavior, context
        )

        if "error" in result:
            return result

        # Optionally enhance with AI analysis
        if use_ai:
            try:
                ai_context = {
                    "character_name": result.get("character_name", ""),
                    "behavior": behavior,
                    "context": context,
                    "rule_based_result": result,
                }
                ai_analysis = ai_service.generate_simulation(
                    ai_context,
                    f"请分析角色行为的合理性：{behavior[:200]}"
                )
                result["ai_analysis"] = ai_analysis
                result["ai_used"] = True
            except Exception:
                result["ai_analysis"] = "AI 辅助分析暂时不可用"
                result["ai_used"] = False
        else:
            result["ai_used"] = False

        return result
