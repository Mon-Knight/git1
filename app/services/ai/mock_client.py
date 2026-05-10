"""
AI World Engine - Mock AI Client.
Used when no real AI API key is configured, or when testing.
Guaranteed to work without network.
"""

import random
from typing import Dict, Any, List, Optional

from app.services.ai.base import AIClient, success_response


class MockAIClient(AIClient):
    """A mock AI client that returns deterministic, rule-based results."""

    @property
    def provider(self) -> str:
        return "mock"

    @property
    def model_name(self) -> str:
        return "mock"

    def generate(
        self,
        messages: List[Dict[str, str]],
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Return a mock AI response. Always succeeds."""
        # Extract user message for context
        user_text = ""
        for m in messages:
            if m.get("role") == "user":
                user_text = m.get("content", "")
                break

        content = self._build_mock_output(user_text)
        usage = {
            "prompt_tokens": len(user_text) // 4,
            "completion_tokens": len(content) // 4,
            "total_tokens": (len(user_text) + len(content)) // 4,
        }
        return success_response(
            content=content,
            raw={"mock": True, "messages": messages},
            model="mock",
            provider="mock",
            usage=usage,
        )

    def test_connection(self) -> Dict[str, Any]:
        """Mock connection test always succeeds."""
        return {
            "success": True,
            "message": "Mock AI 可用",
            "provider": "mock",
            "model": "mock",
        }

    def _build_mock_output(self, user_text: str) -> str:
        """Build a deterministic mock output from user input."""
        parts = ["【Mock AI 推演结果】\n"]

        # Try to extract world context keywords
        if "世界名" in user_text or "世界设定" in user_text:
            parts.append("基于当前世界设定进行分析：")
        parts.append("")

        parts.append("=== 推演分析 ===")
        parts.append(f"输入长度: {len(user_text)} 字")

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

        parts.append("\n=== 建议 ===")
        parts.append("继续观察局势发展，结合实际设定进行更细致的推演。")
        parts.append("")
        parts.append("[注意: 此为 Mock AI 生成结果，仅供参考。配置 AI 设置后可获得真实 AI 推演。]")

        return "\n".join(parts)
