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
        # Detect novel evolution mode (both old and new formats)
        if ("小说工程" in user_text or "全书演化" in user_text
                or "主角成长路线" in user_text or "小说定位" in user_text
                or "全书核心矛盾" in user_text):
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
        """Build a structured 12-section mock novel evolution result."""
        parts = [
            "【Mock AI - 全书演化方案】\n",
            "## 一、小说定位",
            "- 题材方向：基于世界设定的硬核奇幻，融合学院成长与势力博弈",
            "- 故事基调：理性克制、设定严谨、冲突推进强",
            "- 读者预期：喜欢逻辑严密世界观和主角成长路线的读者",
            "- 核心卖点：独特的主角能力与世界法则的深层互动关系\n",
            "## 二、全书核心矛盾",
            "- 表层矛盾：传统体系与新兴力量之间的对抗",
            "- 深层矛盾：世界法则的真相——是自然规律还是远古文明的遗留实验",
            "- 世界级矛盾：法则崩溃风险 vs 文明延续",
            "- 主角个人矛盾：使用能力改变世界 vs 能力本身加速法则崩溃\n",
            "## 三、主角成长路线",
            "- 初始状态：出身平凡但拥有特殊能力，对世界了解有限",
            "- 早期目标：掌握基本能力，在学院/组织中站稳脚跟",
            "- 中期转折：发现能力与世界法则的深层联系，卷入势力博弈",
            "- 后期蜕变：承担改变世界格局的责任，面临重大牺牲选择",
            "- 最终状态：成为世界新秩序的关键缔造者之一\n",
            "## 四、特殊能力影响路线",
            "- 能力早期影响：帮助主角快速学习和生存，获得初期优势",
            "- 能力中期暴露风险：引起各方势力关注，成为争夺/打压目标",
            "- 能力后期改变世界的方式：揭示世界法则本质，推动法则重构",
            "- 能力限制与代价：每次深度使用消耗不可再生资源，过度使用加速法则崩溃",
            "- 禁止无代价升级：能力提升必须伴随相应的风险和责任增长\n",
            "## 五、世界演化路线",
            "- 世界原本运行方式：传统势力维持稳定但僵化的秩序",
            "- 主角介入后的变化：新思想和技术冲击旧体系，触发连锁反应",
            "- 势力格局变化：从多极平衡 → 两极对抗 → 多极重组",
            "- 历史走向变化：原本走向缓慢衰落 → 主角介入后走向重构新生",
            "- 最终世界状态候选：新旧融合的平衡态 / 彻底重构的新纪元\n",
            "## 六、主要势力反应",
            "- 支持者：新兴势力、改革派、被压迫群体",
            "- 观察者：中立势力、情报组织、跨国商会",
            "- 利益竞争者：保守派中的务实力量、相邻势力",
            "- 敌对者：极端保守派、利益受损方、法则守护者",
            "- 隐藏威胁：法则本身的非人逻辑、远古文明的残留机制\n",
            "## 七、主要人物关系变化",
            "- 核心盟友：初期同伴 → 中期核心团队 → 后期理念分化/坚守",
            "- 导师/引路人：启蒙阶段指导 → 中期被超越/牺牲 → 后期精神遗产",
            "- 对手：初期竞争者 → 中期宿敌 → 后期共同面对终极威胁的临时同盟",
            "- 潜在背叛者：利益冲突导致的内部裂痕",
            "- 情感关系或羁绊：在动荡中不断被考验和重构\n",
            "## 八、阶段结构建议",
            "- 第一阶段：启蒙与立足（约20%篇幅）—— 能力初现，建立基本人际关系",
            "- 第二阶段：能力成长与初步冲突（约25%篇幅）—— 卷入势力博弈",
            "- 第三阶段：真相揭示与阵营分化（约25%篇幅）—— 世界法则真相浮出水面",
            "- 第四阶段：全面对抗与牺牲（约15%篇幅）—— 关键决战与重大牺牲",
            "- 终局阶段：世界重构与新秩序（约15%篇幅）—— 法则重构/世界新生\n",
            "## 九、关键转折事件",
            "- 事件1「初露锋芒」：主角能力首次在公开场合显现，引起各方注意",
            "  触发：危机情境下的自我保护本能  影响：成为关注焦点",
            "- 事件2「法则初探」：主角首次感知到世界法则的异常",
            "  触发：能力深度使用触及法则边界  影响：开启法则探索线",
            "- 事件3「势力选择」：主角被迫在多个势力间做出选择",
            "  触发：多方同时伸出橄榄枝/威胁  影响：确定主要盟友和敌人",
            "- 事件4「真相碎片」：获得世界法则真相的第一块关键碎片",
            "  触发：探索远古遗迹/接触法则守护者  影响：认知升级",
            "- 事件5「背叛时刻」：信任的人因利益背叛",
            "  触发：外部压力+内部裂痕  影响：性格成熟/策略转变",
            "- 事件6「法则危机」：法则崩溃的前兆首次显现",
            "  触发：主角或他人的能力滥用  影响：紧迫感爆发",
            "- 事件7「最终抉择」：主角必须在个人和世界之间做出选择",
            "  触发：终极威胁降临  影响：确定最终路线",
            "- 事件8「代价支付」：主角为改变世界付出的最大代价",
            "  触发：实施终极方案的必要条件  影响：角色弧光完成\n",
            "## 十、结局候选",
            "- 稳健结局：新旧融合，在法则框架内建立更灵活的秩序（推荐）",
            "- 高压结局：主角强制改变法则，带来短期和平但埋下隐患",
            "- 悲壮结局：主角牺牲自己完成法则重构，世界铭记其贡献",
            "- 开放式结局：法则真相揭示后，留下新问题让读者思考\n",
            "## 十一、设定风险与禁止越界项",
            "- 可能破坏世界观的风险：能力体系过度膨胀导致战力崩坏",
            "- 可能导致主角过强的问题：避免能力无上限增长，必须有明确天花板",
            "- 可能导致配角降智的问题：对手必须有合理动机，不能为反派而反派",
            "- 不能提前暴露的秘密：世界法则的完整真相应在后期逐步揭示",
            "- 不能自动改变的正史事实：已有正史事件不可被新生成内容篡改\n",
            "## 十二、后续拆分建议",
            "- 适合拆成：5-6卷",
            "- 下一步适合生成：第一阶段的详细分卷大纲",
            "- 需要用户确认的问题：主角性别/性格细节、叙事人称偏好、目标读者群",
            "",
            "[注意：此为 Mock AI 生成结果，仅供参考。配置真实 AI 后可获得更详细的全书演化方案。]",
        ]
        return "\n".join(parts)
