"""
AI World Engine - Check Service
Orchestrates setting consistency and behavior checks.
"""

from typing import Optional
from sqlalchemy.orm import Session

from app.services.consistency_service import ConsistencyService
from app.services.behavior_service import BehaviorService


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
        Always runs rule-based check first.
        Optionally adds AI supplement analysis.
        Returns a dict with results suitable for template rendering.
        """
        # Run rule-based check (always runs, never fails)
        result = ConsistencyService.check_setting_conflicts(
            db, world_id, content, check_types
        )

        # Optionally enhance with AI analysis
        if use_ai:
            try:
                from app.services.world_context_service import WorldContextService
                from app.services.ai.model_router import ModelRouter
                from app.services.ai.prompt_builder import PromptBuilder
                from app.services.settings_service import SettingsService

                world_context = WorldContextService.build_world_context(db, world_id)
                client = ModelRouter.get_client(db, "conflict_check")
                messages = PromptBuilder.build_conflict_check_prompt(world_context, result)
                config = SettingsService.get_effective_config(db)
                options = {
                    "temperature": config.get("ai_temperature", 0.7),
                    "max_tokens": config.get("ai_max_tokens", 2000),
                    "timeout": config.get("ai_timeout", 60),
                }
                ai_result = client.generate(messages, options)
                if ai_result.get("success"):
                    result["ai_analysis"] = ai_result["content"]
                    result["ai_used"] = True
                else:
                    err = ai_result.get("error", {})
                    result["ai_analysis"] = f"AI 辅助分析失败: {err.get('message', '未知错误')}"
                    result["ai_used"] = False
            except Exception as e:
                result["ai_analysis"] = f"AI 辅助分析暂时不可用: {str(e)}"
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
        Always runs rule-based check first.
        Optionally adds AI supplement analysis.
        """
        result = BehaviorService.check_character_behavior(
            db, character_id, world_id, behavior, context
        )

        if "error" in result:
            return result

        # Optionally enhance with AI analysis
        if use_ai:
            try:
                from app.services.world_context_service import WorldContextService
                from app.services.character_service import CharacterService
                from app.services.ai.model_router import ModelRouter
                from app.services.ai.prompt_builder import PromptBuilder
                from app.services.settings_service import SettingsService

                world_context = WorldContextService.build_world_context(db, world_id)
                character = CharacterService.get_character(db, character_id)
                character_info = {
                    "name": character.name if character else "",
                    "personality": result.get("character_personality", ""),
                    "goal": result.get("character_goal", ""),
                    "abilities": result.get("character_abilities", ""),
                    "current_status": result.get("character_status", ""),
                }
                client = ModelRouter.get_client(db, "behavior_check")
                messages = PromptBuilder.build_behavior_check_prompt(
                    world_context, character_info, result
                )
                config = SettingsService.get_effective_config(db)
                options = {
                    "temperature": config.get("ai_temperature", 0.7),
                    "max_tokens": config.get("ai_max_tokens", 2000),
                    "timeout": config.get("ai_timeout", 60),
                }
                ai_result = client.generate(messages, options)
                if ai_result.get("success"):
                    result["ai_analysis"] = ai_result["content"]
                    result["ai_used"] = True
                else:
                    err = ai_result.get("error", {})
                    result["ai_analysis"] = f"AI 辅助分析失败: {err.get('message', '未知错误')}"
                    result["ai_used"] = False
            except Exception as e:
                result["ai_analysis"] = f"AI 辅助分析暂时不可用: {str(e)}"
                result["ai_used"] = False
        else:
            result["ai_used"] = False

        return result
