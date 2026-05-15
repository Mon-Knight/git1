"""
AI World Engine - Novel Draft Service
Builds prompts, generates single-chapter drafts via AI, and manages CRUD.
"""
import json
import re
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models import (
    NovelDraft,
    NovelChapterOutline,
    NovelVolumeOutline,
    SimulationRecord,
    StyleProfile,
    PlotAnchor,
    ContextPackage,
)


class NovelDraftService:
    """Service for novel draft generation and management."""

    DRAFT_SYSTEM_PROMPT = """你是长篇小说正文撰写助手。
你需要基于主线章节方案撰写单章正文初稿，必须遵守世界设定和已确认正史。
"""

    @staticmethod
    def build_novel_draft_prompt(db: Session, world_id: int, request_data: Dict[str, Any]) -> str:
        """Build prompt for single-chapter draft generation."""
        from app.models import World, Character, Faction, Location, WorldRule, HistoricalEvent

        world = db.query(World).filter_by(id=world_id).first()
        if not world:
            raise ValueError("世界不存在")

        chapter_outline_id = _to_int(request_data.get("chapter_outline_id"))
        chapter_index = _to_int(request_data.get("chapter_index"))
        if not chapter_outline_id or chapter_index is None:
            raise ValueError("请选择要生成的章节")

        outline = db.query(NovelChapterOutline).filter_by(
            id=chapter_outline_id, world_id=world_id
        ).first()
        if not outline:
            raise ValueError("主线章节方案不存在")

        chapters = _extract_chapters(outline.result_json)
        if not chapters:
            raise ValueError("主线章节方案缺少章节结构")

        chapter = _find_chapter(chapters, chapter_index)
        if not chapter:
            raise ValueError("未找到对应章节，请重新选择")

        volume_outline = db.query(NovelVolumeOutline).filter_by(
            id=outline.volume_outline_id, world_id=world_id
        ).first()

        main_evo = db.query(SimulationRecord).filter_by(
            world_id=world_id, simulation_type="novel_evolution", status="adopted"
        ).order_by(SimulationRecord.created_at.desc()).first()

        style_profile_id = _to_int(request_data.get("style_profile_id"))
        plot_anchor_id = _to_int(request_data.get("plot_anchor_id"))
        context_package_id = _to_int(request_data.get("context_package_id"))

        target_words = (request_data.get("target_words") or "").strip()
        narrative_pov = (request_data.get("narrative_pov") or "").strip()
        pacing_requirement = (request_data.get("pacing_requirement") or "").strip()
        extra_requirements = (request_data.get("extra_requirements") or "").strip()

        strict_outline = _to_bool(request_data.get("strict_outline"))
        emphasize_psychology = _to_bool(request_data.get("emphasize_psychology"))
        emphasize_scene = _to_bool(request_data.get("emphasize_scene"))
        emphasize_dialogue = _to_bool(request_data.get("emphasize_dialogue"))

        parts = []
        parts.append("【生成规则】")
        parts.append("1. 只生成单章正文初稿，不生成下一章，不生成整卷，不生成整本书。")
        parts.append("2. 不修改章节大纲、分卷大纲、全书演化方案，不修改世界设定和正史。")
        parts.append("3. 不自动设为采用稿，输出仅为候选草稿。")
        parts.append("4. 必须遵守主线章节方案与已确认正史。")
        parts.append("5. 必须体现本章主要冲突、人物动机与情绪变化。")
        parts.append("6. 必须安排信息释放与章末钩子。")
        parts.append("7. 输出中文正文，不得抄袭，不得使用现成作品专有名词。")

        parts.append("\n【世界信息】")
        parts.append(f"世界名称：{world.name}")
        parts.append(f"世界类型：{world.world_type or '未指定'}")
        parts.append(f"当前时代：{world.current_era or '未指定'}")
        parts.append(f"世界基调：{world.tone or '未指定'}")
        parts.append(f"世界简介：{world.description or '无'}")

        chars = db.query(Character).filter_by(world_id=world_id).limit(15).all()
        if chars:
            parts.append(f"\n【已采纳角色】({len(chars)}人)")
            for c in chars:
                parts.append(f"- {c.name}（{c.role or '未知角色'}），状态：{c.current_status}，性格：{c.personality[:80] if c.personality else '无'}")

        factions = db.query(Faction).filter_by(world_id=world_id).limit(10).all()
        if factions:
            parts.append(f"\n【已采纳势力】({len(factions)}个)")
            for f in factions:
                parts.append(f"- {f.name}（{f.faction_type or '未知类型'}），目标：{f.goal[:80] if f.goal else '无'}")

        locations = db.query(Location).filter_by(world_id=world_id).limit(10).all()
        if locations:
            parts.append(f"\n【已采纳地点】({len(locations)}个)")
            for l in locations:
                parts.append(f"- {l.name}（{l.location_type or '未知类型'}）：{l.description[:80] if l.description else '无'}")

        rules = db.query(WorldRule).filter_by(world_id=world_id).limit(10).all()
        if rules:
            parts.append(f"\n【已采纳规则】({len(rules)}条)")
            for r in rules:
                parts.append(f"- {r.name}（{r.rule_type or '通用'}）：{r.content[:100] if r.content else '无'}")

        events = db.query(HistoricalEvent).filter_by(world_id=world_id, is_canon=True).limit(10).all()
        if events:
            parts.append(f"\n【正史事件】({len(events)}条)")
            for e in events:
                parts.append(f"- {e.event_time or '?'} | {e.title}：{e.content[:100] if e.content else '无'}")

        parts.append("\n【主线全书演化方案】")
        if main_evo:
            parts.append(f"标题：{main_evo.question or '(无标题)'}")
            parts.append(f"内容摘要：{(main_evo.ai_response or '')[:1500] or '(空)'}")
        else:
            parts.append("未找到已采纳主线演化方案。")

        if volume_outline:
            parts.append("\n【主线分卷方案】")
            parts.append(f"标题：{volume_outline.title or '未命名'}")
            parts.append(f"分卷总数：{volume_outline.volume_count}")
            parts.append(f"卷序号：{outline.volume_index} | 卷标题：{outline.volume_title or '未命名'}")
        else:
            parts.append("\n【主线分卷方案】未找到对应分卷方案。")

        parts.append("\n【主线章节方案】")
        parts.append(f"章节方案标题：{outline.title or '未命名'}")
        parts.append(f"章节数量：{outline.chapter_count}")

        parts.append("\n【本次选择章节】")
        parts.append(f"章节序号：{chapter.get('chapter_index', chapter_index)}")
        parts.append(f"章节标题：{chapter.get('title') or chapter.get('chapter_title') or '未命名'}")
        parts.append(f"章节目标：{chapter.get('chapter_goal') or '未提供'}")
        parts.append(f"主要冲突：{chapter.get('main_conflict') or '未提供'}")
        parts.append(f"关键角色：{_join_list(chapter.get('key_characters'))}")
        parts.append(f"关键地点：{_join_list(chapter.get('key_locations'))}")
        parts.append(f"剧情事件：{_join_list(chapter.get('plot_events'))}")
        parts.append(f"情绪推进：{chapter.get('emotional_beat') or '未提供'}")
        parts.append(f"伏笔信息：{chapter.get('foreshadowing') or '未提供'}")
        parts.append(f"章末钩子：{chapter.get('ending_hook') or '未提供'}")
        parts.append(f"预计字数：{chapter.get('estimated_words') or '未提供'}")

        if style_profile_id:
            sp = db.query(StyleProfile).filter_by(id=style_profile_id).first()
            if sp:
                parts.append("\n【写作风格方案】")
                parts.append(f"名称：{sp.name}")
                parts.append(f"题材：{sp.genre or '未指定'}；叙事视角：{sp.narrative_pov or '未指定'}；节奏：{sp.pacing or '未指定'}")

        if plot_anchor_id:
            pa = db.query(PlotAnchor).filter_by(id=plot_anchor_id, world_id=world_id).first()
            if pa:
                parts.append("\n【剧情时间点】")
                parts.append(f"{pa.name}（阶段：{pa.stage or '未指定'}，当前冲突：{pa.current_conflict[:100] if pa.current_conflict else '无'}）")

        if context_package_id:
            cp = db.query(ContextPackage).filter_by(id=context_package_id, world_id=world_id).first()
            if cp:
                parts.append("\n【创作上下文包】")
                parts.append(f"{cp.name}：{cp.description[:200] if cp.description else '无'}")

        parts.append("\n【写作参数】")
        parts.append(f"目标字数：{target_words or '未指定'}")
        parts.append(f"叙事人称：{narrative_pov or '未指定'}")
        parts.append(f"节奏要求：{pacing_requirement or '未指定'}")
        parts.append(f"严格遵守章节大纲：{'是' if strict_outline else '否'}")
        parts.append(f"强调人物心理：{'是' if emphasize_psychology else '否'}")
        parts.append(f"强调场景描写：{'是' if emphasize_scene else '否'}")
        parts.append(f"强调对话推进：{'是' if emphasize_dialogue else '否'}")
        if extra_requirements:
            parts.append(f"补充要求：{extra_requirements}")

        parts.append("\n【输出格式建议】")
        parts.append("标题：<章节标题>")
        parts.append("正文：<正文内容>")
        parts.append("作者备注：<可选>")

        return "\n".join(parts)

    @staticmethod
    def generate_novel_draft(db: Session, world_id: int, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a novel draft using AI (or Mock)."""
        from app.services.ai.model_router import ModelRouter
        from app.services.settings_service import SettingsService

        prompt = NovelDraftService.build_novel_draft_prompt(db, world_id, request_data)

        is_mock = not SettingsService.is_live_enabled(db)
        if is_mock:
            raw_text = NovelDraftService._mock_generate(db, world_id, request_data)
        else:
            try:
                client = ModelRouter.get_client(db, "novel_evolution")
                full_prompt = NovelDraftService.DRAFT_SYSTEM_PROMPT + "\n\n" + prompt
                raw_text = client.generate(full_prompt) or ""
            except Exception as e:
                raise RuntimeError(f"AI 调用失败: {str(e)}")

        if not raw_text.strip():
            raise RuntimeError("AI 返回空文本，请稍后再试")

        content = NovelDraftService.extract_draft_content(raw_text)
        if not content.strip():
            content = raw_text.strip()

        return {
            "prompt": prompt,
            "content": content,
            "raw_text": raw_text,
            "word_count": _count_words(content),
            "is_mock": is_mock,
        }

    @staticmethod
    def save_novel_draft(
        db: Session,
        world_id: int,
        request_data: Dict[str, Any],
        prompt: str,
        content: str,
        raw_text: str = "",
    ) -> NovelDraft:
        """Save a generated novel draft."""
        chapter_outline_id = _to_int(request_data.get("chapter_outline_id"))
        chapter_index = _to_int(request_data.get("chapter_index"))
        if not chapter_outline_id or chapter_index is None:
            raise ValueError("请选择要生成的章节")

        outline = db.query(NovelChapterOutline).filter_by(
            id=chapter_outline_id, world_id=world_id
        ).first()
        if not outline:
            raise ValueError("主线章节方案不存在")

        chapters = _extract_chapters(outline.result_json)
        if not chapters:
            raise ValueError("主线章节方案缺少章节结构")

        chapter = _find_chapter(chapters, chapter_index)
        if not chapter:
            raise ValueError("未找到对应章节")

        chapter_title = chapter.get("title") or chapter.get("chapter_title") or ""
        title = chapter_title or f"第{chapter_index}章 正文草稿"

        generation_requirement = _build_generation_requirement(request_data)

        draft = NovelDraft(
            world_id=world_id,
            chapter_outline_id=chapter_outline_id,
            volume_index=outline.volume_index,
            volume_title=outline.volume_title or "",
            chapter_index=chapter_index,
            chapter_title=chapter_title,
            title=title,
            style_profile_id=_to_int(request_data.get("style_profile_id")),
            context_package_id=_to_int(request_data.get("context_package_id")),
            plot_anchor_id=_to_int(request_data.get("plot_anchor_id")),
            generation_requirement=generation_requirement,
            prompt=prompt,
            content=content,
            raw_text=raw_text or "",
            word_count=_count_words(content),
            status="candidate",
            is_accepted=False,
        )
        db.add(draft)
        db.commit()
        db.refresh(draft)
        return draft

    @staticmethod
    def list_novel_drafts(db: Session, world_id: int) -> List[NovelDraft]:
        """List all novel drafts for a world, newest first."""
        return db.query(NovelDraft).filter_by(world_id=world_id).order_by(
            NovelDraft.created_at.desc()
        ).all()

    @staticmethod
    def get_novel_draft(db: Session, world_id: int, draft_id: int) -> Optional[NovelDraft]:
        """Get a specific draft, verifying world ownership."""
        return db.query(NovelDraft).filter_by(id=draft_id, world_id=world_id).first()

    @staticmethod
    def set_accepted_novel_draft(db: Session, world_id: int, draft_id: int) -> NovelDraft:
        """Mark a draft as accepted and unset prior accepted draft for same chapter."""
        draft = NovelDraftService.get_novel_draft(db, world_id, draft_id)
        if not draft:
            raise ValueError("正文草稿不存在")
        if draft.status == "discarded":
            raise ValueError("已废弃草稿不能标记为采用稿")

        existing = db.query(NovelDraft).filter_by(
            world_id=world_id,
            chapter_outline_id=draft.chapter_outline_id,
            chapter_index=draft.chapter_index,
            is_accepted=True,
        ).first()
        if existing and existing.id != draft.id:
            existing.is_accepted = False
            if existing.status == "accepted":
                existing.status = "candidate"

        draft.status = "accepted"
        draft.is_accepted = True
        draft.accepted_at = datetime.now(timezone.utc)
        db.commit()
        return draft

    @staticmethod
    def discard_novel_draft(db: Session, world_id: int, draft_id: int) -> NovelDraft:
        """Discard a novel draft."""
        draft = NovelDraftService.get_novel_draft(db, world_id, draft_id)
        if not draft:
            raise ValueError("正文草稿不存在")
        if draft.status == "discarded":
            raise ValueError("该正文草稿已被废弃")

        draft.status = "discarded"
        draft.is_accepted = False
        db.commit()
        return draft

    @staticmethod
    def update_novel_draft(
        db: Session, world_id: int, draft_id: int, edited_data: Dict[str, Any]
    ) -> NovelDraft:
        """Update a draft's editable fields."""
        draft = NovelDraftService.get_novel_draft(db, world_id, draft_id)
        if not draft:
            raise ValueError("正文草稿不存在")
        if draft.status == "discarded":
            raise ValueError("已废弃的正文草稿不能编辑")

        if edited_data.get("title"):
            draft.title = edited_data["title"].strip()
        if edited_data.get("content"):
            draft.content = edited_data["content"].strip()
            draft.word_count = _count_words(draft.content)
        if edited_data.get("notes") is not None:
            draft.notes = edited_data["notes"].strip()

        draft.updated_at = datetime.now(timezone.utc)
        db.commit()
        return draft

    @staticmethod
    def extract_draft_content(raw_text: str) -> str:
        """Extract the正文 content from AI response."""
        if not raw_text:
            return ""
        text = raw_text.strip()

        # Prefer explicit 正文 section
        match = re.search(r"正文[:：]\s*", text)
        if match:
            content = text[match.end():]
            content = re.split(r"\n\s*(作者备注|作者说明|备注)[:：]", content, maxsplit=1)[0]
            return content.strip()

        # Remove leading 标题 section if present
        if text.startswith("标题"):
            parts = re.split(r"\n+", text, maxsplit=1)
            if len(parts) > 1:
                text = parts[1].strip()

        return text.strip()

    @staticmethod
    def _mock_generate(db: Session, world_id: int, request_data: Dict[str, Any]) -> str:
        """Generate a stable mock draft response."""
        chapter_outline_id = _to_int(request_data.get("chapter_outline_id"))
        chapter_index = _to_int(request_data.get("chapter_index"))
        outline = db.query(NovelChapterOutline).filter_by(
            id=chapter_outline_id, world_id=world_id
        ).first()
        chapters = _extract_chapters(outline.result_json if outline else "")
        chapter = _find_chapter(chapters, chapter_index) if chapters else {}
        title = chapter.get("title") or chapter.get("chapter_title") or f"第{chapter_index}章"
        goal = chapter.get("chapter_goal") or "推进主线目标"
        conflict = chapter.get("main_conflict") or "冲突逐步升级"
        characters = _join_list(chapter.get("key_characters")) or "主角、重要角色"
        locations = _join_list(chapter.get("key_locations")) or "关键地点"
        events = _join_list(chapter.get("plot_events")) or "关键事件"
        emotion = chapter.get("emotional_beat") or "情绪递进"
        hook = chapter.get("ending_hook") or "章末钩子"

        paragraphs = [
            f"{title}开篇以{locations}的氛围展开，主角在当下局势中再次确认本章目标：{goal}。清晨的光线透过窗棂洒落，在地面投下斑驳的影子，空气里带着微凉的湿意，一切都显得平静而暗藏波澜。",
            f"围绕{conflict}的矛盾逐步显现，{characters}之间的关系被迫重新调整，言语与行动都带着试探。每个人都在观察别人的反应，同时在权衡自己的位置与立场。",
            f"事件的推进从{events}开始，细节在场景中铺陈。环境的变化、人物微表情的波动、道具的象征意味，都在不动声色地传递着隐藏的信息，读者能感知到水面之下的暗流。",
            f"主角在关键节点产生犹疑，心理层面被{emotion}牵引。内心独白与外在行动之间的落差，让决策的代价变得清晰而沉重——每一次选择都不可逆转，每一步都在塑造命运的走向。",
            f"矛盾冲突在中段达到首次爆点，外部压力与内心坚持形成拉扯。动作的节奏明显加快，场景之间的切换更加紧凑，读者几乎能听到时间流逝的声响。信息释放的节奏被精准控制，每一条线索都在恰到好处的时刻浮现。",
            f"随着线索汇聚，人物动机被逐步揭示。过去的片断、隐藏的关联、未说出口的真相，在情节推进中慢慢拼接成完整的图景。隐含的伏笔开始发出回响，前文的细节在此刻获得新的意义。",
            f"场景描写转向更紧张的区域，氛围从克制走向紧绷。环境的变化——光线的明暗、温度的高低、声音的远近——都在强化冲突的力量，将情绪推向更高的维度。读者仿佛身临其境，感受到空气中凝结的压力。",
            f"角色间的对话推动剧情前行，言辞背后透露出新的立场与选择。对话不仅仅是信息的交换，更是力量的博弈——每一句话都可能是试探、是威胁、是妥协，或是一步精心设计的棋。情感强度在对话中持续上升，人物关系在言语之间被重新定义。",
            f"主角以一次关键行动推动局势转向，新的风险与机会同步出现。行动的结果并非简单的成功或失败，而是在原有的格局中撕开一道裂缝，让全新的可能性涌入。冲突进入第二阶段，格局被重新洗牌。",
            f"本章尾声收束到更大的疑问与不安，{hook}成为悬念焦点。主角在短暂的平静中回望当前处境，确认下一步方向，为后续章节奠定动力。读者被留在悬而未决的情绪中，迫不及待想要翻到下一页。",
            f"最后的视角落在未解的线索上，情绪余波延续。章节在情节闭环与开放悬念之间找到微妙的平衡——本段故事告一段落，但更大的谜团才刚刚露出冰山一角。",
            f"环境再次归于寂静，但空气中弥漫着未散尽的张力。主角的背影融入渐深的暮色之中，前方道路模糊而充满变数，而读者已经深深沉浸在这个世界之中，期待下一章的展开。",
        ]
        body = "\n\n".join(paragraphs)
        return f"标题：{title}\n\n正文：\n{body}\n\n作者备注：这是 Mock 模式生成的示例正文，用于测试流程。本Mock文本长度已满足最低字数要求，内容围绕所选章节标题展开，体现章节目标与冲突推进，并含有章末钩子。"


def _to_int(value: Any) -> Optional[int]:
    try:
        if value is None or value == "":
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).lower() in ("1", "true", "yes", "on")


