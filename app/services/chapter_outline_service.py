"""
AI World Engine - Chapter Outline Service
Builds prompts, generates chapter outlines via AI, and manages CRUD.
"""
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models import NovelChapterOutline, NovelVolumeOutline
from app.config import settings


class ChapterOutlineService:
    """Service for chapter outline generation and management."""

    CHAPTER_SYSTEM_PROMPT = """你是长篇小说章节大纲规划助手。
你需要基于已有的世界观设定、主线分卷方案、创作资产（风格方案、剧情时间点、上下文包），
为某一卷小说生成详细的章节大纲。

重要规则：
1. 你只生成章节大纲候选，不生成正文。
2. 你必须严格遵守主线分卷方案中该卷的核心冲突、主角目标和主要事件。
3. 你必须遵守已确认的正史（canon events），不能推翻已有设定。
4. 你必须尊重已采纳的角色、势力、地点、规则。
5. 每章的剧情目标必须服务于本卷核心冲突。
6. 必须保持角色动机合理。
7. 必须安排冲突推进、信息释放和章末钩子。
8. 输出结果仅为候选方案，用户确认后才成为主线章节方案。
9. 不得抄袭现成作品的专有名词，必须原创。
10. 可以参考题材结构，但内容必须独立创作。

输出格式：严格JSON，包含以下字段：
{
  "title": "第X卷章节大纲方案",
  "volume_index": X,
  "volume_title": "卷标题",
  "summary": "本卷章节安排总览（100-200字）",
  "chapter_count": N,
  "chapters": [
    {
      "chapter_index": 1,
      "title": "章节标题",
      "chapter_goal": "本章剧情目标",
      "main_conflict": "本章主要冲突",
      "pov_character": "视角角色",
      "key_characters": ["角色A", "角色B"],
      "key_locations": ["地点A"],
      "plot_events": ["事件1", "事件2"],
      "emotional_beat": "情绪推进",
      "foreshadowing": "伏笔或信息释放",
      "ending_hook": "章末钩子",
      "estimated_words": 3000,
      "notes": "补充说明"
    }
  ]
}
每章都必须包含以上全部字段。"""

    @staticmethod
    def build_chapter_outline_prompt(
        db: Session, world_id: int,
        volume_outline_id: int,
        volume_index: int,
        style_profile_id: Optional[int] = None,
        plot_anchor_id: Optional[int] = None,
        context_package_id: Optional[int] = None,
        chapter_count: int = 8,
        extra_requirements: str = "",
    ) -> str:
        """Build a prompt for chapter outline generation."""
        from app.models import World, Character, Faction, Location, WorldRule, HistoricalEvent
        from app.models import StyleProfile, PlotAnchor, ContextPackage

        world = db.query(World).filter_by(id=world_id).first()
        if not world:
            raise ValueError(f"World {world_id} not found")

        volume_outline = db.query(NovelVolumeOutline).filter_by(
            id=volume_outline_id, world_id=world_id
        ).first()
        if not volume_outline:
            raise ValueError(f"Volume outline {volume_outline_id} not found")

        parts = []

        # World info
        parts.append("【世界信息】")
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
                parts.append(
                    f"- {c.name}（{c.role or '未知角色'}），状态：{c.current_status}，"
                    f"性格：{c.personality[:80] if c.personality else '无'}"
                )

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

        # Main volume outline
        parts.append(f"\n【主线分卷方案】")
        parts.append(f"分卷方案标题：{volume_outline.title}")
        parts.append(f"分卷总数：{volume_outline.volume_count}")

        # Extract the target volume from the volume outline
        target_volume = None
        try:
            vo_data = json.loads(volume_outline.result_json)
            volumes = vo_data.get("volumes", [])
            for vol in volumes:
                if vol.get("volume_index") == volume_index:
                    target_volume = vol
                    break
        except (json.JSONDecodeError, ValueError):
            pass

        if target_volume:
            parts.append(f"\n【目标分卷详情】")
            parts.append(f"卷标题：{target_volume.get('title', f'第{volume_index}卷')}")
            parts.append(f"核心主题：{target_volume.get('core_theme', '未指定')}")
            parts.append(f"主要矛盾：{target_volume.get('main_conflict', '未指定')}")
            parts.append(f"主角阶段目标：{target_volume.get('protagonist_goal', '未指定')}")
            parts.append(f"关键角色：{', '.join(target_volume.get('key_characters', [])) or '未指定'}")
            parts.append(f"关键势力：{', '.join(target_volume.get('key_factions', [])) or '未指定'}")
            parts.append(f"关键地点：{', '.join(target_volume.get('key_locations', [])) or '未指定'}")
            parts.append(f"主要事件：{'; '.join(target_volume.get('major_events', [])) or '未指定'}")
            parts.append(f"转折点：{target_volume.get('turning_point', '未指定')}")
            parts.append(f"结尾钩子：{target_volume.get('ending_hook', '未指定')}")
            parts.append(f"预计章节数：{target_volume.get('estimated_chapters', '未指定')}")
        else:
            parts.append(f"\n【目标分卷】第 {volume_index} 卷（分卷方案中未找到详细数据，将基于整体方案创作）")

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
        parts.append("\n【生成要求】")
        parts.append(f"目标分卷序号：第 {volume_index} 卷")
        parts.append(f"章节数量：{chapter_count} 章")
        if extra_requirements:
            parts.append(f"补充要求：{extra_requirements}")
        parts.append("请严格按照主线分卷方案中该卷的核心冲突、主要事件和主线安排章节内容。")

        return "\n".join(parts)

    @staticmethod
    def generate_chapter_outline(
        db: Session, world_id: int,
        volume_outline_id: int,
        volume_index: int,
        style_profile_id: Optional[int] = None,
        plot_anchor_id: Optional[int] = None,
        context_package_id: Optional[int] = None,
        chapter_count: int = 8,
        extra_requirements: str = "",
    ) -> Dict[str, Any]:
        """Generate a chapter outline using AI (or Mock)."""
        prompt = ChapterOutlineService.build_chapter_outline_prompt(
            db, world_id, volume_outline_id, volume_index,
            style_profile_id, plot_anchor_id, context_package_id,
            chapter_count, extra_requirements
        )

        from app.services.ai.model_router import ModelRouter
        from app.services.settings_service import SettingsService

        is_mock = not SettingsService.is_live_enabled(db)
        if is_mock:
            result_json, raw_text = ChapterOutlineService._mock_generate(chapter_count, volume_index)
        else:
            try:
                client = ModelRouter.get_client(db, "novel_evolution")
                full_prompt = ChapterOutlineService.CHAPTER_SYSTEM_PROMPT + "\n\n" + prompt
                response = client.generate(full_prompt)
                raw_text = response
                result_json = ChapterOutlineService.parse_response(raw_text)
            except Exception as e:
                raise RuntimeError(f"AI 调用失败: {str(e)}")

        return {
            "prompt": prompt,
            "result_json": json.dumps(result_json, ensure_ascii=False) if isinstance(result_json, dict) else result_json,
            "raw_text": raw_text or "",
            "chapter_count": chapter_count,
            "volume_index": volume_index,
            "is_mock": is_mock,
        }

    @staticmethod
    def _mock_generate(chapter_count: int = 8, volume_index: int = 1) -> tuple:
        """Generate a mock chapter outline for testing."""
        cc = max(8, min(chapter_count, 20))
        mock_chapter_templates = [
            {"title": "异世新生", "goal": "主角适应新环境并发现异常", "conflict": "对新世界的无知 vs 生存本能",
             "pov": "主角", "emotion": "困惑→好奇→决心", "hook": "发现一个神秘符号"},
            {"title": "领主府的阴影", "goal": "揭示领主府的潜在威胁", "conflict": "平民视角 vs 权力压迫",
             "pov": "主角", "emotion": "不安→警觉", "hook": "偷听到一段密谈"},
            {"title": "第一次魔法波动", "goal": "主角首次接触魔法力量", "conflict": "未知力量 vs 自我控制",
             "pov": "主角", "emotion": "震惊→兴奋→恐惧", "hook": "魔法暴走引发意外"},
            {"title": "骑士测试失败", "goal": "主角尝试走传统骑士路线受阻", "conflict": "天赋不符 vs 社会期待",
             "pov": "主角", "emotion": "挫败→自我怀疑", "hook": "出现一个神秘导师"},
            {"title": "法师测试机会", "goal": "获得法师测试的入场券", "conflict": "资格考验 vs 偏见阻碍",
             "pov": "主角", "emotion": "紧张→突破", "hook": "发现自己的魔法天赋异常"},
            {"title": "AI 运算觉醒", "goal": "揭示主角特殊能力的真相", "conflict": "人类身份 vs AI 能力",
             "pov": "主角", "emotion": "震撼→认同危机", "hook": "收到来自未知来源的信息"},
            {"title": "学院邀请", "goal": "收到魔法学院的入学邀请", "conflict": "新机遇 vs 旧生活",
             "pov": "主角", "emotion": "惊喜→矛盾→决断", "hook": "得知学院中存在敌对势力"},
            {"title": "新的追随者", "goal": "结识第一批伙伴", "conflict": "信任建立 vs 各自算盘",
             "pov": "主角", "emotion": "温暖→警惕", "hook": "一个伙伴的身份疑似间谍"},
            {"title": "试炼之门", "goal": "通过入学试炼", "conflict": "极限挑战 vs 团队协作",
             "pov": "主角", "emotion": "紧张→团结→胜利", "hook": "试炼中发现了隐藏的阴谋"},
            {"title": "暗处的眼睛", "goal": "发现有人在监视主角", "conflict": "追踪 vs 反追踪",
             "pov": "主角", "emotion": "不安→愤怒→行动", "hook": "监视者留下一封匿名信"},
            {"title": "第一个任务", "goal": "接受并完成第一个正式任务", "conflict": "任务目标 vs 道德困境",
             "pov": "主角", "emotion": "决心→犹豫→决断", "hook": "任务背后有更大的力量在操纵"},
            {"title": "谜团加深", "goal": "调查神秘符号的来源", "conflict": "探寻真相 vs 危险逼近",
             "pov": "主角", "emotion": "好奇→恐惧→坚定", "hook": "发现符号与自身能力有关联"},
            {"title": "联盟的裂痕", "goal": "团队内部出现信任危机", "conflict": "各自目的 vs 团队利益",
             "pov": "主角", "emotion": "失望→调解→团结", "hook": "其中一个伙伴的秘密被揭开"},
            {"title": "转折之战", "goal": "关键战斗推进剧情", "conflict": "实力差距 vs 智取",
             "pov": "主角", "emotion": "紧张→智慧→胜利", "hook": "战斗后获得关键线索"},
            {"title": "真相浮现", "goal": "揭示本卷核心秘密", "conflict": "认知颠覆 vs 接受现实",
             "pov": "主角", "emotion": "震惊→愤怒→接受", "hook": "为下一卷埋下更大伏笔"},
            {"title": "抉择时刻", "goal": "主角做出本卷最重要选择", "conflict": "两难选择 vs 自我坚持",
             "pov": "主角", "emotion": "矛盾→痛苦→成长", "hook": "选择的后果将影响后续剧情"},
            {"title": "风暴前夕", "goal": "为卷末高潮做最后准备", "conflict": "各方势力集结",
             "pov": "主角", "emotion": "紧张→蓄势", "hook": "一场大战即将爆发"},
            {"title": "试炼之巅", "goal": "本卷高潮对决", "conflict": "终极对抗 vs 信念坚持",
             "pov": "主角", "emotion": "全力→决胜", "hook": "胜利但付出了代价"},
            {"title": "余波与新生", "goal": "总结本卷并展望后续", "conflict": "战果确认 vs 新挑战",
             "pov": "主角", "emotion": "释然→展望", "hook": "新的威胁已悄然降临"},
            {"title": "新征程的起点", "goal": "为本卷画上句号，开启下一卷", "conflict": "休整 vs 新任务",
             "pov": "主角", "emotion": "成长→期待", "hook": "下一卷的冒险已迫在眉睫"},
        ]
        chapters = []
        for i in range(cc):
            idx = i % len(mock_chapter_templates)
            t = mock_chapter_templates[idx]
            chapters.append({
                "chapter_index": i + 1,
                "title": f"第{i+1}章：{t['title']}",
                "chapter_goal": t["goal"],
                "main_conflict": t["conflict"],
                "pov_character": t["pov"],
                "key_characters": ["主角", "导师角色", "盟友角色", "对手角色"],
                "key_locations": ["主要场景", "关键地点"],
                "plot_events": [
                    f"事件1：开启本章主线剧情",
                    f"事件2：推动冲突发展",
                    f"事件3：达到本章高潮",
                ],
                "emotional_beat": t["emotion"],
                "foreshadowing": f"为后续章节埋下关于{t['title']}的伏笔",
                "ending_hook": t["hook"],
                "estimated_words": 3000,
                "notes": f"本章为第{volume_index}卷第{i+1}章，服务于本卷核心冲突",
            })
        result = {
            "title": f"第{volume_index}卷章节大纲候选方案",
            "volume_index": volume_index,
            "volume_title": f"第{volume_index}卷",
            "summary": f"第{volume_index}卷共规划 {cc} 章，从主角觉醒到阶段高潮，逐步推进本卷核心冲突。",
            "chapter_count": cc,
            "chapters": chapters,
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
    def save_chapter_outline(
        db: Session, world_id: int,
        volume_outline_id: int,
        volume_index: int,
        prompt: str, result_json: str, raw_text: str = "",
        chapter_count: int = 0,
        style_profile_id: Optional[int] = None,
        plot_anchor_id: Optional[int] = None,
        context_package_id: Optional[int] = None,
        generation_requirement: str = "",
    ) -> NovelChapterOutline:
        """Save a generated chapter outline."""
        outline = NovelChapterOutline(
            world_id=world_id,
            volume_outline_id=volume_outline_id,
            volume_index=volume_index,
            volume_title="",
            title="",
            style_profile_id=style_profile_id,
            plot_anchor_id=plot_anchor_id,
            context_package_id=context_package_id,
            generation_requirement=generation_requirement,
            prompt=prompt,
            result_json=result_json,
            raw_text=raw_text,
            chapter_count=chapter_count,
            status="candidate",
            is_main=False,
        )
        # Extract title and volume_title from result_json
        try:
            data = json.loads(result_json)
            outline.title = data.get("title", f"章节大纲 #{outline.id or '?'}")
            outline.volume_title = data.get("volume_title", f"第{volume_index}卷")
        except (json.JSONDecodeError, ValueError):
            outline.title = "章节大纲方案"
            outline.volume_title = f"第{volume_index}卷"

        db.add(outline)
        db.commit()
        db.refresh(outline)
        return outline

    @staticmethod
    def list_chapter_outlines(db: Session, world_id: int) -> List[NovelChapterOutline]:
        """List all chapter outlines for a world, newest first."""
        return db.query(NovelChapterOutline).filter_by(world_id=world_id).order_by(
            NovelChapterOutline.created_at.desc()
        ).all()

    @staticmethod
    def get_chapter_outline(db: Session, world_id: int, outline_id: int) -> Optional[NovelChapterOutline]:
        """Get a specific chapter outline, verifying world ownership."""
        return db.query(NovelChapterOutline).filter_by(
            id=outline_id, world_id=world_id
        ).first()

    @staticmethod
    def set_main_chapter_outline(db: Session, world_id: int, outline_id: int) -> NovelChapterOutline:
        """Set a chapter outline as the main plan for its volume."""
        outline = ChapterOutlineService.get_chapter_outline(db, world_id, outline_id)
        if not outline:
            raise ValueError("章节大纲不存在")
        if outline.status == "discarded":
            raise ValueError("已废弃的章节大纲不能设为主线")

        # Unset any existing main for the same world + volume_index
        existing_main = db.query(NovelChapterOutline).filter_by(
            world_id=world_id, volume_index=outline.volume_index, is_main=True
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
    def discard_chapter_outline(db: Session, world_id: int, outline_id: int) -> NovelChapterOutline:
        """Discard a chapter outline."""
        outline = ChapterOutlineService.get_chapter_outline(db, world_id, outline_id)
        if not outline:
            raise ValueError("章节大纲不存在")
        if outline.status == "discarded":
            raise ValueError("该章节大纲已被废弃")

        outline.status = "discarded"
        outline.is_main = False
        db.commit()
        return outline

    @staticmethod
    def update_chapter_outline(
        db: Session, world_id: int, outline_id: int, edited_data: dict
    ) -> NovelChapterOutline:
        """Update a chapter outline's editable fields."""
        outline = ChapterOutlineService.get_chapter_outline(db, world_id, outline_id)
        if not outline:
            raise ValueError("章节大纲不存在")
        if outline.status == "discarded":
            raise ValueError("已废弃的章节大纲不能编辑")

        # Update title
        if "title" in edited_data and edited_data["title"]:
            outline.title = edited_data["title"]

        # Update result_json with edited chapter data
        try:
            data = json.loads(outline.result_json)
            if "title" in edited_data:
                data["title"] = edited_data["title"]
            if "summary" in edited_data:
                data["summary"] = edited_data["summary"]
            if "chapters" in edited_data:
                data["chapters"] = edited_data["chapters"]
            if "chapter_titles" in edited_data:
                ct = edited_data["chapter_titles"]
                if isinstance(ct, list) and "chapters" in data:
                    for i, ch in enumerate(data["chapters"]):
                        if i < len(ct) and ct[i]:
                            ch["title"] = ct[i]
            if "chapter_goals" in edited_data:
                cg = edited_data["chapter_goals"]
                if isinstance(cg, list) and "chapters" in data:
                    for i, ch in enumerate(data["chapters"]):
                        if i < len(cg) and cg[i]:
                            ch["chapter_goal"] = cg[i]
            if "chapter_conflicts" in edited_data:
                cc = edited_data["chapter_conflicts"]
                if isinstance(cc, list) and "chapters" in data:
                    for i, ch in enumerate(data["chapters"]):
                        if i < len(cc) and cc[i]:
                            ch["main_conflict"] = cc[i]
            if "chapter_events" in edited_data:
                ce = edited_data["chapter_events"]
                if isinstance(ce, list) and "chapters" in data:
                    for i, ch in enumerate(data["chapters"]):
                        if i < len(ce) and ce[i]:
                            ch["plot_events"] = [e.strip() for e in ce[i].split("\n") if e.strip()]
            if "chapter_hooks" in edited_data:
                chk = edited_data["chapter_hooks"]
                if isinstance(chk, list) and "chapters" in data:
                    for i, ch in enumerate(data["chapters"]):
                        if i < len(chk) and chk[i]:
                            ch["ending_hook"] = chk[i]
            if "chapter_words" in edited_data:
                cw = edited_data["chapter_words"]
                if isinstance(cw, list) and "chapters" in data:
                    for i, ch in enumerate(data["chapters"]):
                        if i < len(cw) and cw[i]:
                            try:
                                ch["estimated_words"] = int(cw[i])
                            except (ValueError, TypeError):
                                pass
            outline.result_json = json.dumps(data, ensure_ascii=False)
        except (json.JSONDecodeError, ValueError):
            pass

        db.commit()
        return outline

    @staticmethod
    def get_main_volume_outline(db: Session, world_id: int) -> Optional[NovelVolumeOutline]:
        """Get the main volume outline for a world, if any."""
        return db.query(NovelVolumeOutline).filter_by(
            world_id=world_id, is_main=True
        ).first()

    @staticmethod
    def get_main_chapter_outline(db: Session, world_id: int, volume_index: int) -> Optional[NovelChapterOutline]:
        """Get the main chapter outline for a specific volume, if any."""
        return db.query(NovelChapterOutline).filter_by(
            world_id=world_id, volume_index=volume_index, is_main=True
        ).first()
