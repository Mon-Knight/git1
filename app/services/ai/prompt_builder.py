"""
AI World Engine - Prompt Builder.
Centralized construction of all AI prompts used in simulation and checks.
Keeping prompts out of routes makes them testable and maintainable.
"""

from typing import Dict, List


class PromptBuilder:
    """Builds structured prompts for AI tasks."""

    SIMULATION_SYSTEM = """你是小说世界观推演助手。
你需要基于已有世界设定进行合理推演。
不要直接推翻已有正史。
不要生成与已有世界规则明显冲突的内容。
如果存在不确定性，要说明假设。

输出应包含：
1. 推演摘要
2. 关键事件
3. 涉及角色
4. 涉及势力
5. 影响范围
6. 潜在矛盾
7. 是否建议采纳为正史"""

    CHECK_SYSTEM = """你是小说世界观一致性检查助手。
你需要根据已有角色、势力、地点、规则、正史事件检查潜在矛盾。
不要修改数据库。
不要直接替用户决定正史。

输出应包含：
1. 问题列表
2. 严重程度
3. 涉及设定
4. 原因
5. 修改建议"""

    @staticmethod
    def build_simulation_prompt(world_context: dict, user_question: str) -> List[Dict[str, str]]:
        """Build a simulation prompt pair (system + user)."""
        parts = []
        parts.append(f"【世界名称】{world_context.get('world_name', '未知')}")
        wc_type = world_context.get("world_type")
        if wc_type:
            parts.append(f"【世界类型】{wc_type}")
        current_era = world_context.get("current_era")
        if current_era:
            parts.append(f"【当前时代】{current_era}")
        tone = world_context.get("tone")
        if tone:
            parts.append(f"【世界基调】{tone}")
        desc = world_context.get("description")
        if desc:
            parts.append(f"【世界简介】{desc[:200]}")

        characters = world_context.get("characters", [])
        if characters:
            parts.append("\n【角色设定】")
            for c in characters[:10]:
                parts.append(f"- {c.get('name','?')}: 角色={c.get('role','?')}, 性格={c.get('personality','?')}, 目标={c.get('goal','?')}")

        factions = world_context.get("factions", [])
        if factions:
            parts.append("\n【势力设定】")
            for f in factions[:10]:
                parts.append(f"- {f.get('name','?')}: 类型={f.get('faction_type','?')}, 目标={f.get('goal','?')}")

        rules = world_context.get("rules", [])
        if rules:
            parts.append("\n【世界规则】")
            for r in rules[:10]:
                parts.append(f"- {r.get('name','?')}: {r.get('content','?')[:100]}")

        events = world_context.get("events", [])
        if events:
            parts.append("\n【近期正史事件】")
            for e in events[:10]:
                parts.append(f"- {e.get('title','?')}: {e.get('content','?')[:100]}")

        parts.append(f"\n【用户推演问题】{user_question}")
        parts.append("\n请基于以上设定，给出合理、连贯、符合世界逻辑的推演结果。")
        user_prompt = "\n".join(parts)

        return [
            {"role": "system", "content": PromptBuilder.SIMULATION_SYSTEM},
            {"role": "user", "content": user_prompt},
        ]

    @staticmethod
    def build_conflict_check_prompt(world_context: dict, rule_results: dict) -> List[Dict[str, str]]:
        """
        Build a prompt to get AI supplement analysis for a conflict check.
        rule_results is the output of ConsistencyService.check_setting_conflicts().
        """
        parts = ["请对以下设定矛盾检查结果进行补充分析。\n"]

        parts.append(f"【世界名称】{world_context.get('world_name', '未知')}")
        parts.append(f"【已知冲突数量】{len(rule_results.get('conflicts', []))}")
        parts.append(f"【风险等级】{rule_results.get('risk_level', '未知')}")
        parts.append(f"【规则式检查分析】{rule_results.get('analysis', '')[:300]}")

        rules = world_context.get("rules", [])
        if rules:
            parts.append("\n【世界规则摘要】")
            for r in rules[:5]:
                parts.append(f"- {r.get('name','?')}: {r.get('content','?')[:80]}")

        parts.append("\n请分析这些规则式检查结果是否遗漏了重要的矛盾风险，并给出你的补充分析和建议。")
        user_prompt = "\n".join(parts)

        return [
            {"role": "system", "content": PromptBuilder.CHECK_SYSTEM},
            {"role": "user", "content": user_prompt},
        ]

    @staticmethod
    def build_behavior_check_prompt(
        world_context: dict,
        character_info: dict,
        rule_results: dict,
    ) -> List[Dict[str, str]]:
        """Build a prompt for AI supplement analysis of a behavior check."""
        parts = ["请对以下角色行为合理性检查结果进行补充分析。\n"]

        parts.append(f"【角色名】{character_info.get('name', '未知')}")
        parts.append(f"【角色性格】{character_info.get('personality', '')[:200]}")
        parts.append(f"【角色目标】{character_info.get('goal', '')[:200]}")
        parts.append(f"【角色能力】{character_info.get('abilities', '')[:200]}")
        parts.append(f"【当前状态】{character_info.get('current_status', '')}")
        parts.append(f"【评估总结果】{rule_results.get('reasonableness', '未知')}")

        checks = rule_results.get("checks", [])
        if checks:
            parts.append("\n【逐项检查结果】")
            for c in checks:
                if c.get("dimension"):
                    parts.append(f"- {c['dimension']}: {c.get('level','')} — {c.get('detail','')}")

        parts.append(f"\n【分析说明】{rule_results.get('analysis', '')[:200]}")
        parts.append("\n请分析该角色行为合理性检查是否遗漏了重要维度，并给出补充分析和建议。")
        user_prompt = "\n".join(parts)

        return [
            {"role": "system", "content": PromptBuilder.CHECK_SYSTEM},
            {"role": "user", "content": user_prompt},
        ]

    @staticmethod
    def build_summary_prompt(world_context: dict) -> List[Dict[str, str]]:
        """Build a prompt asking the AI to summarize the current world state."""
        parts = ["请对以下世界观进行简要的结构化总结。\n"]

        parts.append(f"【世界名称】{world_context.get('world_name', '未知')}")
        parts.append(f"【世界类型】{world_context.get('world_type', '')}")
        parts.append(f"【当前时代】{world_context.get('current_era', '')}")
        parts.append(f"【世界基调】{world_context.get('tone', '')}")
        parts.append(f"【世界简介】{world_context.get('description', '')[:300]}")

        characters = world_context.get("characters", [])
        parts.append(f"\n【角色数量】{len(characters)}")
        factions = world_context.get("factions", [])
        parts.append(f"【势力数量】{len(factions)}")
        locations = world_context.get("locations", [])
        parts.append(f"【地点数量】{len(locations)}")
        rules = world_context.get("rules", [])
        parts.append(f"【规则数量】{len(rules)}")
        events = world_context.get("events", [])
        parts.append(f"【正史事件数量】{len(events)}")

        parts.append("\n请给出：1) 世界观总览 2) 核心冲突点 3) 主要势力关系 4) 关键角色 5) 潜在发展方向")
        user_prompt = "\n".join(parts)

        return [
            {"role": "system", "content": "你是小说世界观总结助手，请用结构化方式简洁总结用户提供的世界观。"},
            {"role": "user", "content": user_prompt},
        ]
