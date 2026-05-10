"""
AI World Engine - Model Router.
Determines which AI client to use based on task type and DB settings.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.services.ai.base import AIClient
from app.services.ai.mock_client import MockAIClient
from app.services.ai.openai_compatible_client import OpenAICompatibleClient
from app.services.settings_service import SettingsService


# Task type -> settings key for per-task model override
TASK_MODEL_KEYS = {
    "simulation": "ai_simulation_model",
    "novel_evolution": "ai_simulation_model",
    "conflict_check": "ai_check_model",
    "behavior_check": "ai_check_model",
    "summary": "ai_summary_model",
    "connection_test": "ai_model",
}


class ModelRouter:
    """Routes requests to the appropriate AI client based on configuration."""

    @staticmethod
    def get_client(db: Session, task_type: str = "simulation") -> AIClient:
        """
        Return an AIClient instance for the given task.
        Falls back to MockAIClient if live AI is not configured.

        Args:
            db: Database session
            task_type: One of simulation, conflict_check, behavior_check, summary, connection_test

        Returns:
            An AIClient (either MockAIClient or OpenAICompatibleClient)
        """
        config = SettingsService.get_effective_config(db)

        # If live AI is disabled or provider is mock, always use mock
        if not config["ai_enable_live"] or config["ai_provider"] == "mock":
            return MockAIClient()

        # If provider is openai_compatible, check that all required fields are present
        if config["ai_provider"] == "openai_compatible":
            if not (config["ai_api_key"] and config["ai_base_url"] and config["ai_model"]):
                return MockAIClient()
            # Determine which model to use for this task
            model = ModelRouter._resolve_model(config, task_type)
            return OpenAICompatibleClient(
                api_key=config["ai_api_key"],
                base_url=config["ai_base_url"],
                model=model,
                temperature=config["ai_temperature"],
                max_tokens=config["ai_max_tokens"],
                timeout=config["ai_timeout"],
            )

        # Unknown provider -> fallback to mock
        return MockAIClient()

    @staticmethod
    def _resolve_model(config: Dict[str, Any], task_type: str) -> str:
        """Resolve the model to use for a given task type."""
        override_key = TASK_MODEL_KEYS.get(task_type)
        if override_key:
            override_model = config.get(override_key, "").strip()
            if override_model:
                return override_model
        return config["ai_model"]

    @staticmethod
    def is_config_complete(db: Session) -> bool:
        """Check if the AI configuration is complete for live mode."""
        config = SettingsService.get_effective_config(db)
        if not config["ai_enable_live"] or config["ai_provider"] == "mock":
            return True
        if config["ai_provider"] == "openai_compatible":
            return bool(config["ai_api_key"] and config["ai_base_url"] and config["ai_model"])
        return False

    @staticmethod
    def config_hint(db: Session) -> str:
        """Return a human-readable hint about the current AI configuration."""
        config = SettingsService.get_effective_config(db)
        if not config["ai_enable_live"]:
            return "当前未启用真实 AI，使用 Mock 模式。"
        if config["ai_provider"] == "mock":
            return "当前使用 Mock AI 模式。"
        if config["ai_provider"] == "openai_compatible":
            missing = []
            if not config["ai_api_key"]:
                missing.append("API Key")
            if not config["ai_base_url"]:
                missing.append("Base URL")
            if not config["ai_model"]:
                missing.append("Model")
            if missing:
                return f"当前 AI 配置不完整，缺少: {', '.join(missing)}，已使用 Mock AI。"
            return f"当前使用 OpenAI-compatible 模型: {config['ai_model']}"
        return "未知 AI 提供商，已使用 Mock AI。"
