"""
AI World Engine - Novel Evolution Service
Builds structured prompts for full-novel evolution using context packages.
"""

import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.config import settings


class NovelEvolutionService:
    """Service for building novel-evolution prompts and saving results."""

    EVOLUTION_SYSTEM_PROMPT = """你是长篇小说全书演化规划助手。
你需要基于已有世界观、角色、势力、地点、规则、正史事件、用户提供的创作上下文包，推演一部长篇小说的全书演化方案。
你不能直接推翻已有正史。
你不能让主角无代价获得胜利。
你不能忽视已有世界规则。
如果用户给出的设定与现有世界矛盾，需要明确指出。
你输出的是"全书演化方案"，不是正文，不是章节正文。
你可以给出阶段结构建议，但不要展开到具体章节正文。
你必须保留用户最终审核权，不要直接替用户决定正史。

输出格式必须严格遵守以下12个章节（每个章节用"## 章节标题"标记）：

## 一、小说定位
- 题材方向
- 故事基调
- 读者预期
- 核心卖点

## 二、全书核心矛盾
- 表层矛盾
- 深层矛盾
- 世界级矛盾
- 主角个人矛盾

## 三、主角成长路线
- 初始状态
- 早期目标
- 中期转折
- 后期蜕变
- 最终状态

## 四、特殊能力影响路线
- 能力早期影响
- 能力中期暴露风险
- 能力后期改变世界的方式
- 能力限制与代价
- 禁止无代价升级

## 五、世界演化路线
- 世界原本运行方式
- 主角介入后的变化
- 势力格局变化
- 历史走向变化
- 最终世界状态候选

## 六、主要势力反应
- 支持者
- 观察者
- 利益竞争者
- 敌对者
- 隐藏威胁

## 七、主要人物关系变化
- 核心盟友
- 导师/引路人
- 对手
- 潜在背叛者
- 情感关系或羁绊

## 八、阶段结构建议
- 第一阶段
- 第二阶段
- 第三阶段
- 第四阶段
- 终局阶段
（注意：只做阶段结构，不做正式分卷大纲，不要生成具体章节列表）

## 九、关键转折事件
至少8个关键转折事件，每个事件包含：
- 事件名称
- 触发原因
- 参与角色/势力
- 对主角的影响
- 对世界的影响
- 是否适合作为正史候选

## 十、结局候选
- 稳健结局
- 高压结局
- 悲壮结局
- 开放式结局
- 推荐结局及理由

## 十一、设定风险与禁止越界项
- 可能破坏世界观的风险
- 可能导致主角过强的问题
- 可能导致配角降智的问题
- 不能提前暴露的秘密
- 不能自动改变的正史事实

## 十二、后续拆分建议
- 适合拆成几卷
- 下一步适合生成哪一阶段的分卷大纲
- 需要用户确认的问题"""

    @staticmethod
    def build_novel_evolution_context(
        db: Session, world_id: int, context_package_id: int
    ) -> Dict[str, Any]:
        """Build the full evolution context including world data and context package.

        Returns:
            Dict with world, context_package, and error keys.
        """
        from app.services.world_service import WorldService
        from app.services.world_context_service import WorldContextService
        from app.services.context_package_service import ContextPackageService

        world = WorldService.get_world(db, world_id)
        if not world:
            return {"error": "世界不存在", "world": None, "context_package": None}

        world_context = WorldContextService.build_world_context(db, world_id)

        result: Dict[str, Any] = {
            "world": world,
            "world_context": world_context,
            "context_package": None,
            "pkg_data": None,
            "error": None,
        }

        if context_package_id:
            pkg = ContextPackageService.get_context_package(db, context_package_id)
            if not pkg:
                return {**result, "error": "上下文包不存在"}
            if pkg.world_id != world_id:
                return {**result, "error": "上下文包不属于当前世界"}

            result["context_package"] = pkg
            result["pkg_data"] = ContextPackageService.build_context_for_generation(
                db, context_package_id
            )
            if "error" in result["pkg_data"]:
                result["pkg_data"] = None

        return result

    @staticmethod
    def build_novel_evolution_prompt(
        world_context: dict,
        pkg_data: Optional[Dict[str, Any]] = None,
        user_goal: str = "",
        options: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, str]]:
        """Build a novel evolution prompt with context package data.

        Args:
            world_context: Aggregated world setting context
            pkg_data: Context package data from build_context_for_generation
            user_goal: User's evolution goal
            options: Additional options (strict_canon, strict_style, etc.)

        Returns:
            List of message dicts for AI generation.
        """
        parts = []

        # World context section
        parts.append("## 世界基础信息")
        parts.append("- 世界名称：" + world_context.get("world_name", "未知"))
        wc_type = world_context.get("world_type")
        if wc_type:
            parts.append("- 世界类型：" + wc_type)
        current_era = world_context.get("current_era")
        if current_era:
            parts.append("- 当前时代：" + current_era)
        tone = world_context.get("tone")
        if tone:
            parts.append("- 世界基调：" + tone)
        desc = world_context.get("description")
        if desc:
            parts.append("- 世界简介：" + desc[:300])

        # Characters
        characters = world_context.get("characters", [])
        if characters:
            parts.append("\n## 角色设定")
            for c in characters[:15]:
                parts.append("- {}：角色={}，性格={}，目标={}".format(
                    c.get("name", "?"),
                    c.get("role", "?"),
                    c.get("personality", "?"),
                    c.get("goal", "?"),
                ))

        # Factions
        factions = world_context.get("factions", [])
        if factions:
            parts.append("\n## 势力设定")
            for f in factions[:10]:
                parts.append("- {}：类型={}，目标={}".format(
                    f.get("name", "?"),
                    f.get("faction_type", "?"),
                    f.get("goal", "?"),
                ))

        # Locations
        locations = world_context.get("locations", [])
        if locations:
            parts.append("\n## 地点设定")
            for loc in locations[:10]:
                parts.append("- {}：类型={}，区域={}".format(
                    loc.get("name", "?"),
                    loc.get("location_type", "?"),
                    loc.get("region", "?"),
                ))

        # Rules
        rules = world_context.get("rules", [])
        if rules:
            parts.append("\n## 世界规则")
            for r in rules[:10]:
                parts.append("- {}：{}".format(
                    r.get("name", "?"), r.get("content", "?")[:150]
                ))

        # Canon events
        events = world_context.get("canon_events", world_context.get("events", []))
        if events:
            parts.append("\n## 正史事件")
            for e in events[:10]:
                parts.append("- {}：{}".format(
                    e.get("title", "?"), e.get("content", "?")[:150]
                ))

        # Context package data
        if pkg_data:
            parts.append("\n\n## 创作上下文包信息")
            parts.append("- 上下文包名称：" + pkg_data.get("package_name", "未命名"))
            if pkg_data.get("generation_type"):
                parts.append("- 生成类型：" + pkg_data["generation_type"])
            if pkg_data.get("target_words"):
                parts.append("- 目标字数：" + pkg_data["target_words"])

            # Style profile
            style = pkg_data.get("style_profile_content")
            if style:
                parts.append("\n### 写作风格要求")
                parts.append("- 风格名称：" + style.get("name", ""))
                if style.get("genre"):
                    parts.append("- 题材：" + style["genre"])
                if style.get("narrative_pov"):
                    parts.append("- 叙事人称：" + style["narrative_pov"])
                if style.get("pacing"):
                    parts.append("- 节奏：" + style["pacing"])
                for key in [
                    "sentence_style", "dialogue_style", "conflict_style",
                    "character_style", "battle_style", "emotion_style",
                ]:
                    val = style.get(key)
                    if val:
                        parts.append("- {}：{}".format(
                            key.replace("_style", ""), val
                        ))
                if style.get("forbidden_patterns"):
                    parts.append("- 禁用写法：" + style["forbidden_patterns"])
                if style.get("extra_instructions"):
                    parts.append("- 补充风格要求：" + style["extra_instructions"])

            # Plot anchor
            anchor = pkg_data.get("plot_anchor_content")
            if anchor:
                parts.append("\n### 剧情时间点（当前故事进度）")
                parts.append("- 名称：" + anchor.get("name", ""))
                if anchor.get("stage"):
                    parts.append("- 所处阶段：" + anchor["stage"])
                if anchor.get("volume_name"):
                    parts.append("- 所属卷：" + anchor["volume_name"])
                if anchor.get("protagonist_age"):
                    parts.append("- 主角年龄：" + anchor["protagonist_age"])
                if anchor.get("current_location"):
                    parts.append("- 当前地点：" + anchor["current_location"])
                if anchor.get("occurred_events"):
                    parts.append("- 已发生事件：" + anchor["occurred_events"][:300])
                if anchor.get("hidden_secrets"):
                    parts.append("- 未公开秘密：" + anchor["hidden_secrets"][:300])
                if anchor.get("current_conflict"):
                    parts.append("- 当前核心矛盾：" + anchor["current_conflict"][:300])
                if anchor.get("character_states"):
                    parts.append("- 角色状态：" + anchor["character_states"][:200])
                if anchor.get("faction_states"):
                    parts.append("- 势力状态：" + anchor["faction_states"][:200])
                if anchor.get("current_goal"):
                    parts.append("- 当前目标：" + anchor["current_goal"])
                if anchor.get("next_goal"):
                    parts.append("- 下一步目标：" + anchor["next_goal"])
                if anchor.get("forbidden_events"):
                    parts.append("- 禁止提前发生：" + anchor["forbidden_events"])

            # Simulation record
            sim = pkg_data.get("simulation_record_content")
            if sim:
                parts.append("\n### 选中的推演记录")
                parts.append("- 推演类型：" + sim.get("simulation_type", ""))
                parts.append("- 状态：" + sim.get("status", ""))
                if sim.get("question"):
                    parts.append("- 推演问题：" + sim["question"][:300])
                if sim.get("ai_response"):
                    parts.append("- 推演结果摘要：" + sim["ai_response"][:800])

        # Constraints from context package
        if pkg_data:
            constraints = []
            if pkg_data.get("strict_canon"):
                constraints.append("- 严格遵守正史：生成内容必须与已有正史一致")
            if pkg_data.get("strict_style"):
                constraints.append("- 严格遵守写作风格：必须遵守上述风格要求")
            if pkg_data.get("extra_requirements"):
                constraints.append("- 补充要求：" + pkg_data["extra_requirements"])
            if constraints:
                parts.append("\n## 约束条件")
                parts.extend(constraints)

        # User goal
        parts.append("\n\n## 用户推演目标")
        parts.append(user_goal if user_goal.strip() else "基于当前世界设定，生成一条完整的全书演化路线。")

        # Output requirements
        parts.append("\n\n请基于以上所有信息，生成一份完整的全书演化方案。")
        parts.append("严格遵守12个章节的输出格式。")
        parts.append("不要生成正文。不要展开到具体章节。")
        parts.append("每个章节必须包含实质性内容，不要留空。")
        parts.append("如果缺少某些信息，基于现有设定合理推测并标注【推测】。")

        user_prompt = "\n".join(parts)

        return [
            {"role": "system", "content": NovelEvolutionService.EVOLUTION_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

    @staticmethod
    def build_context_snapshot(
        world_id: int,
        context_package_id: Optional[int] = None,
        pkg_data: Optional[Dict[str, Any]] = None,
        user_goal: str = "",
    ) -> str:
        """Build a JSON context_snapshot string for saving to simulation_records."""
        snapshot = {
            "app_version": settings.VERSION,
            "world_id": world_id,
            "context_package_id": context_package_id,
            "user_goal": user_goal,
        }

        if pkg_data:
            snapshot["generation_type"] = pkg_data.get("generation_type", "")
            snapshot["strict_canon"] = pkg_data.get("strict_canon", True)
            snapshot["strict_style"] = pkg_data.get("strict_style", True)
            snapshot["include_branches"] = pkg_data.get("include_branches", False)
            snapshot["include_non_canon"] = pkg_data.get("include_non_canon", False)
            snapshot["target_words"] = pkg_data.get("target_words", "")
            snapshot["package_name"] = pkg_data.get("package_name", "")

            # Record referenced IDs
            if pkg_data.get("simulation_record_content"):
                rec = pkg_data["simulation_record_content"]
                snapshot["selected_simulation_record_question"] = rec.get("question", "")[:200]
            if pkg_data.get("style_profile_content"):
                style = pkg_data["style_profile_content"]
                snapshot["style_profile_name"] = style.get("name", "")
            if pkg_data.get("plot_anchor_content"):
                anchor = pkg_data["plot_anchor_content"]
                snapshot["plot_anchor_name"] = anchor.get("name", "")

        return json.dumps(snapshot, ensure_ascii=False, indent=2)

    @staticmethod
    def save_novel_evolution_record(
        db: Session,
        world_id: int,
        question: str,
        ai_response: str,
        context_snapshot: str,
        ai_model: str = "mock",
        is_mock: bool = True,
    ):
        """Save a novel evolution result as a simulation_record."""
        from app.services.simulation_service import SimulationService
        from app.constants import SIMULATION_TYPE_NOVEL_EVOLUTION

        return SimulationService.create_simulation_record(
            db=db,
            world_id=world_id,
            question=question,
            simulation_type=SIMULATION_TYPE_NOVEL_EVOLUTION,
            context_snapshot=context_snapshot,
            ai_response=ai_response,
            ai_model=ai_model,
            is_mock=is_mock,
        )

    @staticmethod
    def list_novel_evolution_records(db: Session, world_id: int) -> list:
        """List all novel_evolution records for a world."""
        from app.models import SimulationRecord
        return (
            db.query(SimulationRecord)
            .filter(SimulationRecord.world_id == world_id)
            .filter(SimulationRecord.simulation_type == "novel_evolution")
            .order_by(SimulationRecord.created_at.desc())
            .all()
        )

    @staticmethod
    def get_novel_evolution_record(db: Session, record_id: int):
        """Get a single novel_evolution record, ensuring it belongs to the given world."""
        from app.models import SimulationRecord
        return (
            db.query(SimulationRecord)
            .filter(SimulationRecord.id == record_id)
            .filter(SimulationRecord.simulation_type == "novel_evolution")
            .first()
        )

    @staticmethod
    def set_record_status(
        db: Session, record_id: int, new_status: str, world_id: int
    ) -> Optional[Dict[str, Any]]:
        """Set a novel_evolution record's status.
        Only operates on novel_evolution records in the given world.
        """
        from app.models import SimulationRecord

        record = (
            db.query(SimulationRecord)
            .filter(SimulationRecord.id == record_id)
            .filter(SimulationRecord.world_id == world_id)
            .filter(SimulationRecord.simulation_type == "novel_evolution")
            .first()
        )
        if not record:
            return None

        record.status = new_status
        db.commit()
        db.refresh(record)

        return {
            "id": record.id,
            "status": record.status,
            "question": record.question,
        }

    @staticmethod
    def get_status_label(status: str) -> str:
        """Return a human-readable label for a record status."""
        labels = {
            "pending": "待确认",
            "adopted": "主线方案",
            "branched": "备选方案",
            "discarded": "已废弃",
        }
        return labels.get(status, status)

    @staticmethod
    def get_status_color(status: str) -> str:
        """Return a CSS color for a status badge."""
        colors = {
            "pending": "#f39c12",
            "adopted": "#27ae60",
            "branched": "#3498db",
            "discarded": "#95a5a6",
        }
        return colors.get(status, "#95a5a6")