def _count_words(text: str) -> int:
    if not text:
        return 0
    return len(re.sub(r"\s+", "", text))


def _extract_chapters(result_json: str) -> List[Dict[str, Any]]:
    try:
        data = json.loads(result_json or "")
        return data.get("chapters", []) if isinstance(data, dict) else []
    except (json.JSONDecodeError, ValueError, TypeError):
        return []


def _find_chapter(chapters: List[Dict[str, Any]], chapter_index: int) -> Optional[Dict[str, Any]]:
    for ch in chapters:
        try:
            if int(ch.get("chapter_index", -1)) == chapter_index:
                return ch
        except (TypeError, ValueError):
            continue
    return None


def _join_list(value: Any) -> str:
    if isinstance(value, list):
        return "、".join([str(v) for v in value if v])
    if isinstance(value, str):
        return value
    return ""


def _build_generation_requirement(request_data: Dict[str, Any]) -> str:
    parts = []
    target_words = (request_data.get("target_words") or "").strip()
    narrative_pov = (request_data.get("narrative_pov") or "").strip()
    pacing_requirement = (request_data.get("pacing_requirement") or "").strip()
    extra_requirements = (request_data.get("extra_requirements") or "").strip()

    if target_words:
        parts.append(f"目标字数：{target_words}")
    if narrative_pov:
        parts.append(f"叙事人称：{narrative_pov}")
    if pacing_requirement:
        parts.append(f"节奏要求：{pacing_requirement}")
    if _to_bool(request_data.get("strict_outline")):
        parts.append("严格遵守章节大纲")
    if _to_bool(request_data.get("emphasize_psychology")):
        parts.append("强调人物心理")
    if _to_bool(request_data.get("emphasize_scene")):
        parts.append("强调场景描写")
    if _to_bool(request_data.get("emphasize_dialogue")):
        parts.append("强调对话推进")
    if extra_requirements:
        parts.append(f"补充要求：{extra_requirements}")

    return "；".join(parts)
