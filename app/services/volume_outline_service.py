"""
AI World Engine - Volume Outline Service
Builds prompts, generates volume outlines via AI, and manages CRUD.
"""
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models import NovelVolumeOutline, SimulationRecord
from app.config import settings


class VolumeOutlineService:
    """Service for volume outline generation and management."""

    VOLUME_SYSTEM_PROMPT = """你是长篇小说分卷大纲规划助手。
你需要基于已有的世界观设定、全书演化方案、创作资产（风格方案、剧情时间点、上下文包），
为一部长篇小说生成分卷大纲。

重要规则：
1. 你只生成分卷大纲候选，不生成章节大纲，不生成正文。
2. 你必须遵守已确认的正史（canon events），不能推翻已有设定。
3. 你必须尊重已采纳的角色、势力、地点、规则。
4. 你必须保证主角路线与全书演化方案一致。
5. 分卷数量必须符合用户要求。
6. 输出结果仅为候选方案，用户确认后才成为主线分卷方案。
7. 不得抄袭现成作品的专有名词，必须原创。
8. 可以参考题材结构，但内容必须独立创作。

输出格式：严格JSON，包含以下字段：
{
  "title": "分卷大纲方案标题",
  "summary": "全书分卷整体说明（100-200字）",
  "volume_count": N,
  "volumes": [
    {
      "volume_index": 1,
      "title": "第一卷标题",
      "core_theme": "本卷核心主题",
      "main_conflict": "本卷主要矛盾",
      "protagonist_goal": "主角阶段目标",
      "key_characters": ["角色名1", "角色名2"],
      "key_factions": ["势力名1"],
      "key_locations": ["地点名1"],
      "major_events": ["关键事件1", "关键事件2", "关键事件3"],
      "turning_point": "本卷转折点描述",
      "ending_hook": "本卷结尾钩子",
      "estimated_chapters": 40,
      "notes": "补充说明"
    }
  ]
}
每一卷都必须包含以上全部字段。"""

    @staticmethod
    def build_volume_outline_prompt(
        db: Session, world_id: int,
        source_evolution_id: Optional[int] = None,
        style_profile_id: Optional[int] = None,
        plot_anchor_id: Optional[int] = None,
        context_package_id: Optional[int] = None,
        volume_count: int = 5,
        extra_requirements: str = "",
    ) -> str:
        """Build a prompt for volume outline generation."""
        from app.models import World, Character, Faction, Location, WorldRule, HistoricalEvent
        from app.models import StyleProfile, PlotAnchor, ContextPackage

        world = db.query(World).filter_by(id=world_id).first()
        if not world:
            raise ValueError(f"World {world_id} not found")

        parts = []

        # World info
        parts.append(f"【世界信息】")
        parts.append(f"世界名称：{world.name}")
        parts.append(f"世界类型：{world.world_type or '未指定'}")
        parts.append(f"当前时代：{world.current_era or '未指定'}")
        parts.append(f"世界基调：{world.tone or '未指定'}")
        parts.append(f"世界简介：{world.description or '无'}")

        # Adopted characters (limit 15)
        chars = db.query(Character).filter_by(world_id=world_id).limit(15).all()
        if chars:
            parts.append(f"\n【已采纳角色】({len(chars)}人)")
            for c in chars:
                parts.append(f"- {c.name}（{c.role or '未知角色'}），状态：{c.current_status}，性格：{c.personality[:80] if c.personality else '无'}")

        # Adopted factions (limit 10)
        factions = db.query(Faction).filter_by(world_id=world_id).limit(10).all()
        if factions:
            parts.append(f"\n【已采纳势力】({len(factions)}个)")
            for f in factions:
                parts.append(f"- {f.name}（{f.faction_type or '未知类型'}），目标：{f.goal[:80] if f.goal else '无'}")

        # Adopted locations (limit 10)
        locs = db.query(Location).filter_by(world_id=world_id).limit(10).all()
        if locs:
            parts.append(f"\n【已采纳地点】({len(locs)}个)")
            for l in locs:
                parts.append(f"- {l.name}（{l.location_type or '未知类型'}）：{l.description[:80] if l.description else '无'}")

        # Adopted rules (limit 10)
        rules = db.query(WorldRule).filter_by(world_id=world_id).limit(10).all()
        if rules:
            parts.append(f"\n【已采纳规则】({len(rules)}条)")
            for r in rules:
                parts.append(f"- {r.name}（{r.rule_type or '通用'}）：{r.content[:100] if r.content else '无'}")

        # Canon events (limit 10)
        events = db.query(HistoricalEvent).filter_by(world_id=world_id, is_canon=True).limit(10).all()
        if events:
            parts.append(f"\n【正史事件】({len(events)}条)")
            for e in events:
                parts.append(f"- {e.event_time or '?'} | {e.title}：{e.content[:100] if e.content else '无'}")

        # Source evolution plan
        if source_evolution_id:
            evo = db.query(SimulationRecord).filter_by(id=source_evolution_id, world_id=world_id).first()
            if evo:
                parts.append(f"\n【来源全书演化方案】")
                parts.append(f"标题：{evo.question or '(无标题)'}")
                parts.append(f"内容摘要：{evo.ai_response[:1500] if evo.ai_response else '(空)'}")
        else:
            parts.append(f"\n【全书演化方案】未选择（将基于当前世界资料自由创作）")

        # Style profile
        if style_profile_id:
            sp = db.query(StyleProfile).filter_by(id=style_profile_id).first()
            if sp:
                parts.append(f"\n【写作风格方案】{sp.name}")
                parts.append(f"题材：{sp.genre or '未指定'}，叙事视角：{sp.narrative_pov or '未指定'}，节奏：{sp.pacing or '未指定'}")

        # Plot anchor
        if plot_anchor_id:
            pa = db.query(PlotAnchor).filter_by(id=plot_anchor_id, world_id=world_id).first()
            if pa:
                parts.append(f"\n【剧情时间点】{pa.name}（阶段：{pa.stage or '?'}，当前冲突：{pa.current_conflict[:100] if pa.current_conflict else '无'}）")

        # Context package
        if context_package_id:
            cp = db.query(ContextPackage).filter_by(id=context_package_id, world_id=world_id).first()
            if cp:
                parts.append(f"\n【创作上下文包】{cp.name}")
                parts.append(f"描述：{cp.description[:200] if cp.description else '无'}")

        # User requirements
        parts.append(f"\n【生成要求】")
        parts.append(f"分卷数量：{volume_count} 卷")
        if extra_requirements:
            parts.append(f"补充要求：{extra_requirements}")

        return "\n".join(parts)

    @staticmethod
    def generate_volume_outline(
        db: Session, world_id: int,
        source_evolution_id: Optional[int] = None,
        style_profile_id: Optional[int] = None,
        plot_anchor_id: Optional[int] = None,
        context_package_id: Optional[int] = None,
        volume_count: int = 5,
        extra_requirements: str = "",
    ) -> Dict[str, Any]:
        """Generate a volume outline using AI (or Mock)."""
        prompt = VolumeOutlineService.build_volume_outline_prompt(
            db, world_id, source_evolution_id, style_profile_id,
            plot_anchor_id, context_package_id, volume_count, extra_requirements
        )

        from app.services.ai.model_router import ModelRouter
        from app.services.settings_service import SettingsService

        is_mock = not SettingsService.is_live_enabled(db)
        if is_mock:
            result_json, raw_text = VolumeOutlineService._mock_generate(volume_count)
        else:
            try:
                client = ModelRouter.get_client(db, "novel_evolution")
                full_prompt = VolumeOutlineService.VOLUME_SYSTEM_PROMPT + "\n\n" + prompt
                response = client.generate(full_prompt)
                raw_text = response
                result_json = VolumeOutlineService.parse_response(raw_text)
            except Exception as e:
                raise RuntimeError(f"AI 调用失败: {str(e)}")

        return {
            "prompt": prompt,
            "result_json": json.dumps(result_json, ensure_ascii=False) if isinstance(result_json, dict) else result_json,
            "raw_text": raw_text or "",
            "volume_count": volume_count,
            "is_mock": is_mock,
        }

    @staticmethod
    def _mock_generate(volume_count: int = 3):
        """Generate a mock volume outline for testing."""
        vc = max(3, min(volume_count, 10))
        mock_templates = [
            {"title": "觉醒与入局", "theme": "主角从平凡到非凡的觉醒过程", "conflict": "外部威胁 vs 内部成长"},
            {"title": "试炼与联盟", "theme": "通过考验建立核心队伍", "conflict": "势力博弈与信任建立"},
            {"title": "危机与真相", "theme": "世界真相逐步揭露", "conflict": "旧秩序崩塌与新势力崛起"},
            {"title": "远征与发现", "theme": "离开舒适区探索未知领域", "conflict": "文化冲突与资源争夺"},
            {"title": "决战与新生", "theme": "最终对决与新时代开启", "conflict": "终极对抗与牺牲"},
            {"title": "暗流与背叛", "theme": "内部裂痕与隐藏敌人", "conflict": "信任危机与权力斗争"},
            {"title": "传承与超越", "theme": "超越前辈成就新的传奇", "conflict": "传统与创新的碰撞"},
            {"title": "混沌与秩序", "theme": "在混乱中重建秩序", "conflict": "多方势力混战"},
            {"title": "破局与反击", "theme": "从劣势中反击逆转", "conflict": "以弱胜强的战略博弈"},
            {"title": "归宿与启程", "theme": "阶段性结局与新冒险的开始", "conflict": "旧敌覆灭新敌出现"},
        ]
        volumes = []
        for i in range(min(vc, len(mock_templates))):
            t = mock_templates[i]
            volumes.append({
                "volume_index": i + 1,
                "title": f"第{i+1}卷：{t['title']}",
                "core_theme": t["theme"],
                "main_conflict": t["conflict"],
                "protagonist_goal": f"在第{i+1}卷中达成阶段性成长",
                "key_characters": ["主角", "导师", "盟友", "反派"],
                "key_factions": ["主角阵营", "敌对势力"],
                "key_locations": ["主城", "关键战场"],
                "major_events": [
                    f"卷首事件：触发本卷主线",
                    f"中间转折：局势发生变化",
                    f"卷末高潮：本卷核心冲突解决",
                ],
                "turning_point": f"第{i+1}卷的关键转折发生于主角做出重要抉择之时",
                "ending_hook": f"第{i+1}卷结尾揭示了一个更大的阴谋，为下一卷埋下伏笔",
                "estimated_chapters": 30 + i * 10,
                "notes": f"本卷为{i+1}卷结构中的第{i+1}部分，承上启下",
            })
        result = {
            "title": f"分卷大纲候选方案",
            "summary": f"全书共规划 {vc} 卷，从主角觉醒到最终对决，逐步展开世界观与主线剧情。",
            "volume_count": vc,
            "volumes": volumes,
        }
        return result, json.dumps(result, ensure_ascii=False, indent=2)

    @staticmethod
    def parse_response(raw_text: str) -> Any:
        """Parse AI response, trying JSON first, falling back to raw text."""
        try:
            # Try to extract JSON block
            json_match = re.search(r'\{[\s\S]*\}', raw_text)
            if json_match:
                return json.loads(json_match.group(0))
        except (json.JSONDecodeError, ValueError):
            pass
        return {"parse_error": True, "raw_text": raw_text, "message": "AI 返回格式非标准 JSON，已保存原始文本"}

    @staticmethod
    def save_volume_outline(
        db: Session, world_id: int,
        prompt: str, result_json: str, raw_text: str = "",
        volume_count: int = 0,
        source_evolution_id: Optional[int] = None,
        style_profile_id: Optional[int] = None,
        plot_anchor_id: Optional[int] = None,
        context_package_id: Optional[int] = None,
        generation_requirement: str = "",
    ) -> NovelVolumeOutline:
        """Save a generated volume outline."""
        outline = NovelVolumeOutline(
            world_id=world_id,
            title="",
            source_evolution_id=source_evolution_id,
            style_profile_id=style_profile_id,
            plot_anchor_id=plot_anchor_id,
            context_package_id=context_package_id,
            generation_requirement=generation_requirement,
            volume_count=volume_count,
            prompt=prompt,
            result_json=result_json,
            raw_text=raw_text,
            status="candidate",
            is_main=False,
        )
        # Extract title from result_json
        try:
            data = json.loads(result_json)
            outline.title = data.get("title", f"分卷大纲 #{outline.id or '?'}")
        except (json.JSONDecodeError, ValueError):
            outline.title = "分卷大纲方案"

        db.add(outline)
        db.commit()
        db.refresh(outline)
        return outline

    @staticmethod
    def list_volume_outlines(db: Session, world_id: int) -> List[NovelVolumeOutline]:
        """List all volume outlines for a world, newest first."""
        return db.query(NovelVolumeOutline).filter_by(world_id=world_id).order_by(
            NovelVolumeOutline.created_at.desc()
        ).all()

    @staticmethod
    def get_volume_outline(db: Session, world_id: int, outline_id: int) -> Optional[NovelVolumeOutline]:
        """Get a specific volume outline, verifying world ownership."""
        return db.query(NovelVolumeOutline).filter_by(
            id=outline_id, world_id=world_id
        ).first()

    @staticmethod
    def set_main_volume_outline(db: Session, world_id: int, outline_id: int) -> NovelVolumeOutline:
        """Set a volume outline as the main plan."""
        outline = VolumeOutlineService.get_volume_outline(db, world_id, outline_id)
        if not outline:
            raise ValueError("分卷大纲不存在")
        if outline.status == "discarded":
            raise ValueError("已废弃的分卷大纲不能设为主线")

        # Unset any existing main
        existing_main = db.query(NovelVolumeOutline).filter_by(
            world_id=world_id, is_main=True
        ).first()
        if existing_main:
            existing_main.is_main = False
            existing_main.status = "candidate"

        outline.is_main = True
        outline.status = "main"
        outline.confirmed_at = datetime.now(timezone.utc)
        db.commit()
        return outline

    @staticmethod
    def discard_volume_outline(db: Session, world_id: int, outline_id: int) -> NovelVolumeOutline:
        """Discard a volume outline."""
        outline = VolumeOutlineService.get_volume_outline(db, world_id, outline_id)
        if not outline:
            raise ValueError("分卷大纲不存在")
        if outline.status == "discarded":
            raise ValueError("该分卷大纲已被废弃")

        outline.status = "discarded"
        outline.is_main = False
        db.commit()
        return outline

    @staticmethod
    def update_volume_outline(
        db: Session, world_id: int, outline_id: int, edited_data: dict
    ) -> NovelVolumeOutline:
        """Update a volume outline's editable fields."""
        outline = VolumeOutlineService.get_volume_outline(db, world_id, outline_id)
        if not outline:
            raise ValueError("分卷大纲不存在")
        if outline.status == "discarded":
            raise ValueError("已废弃的分卷大纲不能编辑")

        # Update title
        if "title" in edited_data and edited_data["title"]:
            outline.title = edited_data["title"]

        # Update result_json with edited volume data
        try:
            data = json.loads(outline.result_json)
            if "title" in edited_data:
                data["title"] = edited_data["title"]
            if "summary" in edited_data:
                data["summary"] = edited_data["summary"]
            if "volumes" in edited_data:
                data["volumes"] = edited_data["volumes"]
            if "volume_titles" in edited_data:
                # Map simple title edits back to volumes
                vt = edited_data["volume_titles"]
                if isinstance(vt, list) and "volumes" in data:
                    for i, vol in enumerate(data["volumes"]):
                        if i < len(vt) and vt[i]:
                            vol["title"] = vt[i]
            if "volume_events" in edited_data:
                ve = edited_data["volume_events"]
                if isinstance(ve, list) and "volumes" in data:
                    for i, vol in enumerate(data["volumes"]):
                        if i < len(ve) and ve[i]:
                            vol["major_events"] = [e.strip() for e in ve[i].split("\n") if e.strip()]
            if "volume_conflicts" in edited_data:
                vc = edited_data["volume_conflicts"]
                if isinstance(vc, list) and "volumes" in data:
                    for i, vol in enumerate(data["volumes"]):
                        if i < len(vc) and vc[i]:
                            vol["main_conflict"] = vc[i]
            if "volume_goals" in edited_data:
                vg = edited_data["volume_goals"]
                if isinstance(vg, list) and "volumes" in data:
                    for i, vol in enumerate(data["volumes"]):
                        if i < len(vg) and vg[i]:
                            vol["protagonist_goal"] = vg[i]
            if "volume_hooks" in edited_data:
                vh = edited_data["volume_hooks"]
                if isinstance(vh, list) and "volumes" in data:
                    for i, vol in enumerate(data["volumes"]):
                        if i < len(vh) and vh[i]:
                            vol["ending_hook"] = vh[i]
            outline.result_json = json.dumps(data, ensure_ascii=False, indent=2)
        except (json.JSONDecodeError, ValueError, KeyError):
            pass

        outline.updated_at = datetime.now(timezone.utc)
        db.commit()
        return outline
