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
        # Detect novel evolution mode
        if "小说工程" in user_text or "全书演化方向" in user_text or "主角成长路线" in user_text:
            return self._build_novel_evolution_output(user_text)

        parts = ["【Mock AI 推演结果】\n"]

        if "世界名" in user_text or "世界设定" in user_text:
            parts.append("基于当前世界设定进行分析：")
        parts.append("")

        parts.append("=== 推演分析 ===")
        parts.append("输入长度: {} 字".format(len(user_text)))

        outcomes = [
            "局势逐渐明朗，各方势力开始重新评估自己的立场。",
            "一场意外的冲突打破了原有的平衡，新的联盟正在形成。",
            "暗流涌动之中，一个被忽视的细节可能改变整个格局。",
            "旧秩序的维护者与新力量的挑战者之间的张力持续增加。",
            "在表面的平静之下，关键人物正在做出影响深远的决定。",
        ]
        parts.append("\n推演结果: " + random.choice(outcomes))

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

    def _build_novel_evolution_output(self, user_text: str) -> str:
        """Build a mock novel evolution result with proper structure."""
        parts = [
            "【Mock AI - 小说工程推演结果】\n",
            "=== 1. 全书核心卖点 ===",
            "基于当前世界观的硬核设定，通过主角的独特视角展现世界法则与人性的冲突。"
            "融合穿越、学院成长、势力博弈等世界观元素，形成多层次叙事结构。\n",
            "=== 2. 主角成长路线 ===",
            "初期：利用特殊能力进行基础学习与生存适应，积累第一桶金和基本势力关系。",
            "中期：通过核心冲突推动主角深入世界法则核心，获得更高层次的能力与责任。",
            "后期：面对终极敌人和法则真相，主角必须付出重大代价才能突破最后的障碍。\n",
            "=== 3. 主线剧情方向 ===",
            "主线围绕主角如何在传统体系与新兴力量之间找到平衡推进。"
            "从个人成长需求出发，逐步卷入势力纷争和世界法则的秘密。\n",
            "=== 4. 世界局势演化 ===",
            "初期：表面平静但暗流涌动，旧势力维持秩序",
            "中期：矛盾激化，多股势力联盟与对抗并存",
            "后期：世界格局剧变，新秩序在废墟中建立\n",
            "=== 5. 主要势力变化 ===",
            "传统势力经历稳固-危机-分裂三阶段；新兴势力经历萌芽-扩张-整合三阶段；"
            "主角所属势力经历弱小-成长-关键一环三阶段。\n",
            "=== 6. 关键剧情阶段 ===",
            "第一阶段：入学与适应（约20%篇幅）",
            "第二阶段：能力显现与初次冲突（约25%篇幅）",
            "第三阶段：势力扩张与阴谋浮现（约25%篇幅）",
            "第四阶段：真相揭示与阵营分裂（约15%篇幅）",
            "第五阶段：最终决战与世界重塑（约15%篇幅）\n",
            "=== 7. 粗略分卷建议 ===",
            "第1卷：新生（约20万字）—— 主角入学，能力初现",
            "第2卷：成长（约20万字）—— 能力提升，初步卷入势力纷争",
            "第3卷：风暴（约20万字）—— 势力冲突全面爆发",
            "第4卷：真相（约15万字）—— 世界法则真相浮出水面",
            "第5卷：终局（约15万字）—— 最终决战与世界重塑\n",
            "=== 8. 重大转折点 ===",
            "转折1：主角发现特殊能力与世界法则的深层联系（第1卷末尾）",
            "转折2：传统势力对新兴力量的全面打压（第2卷中段）",
            "转折3：世界法则真相揭示——并非自然法则，而是远古文明的遗留实验（第4卷）",
            "转折4：主角必须在拯救世界和保全个人之间做出牺牲（第5卷）\n",
            "=== 9. 主要反派或阻力来源 ===",
            "初级阻力：学院内部的传统势力维护者",
            "中级阻力：世界法则的保守派守护者",
            "高级阻力：法则本身的非人逻辑——远古文明的规则引擎\n",
            "=== 10. 主角特殊能力的使用边界 ===",
            "能力具有明确代价：每次深度使用会消耗主角的某种不可再生资源。"
            "能力有学习曲线，早期只能做低级应用，高级应用需要理解世界法则本质。"
            "能力受世界法则排斥，滥用会导致法则崩溃，引发更大的灾难。\n",
            "=== 11. 与现有设定的潜在矛盾 ===",
            "[Mock模式] 尚未检测到明显矛盾。请在真实AI模式下进行深度矛盾分析。\n",
            "=== 12. 建议采纳为正史的内容 ===",
            "主角的入学与能力初现，可作为正史序章记录。\n",
            "=== 13. 适合保存为分支的内容 ===",
            "不同路线选择（如主角选择魔法学院vs骑士团）可作为分支保存。\n",
            "=== 14. 后续可继续推演的问题 ===",
            "1. 主角入学后第一年的具体经历是什么？",
            "2. 传统势力如何在暗中组织反击？",
            "3. 世界法则真相揭示后各方势力如何反应？",
            "",
            "[注意：此为 Mock AI 生成结果，仅供参考。配置真实 AI 后可获得更详细的长篇小说推演。]",
        ]
        return "\n".join(parts)
