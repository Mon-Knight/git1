"""
AI World Engine - AI Service
Handles AI-powered world simulation with real API and mock modes.
"""

import json
import random
from typing import Optional

from app.config import settings


class AIService:
    """Service for AI-powered world simulation."""

    def __init__(self):
        self.api_key = settings.AI_API_KEY
        self.base_url = settings.AI_BASE_URL
        self.model = settings.AI_MODEL

    @property
    def is_mock(self) -> bool:
        """Check if running in mock mode."""
        return settings.is_mock_ai

    def generate_simulation(
        self,
        world_context: dict,
        question: str,
    ) -> str:
        """
        Generate a simulation result based on world context and user question.

        Args:
            world_context: Dict containing world settings (characters, factions, etc.)
            question: The user's simulation question

        Returns:
            A string containing the AI-generated simulation result.
        """
        if self.is_mock:
            return self._mock_simulation(world_context, question)
        else:
            return self._call_real_api(world_context, question)

    def _mock_simulation(self, world_context: dict, question: str) -> str:
        """
        Generate a mock simulation result using rule-based logic.
        Used when no AI API key is configured.
        """
        world_name = world_context.get("world_name", "未知世界")
        characters = world_context.get("characters", [])
        factions = world_context.get("factions", [])

        # Build a simple rule-based response
        parts = [f"【Mock AI 推演结果】\n"]
        parts.append(f"世界: {world_name}")
        parts.append(f"推演问题: {question}\n")

        parts.append("=== 推演分析 ===")

        # Reference characters if available
        if characters:
            char_names = [c.get("name", "未知角色") for c in characters[:3]]
            parts.append(f"涉及角色: {', '.join(char_names)}")

        # Reference factions if available
        if factions:
            faction_names = [f.get("name", "未知势力") for f in factions[:3]]
            parts.append(f"涉及势力: {', '.join(faction_names)}")

        # Generate a plausible outcome
        outcomes = [
            "局势逐渐明朗，各方势力开始重新评估自己的立场。",
            "一场意外的冲突打破了原有的平衡，新的联盟正在形成。",
            "暗流涌动之中，一个被忽视的细节可能改变整个格局。",
            "旧秩序的维护者与新力量的挑战者之间的张力持续增加。",
            "在表面的平静之下，关键人物正在做出影响深远的决定。",
        ]
        parts.append(f"\n推演结果: {random.choice(outcomes)}")

        parts.append("\n=== 可能影响 ===")
        impacts = [
            "1. 势力关系可能发生微妙变化",
            "2. 部分角色的目标需要重新审视",
            "3. 世界规则面临新的考验",
            "4. 新的历史节点正在形成",
        ]
        parts.extend(random.sample(impacts, k=2))

        parts.append(f"\n[注意: 此为 Mock AI 生成结果，仅供参考。配置 AI_API_KEY 后可获得真实 AI 推演。]")

        return "\n".join(parts)

    def _call_real_api(self, world_context: dict, question: str) -> str:
        """
        Call the real AI API for simulation.
        Uses OpenAI-compatible API format.
        """
        import requests

        world_name = world_context.get("world_name", "未知世界")

        prompt = self._build_prompt(world_context, question)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": f"你是一个小说世界观推演AI，负责根据已有设定推演世界发展。当前世界: {world_name}"
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.8,
            "max_tokens": 2000,
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            return f"[AI 调用失败: {str(e)}]\n请检查 AI_API_KEY 和 AI_BASE_URL 配置。"

    def _build_prompt(self, world_context: dict, question: str) -> str:
        """Build a structured prompt for the AI."""
        parts = ["请根据以下世界设定，推演回答用户的问题。\n"]

        parts.append(f"【世界名称】{world_context.get('world_name', '未知')}")
        parts.append(f"【世界类型】{world_context.get('world_type', '未知')}")
        parts.append(f"【当前时代】{world_context.get('current_era', '未知')}")
        parts.append(f"【世界基调】{world_context.get('tone', '未知')}")

        if world_context.get("description"):
            parts.append(f"【世界简介】{world_context['description']}")

        characters = world_context.get("characters", [])
        if characters:
            parts.append("\n【角色设定】")
            for c in characters:
                parts.append(f"- {c.get('name', '?')}: {c.get('role', '?')}, 性格: {c.get('personality', '?')}")

        factions = world_context.get("factions", [])
        if factions:
            parts.append("\n【势力设定】")
            for f in factions:
                parts.append(f"- {f.get('name', '?')}: {f.get('faction_type', '?')}, 目标: {f.get('goal', '?')}")

        rules = world_context.get("rules", [])
        if rules:
            parts.append("\n【世界规则】")
            for r in rules:
                parts.append(f"- {r.get('name', '?')}: {r.get('content', '?')}")

        events = world_context.get("events", [])
        if events:
            parts.append("\n【近期历史事件】")
            for e in events:
                parts.append(f"- {e.get('title', '?')}: {e.get('content', '?')}")

        parts.append(f"\n【用户问题】{question}")
        parts.append("\n请基于以上设定，给出合理、连贯、符合世界逻辑的推演结果。")

        return "\n".join(parts)


# Singleton instance
ai_service = AIService()
