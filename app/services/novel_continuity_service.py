"""
AI World Engine - Novel Continuity Service
v2.5.0: Chapter-to-chapter continuity and cross-chapter consistency checking.
Reads chapter content, builds prompts, generates continuity reports.
Does NOT modify any content.
"""

import json
import re
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.models import NovelContinuityReport


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class NovelContinuityService:
    """Service for chapter continuity analysis and reporting."""

    RANGE_TYPES = [
        ("adjacent", "相邻两章"),
        ("chapter_range", "指定章节范围"),
        ("volume", "当前卷"),
        ("recent", "最近若干章"),
    ]

    @staticmethod
    def build_continuity_context(
        db: Session, world_id: int, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build full context for continuity checking."""
        from app.models import (
            World, Character, Faction, Location, WorldRule,
            HistoricalEvent, NovelVolumeOutline, NovelChapterOutline,
            NovelDraft, NovelFinalDraft, NovelDraftRevision,
            StyleProfile, PlotAnchor, ContextPackage,
        )

        world = db.query(World).filter(World.id == world_id).first()
        context = {
            "world_name": world.name if world else "未知世界",
            "world_desc": (world.description or "")[:500] if world else "",
            "characters": [],
            "factions": [],
            "locations": [],
            "rules": [],
            "events": [],
            "chapters": [],
            "style_profile": None,
        }

        # Characters
        chars = db.query(Character).filter(Character.world_id == world_id).limit(20).all()
        for c in chars:
            context["characters"].append({
                "name": c.name or "",
                "role": getattr(c, "role", "") or "",
                "status": getattr(c, "current_status", "") or "",
                "personality": getattr(c, "personality", "") or "",
                "goal": getattr(c, "goal", "") or "",
            })

        # Factions
        factions = db.query(Faction).filter(Faction.world_id == world_id).limit(10).all()
        for f in factions:
            context["factions"].append({
                "name": f.name or "",
                "type": getattr(f, "faction_type", "") or "",
                "goal": getattr(f, "goal", "") or "",
            })

        # Locations
        locs = db.query(Location).filter(Location.world_id == world_id).limit(10).all()
        for l in locs:
            context["locations"].append({
                "name": l.name or "",
                "type": getattr(l, "location_type", "") or "",
                "region": getattr(l, "region", "") or "",
            })

        # Rules
        rules = db.query(WorldRule).filter(WorldRule.world_id == world_id).limit(10).all()
        for r in rules:
            context["rules"].append({
                "name": r.name or "",
                "type": getattr(r, "rule_type", "") or "",
                "content": getattr(r, "content", "") or "",
            })

        # Events (canon only)
        events = db.query(HistoricalEvent).filter(
            HistoricalEvent.world_id == world_id, HistoricalEvent.is_canon == True
        ).limit(15).all()
        for e in events:
            context["events"].append({
                "title": e.title or "",
                "era": getattr(e, "event_time", "") or "",
                "description": (e.content or "")[:200],
            })

        # Style profile
        style_profile_id = request_data.get("style_profile_id")
        if style_profile_id:
            sp = db.query(StyleProfile).filter(StyleProfile.id == style_profile_id).first()
            if sp:
                context["style_profile"] = {
                    "name": sp.name,
                    "do_rules": sp.do_rules or "",
                    "avoid_rules": sp.avoid_rules or "",
                }

        return context

    @staticmethod
    def get_chapter_texts_for_range(
        db: Session, world_id: int, request_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get chapter texts for a given range, with final-draft priority."""
        from app.models import NovelChapterOutline, NovelDraft, NovelFinalDraft, NovelDraftRevision

        range_type = request_data.get("range_type", "recent")
        start_idx = request_data.get("start_chapter_index", 1)
        end_idx = request_data.get("end_chapter_index", 5)
        recent_count = request_data.get("recent_count", 3)

        # Get chapters (order by id as proxy for chapter order)
        query = db.query(NovelChapterOutline).filter(
            NovelChapterOutline.world_id == world_id, NovelChapterOutline.is_main == True
        ).order_by(NovelChapterOutline.id)

        if range_type == "recent":
            chapters = query.order_by(NovelChapterOutline.id.desc()).limit(recent_count).all()
            chapters = list(reversed(chapters))
        elif range_type == "volume":
            vol_id = request_data.get("volume_outline_id")
            if vol_id:
                chapters = query.filter(NovelChapterOutline.volume_outline_id == vol_id).all()
            else:
                chapters = query.all()
        else:
            # Use id range as proxy for chapter index
            chapters = query.filter(
                NovelChapterOutline.id >= start_idx,
                NovelChapterOutline.id <= end_idx
            ).all()

        results = []
        for ch in chapters:
            text = None
            source_type = "none"
            source_id = None

            # Priority 1: Final draft
            fd = db.query(NovelFinalDraft).filter(
                NovelFinalDraft.chapter_outline_id == ch.id,
                NovelFinalDraft.is_active == True
            ).first()
            if fd and fd.content_snapshot:
                text = fd.content_snapshot
                source_type = "final_draft"
                source_id = fd.id

            # Priority 2: Accepted revision
            if not text:
                rev = db.query(NovelDraftRevision).filter(
                    NovelDraftRevision.chapter_outline_id == ch.id,
                    NovelDraftRevision.status == "accepted"
                ).first()
                if rev and rev.content:
                    text = rev.content
                    source_type = "revision"
                    source_id = rev.id

            # Priority 3: Accepted draft
            if not text:
                draft = db.query(NovelDraft).filter(
                    NovelDraft.chapter_outline_id == ch.id,
                    NovelDraft.is_accepted == True
                ).first()
                if draft and draft.content:
                    text = draft.content
                    source_type = "draft"
                    source_id = draft.id

            # Priority 4: Raw draft
            if not text:
                draft = db.query(NovelDraft).filter(
                    NovelDraft.chapter_outline_id == ch.id
                ).order_by(NovelDraft.created_at.desc()).first()
                if draft and draft.content:
                    text = draft.content
                    source_type = "raw_draft"
                    source_id = draft.id

            results.append({
                "chapter_index": getattr(ch, "chapter_index", ch.id),
                "chapter_title": ch.title or f"章节{ch.id}",
                "volume_index": getattr(ch, "volume_index", 1),
                "chapter_outline_id": ch.id,
                "text": text[:3000] if text else None,  # Truncate for prompt
                "text_length": len(text) if text else 0,
                "source_type": source_type,
                "source_id": source_id,
                "has_text": text is not None,
            })

        return results

    @staticmethod
    def build_continuity_prompt(
        db: Session, world_id: int, request_data: Dict[str, Any]
    ) -> str:
        """Build the continuity check prompt."""
        context = NovelContinuityService.build_continuity_context(db, world_id, request_data)
        chapters = NovelContinuityService.get_chapter_texts_for_range(db, world_id, request_data)

        range_type = request_data.get("range_type", "recent")
        style_profile_id = request_data.get("style_profile_id")
        user_requirement = request_data.get("user_requirement", "")

        # Build chapter summary
        chapter_lines = []
        for ch in chapters:
            status = "✅" if ch["has_text"] else "⚠️ 缺失正文"
            chapter_lines.append(
                f"第{ch['chapter_index']}章「{ch['chapter_title']}」"
                f"（来源: {ch['source_type']}, 长度: {ch['text_length']}字）{status}"
            )
        chapter_summary = "\n".join(chapter_lines)

        # Chapter texts
        chapter_texts = []
        for ch in chapters:
            if ch["text"]:
                chapter_texts.append(
                    f"--- 第{ch['chapter_index']}章「{ch['chapter_title']}」（{ch['source_type']}）---\n"
                    f"{ch['text']}\n"
                )
        full_text = "\n".join(chapter_texts)

        # Style profile section
        style_section = ""
        if context.get("style_profile"):
            sp = context["style_profile"]
            style_section = f"""
【参考风格画像】
名称：{sp['name']}
应遵守：{sp['do_rules']}
应避免：{sp['avoid_rules']}
"""

        chars_str = ", ".join([c["name"] for c in context["characters"]]) or "无"

        prompt = f"""【章节连续性检查任务】
你是一位专业的小说编辑，需要对以下章节进行连续性和一致性检查。

【世界信息】
名称：{context['world_name']}
简介：{context['world_desc']}

【已知角色】{chars_str}

【检查范围】
类型：{range_type}
{chapter_summary}

{style_section}
{'- 补充检查要求：' + user_requirement if user_requirement else ''}

【章节正文】
{full_text if full_text else '（当前范围内没有正文内容，无法进行连续性检查）'}

【检查要求】
请基于以上章节正文，生成一份章节连续性检查报告。

重要约束：
1. 你只能生成检查报告，绝对不能修改正文。
2. 绝对不能生成新章节内容。
3. 绝对不能润色或重写正文。
4. 绝对不能改变角色、地点、事件设定。
5. 只分析连续性问题，不修改原文。

检查维度：
1. 时间线连续性：章节间时间顺序是否合理。
2. 人物状态连续性：伤势、位置、身份、关系是否前后一致。
3. 地点移动合理性：角色位移是否有过渡说明。
4. 剧情因果连续性：上一章是否自然引出下一章。
5. 伏笔与回收：前文伏笔是否被遗忘，后文是否突然出现未铺垫信息。
6. 世界设定一致性：力量体系、规则是否前后矛盾。
7. 角色动机连续性：目标、态度变化是否有过渡。
8. 冲突推进连续性：主要冲突是否持续推进。
{"9. 文风一致性：多章之间是否符合风格画像。" if style_profile_id else ""}

【输出格式】
请严格输出以下 JSON 格式：
{{
  "title": "章节连续性检查报告",
  "overall_score": 82,
  "summary": "整体连续性评价（50-100字）",
  "scores": {{
    "timeline": 85,
    "character_state": 78,
    "plot_causality": 82,
    "setting_consistency": 80,
    "foreshadowing": 76,
    "style_consistency": 84
  }},
  "strengths": ["优点1", "优点2"],
  "issues": [
    {{
      "category": "人物状态不连续",
      "severity": "high",
      "chapters": [2, 3],
      "description": "问题描述",
      "evidence": "概括性说明，不复制长段原文",
      "suggestion": "修改建议"
    }}
  ],
  "continuity_threads": [
    {{"name": "主角目标线", "status": "stable", "notes": "目标持续贯穿"}}
  ],
  "missing_context": ["第X章缺少最终采用稿"],
  "revision_suggestions": [
    {{"priority": "high", "target_chapter": 3, "suggestion": "建议1"}}
  ],
  "next_step": "建议优先修复..."
}}

所有内容用中文输出。不要包含任何 JSON 之外的文字。"""
        return prompt

    @staticmethod
    def generate_continuity_report(
        db: Session, world_id: int, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate continuity report using AI or Mock."""
        try:
            from app.services.ai.model_router import ModelRouter

            prompt = NovelContinuityService.build_continuity_prompt(db, world_id, request_data)
            client = ModelRouter.get_client(db, task_type="simulation")
            resp = client.generate(messages=[{"role": "user", "content": prompt}])
            ai_response = resp.get("content", "") if isinstance(resp, dict) else str(resp)

            return {
                "ok": True,
                "prompt": prompt,
                "raw_response": ai_response,
                "is_mock": getattr(client, "is_mock", False),
            }
        except Exception as e:
            return {"ok": False, "error": str(e), "prompt": ""}

    @staticmethod
    def mock_generate() -> Dict[str, Any]:
        """Generate a stable mock continuity report for testing."""
        return {
            "title": "章节连续性检查报告",
            "overall_score": 82,
            "summary": "整体连续性良好，部分人物状态过渡需要优化。前3章情节推进自然，第4章开始出现一些前后设定不一致。",
            "scores": {
                "timeline": 85,
                "character_state": 78,
                "plot_causality": 82,
                "setting_consistency": 80,
                "foreshadowing": 76,
                "style_consistency": 84,
            },
            "strengths": [
                "章节间时间衔接自然，无突兀跳跃",
                "主要冲突线持续推进，未出现中断",
                "文风在多章间保持相对一致",
            ],
            "issues": [
                {
                    "category": "人物状态不连续",
                    "severity": "high",
                    "chapters": [2, 3],
                    "description": "角色在第2章末受伤，第3章开头直接参与战斗，缺少恢复过程说明。",
                    "evidence": "第2章末描述受伤较重，第3章开头描写正常战斗姿态。",
                    "suggestion": "在第3章开头添加简短恢复说明，或保留伤势影响以增强真实感。",
                },
                {
                    "category": "设定不一致",
                    "severity": "medium",
                    "chapters": [1, 4],
                    "description": "第1章提到的魔法限制在第4章中被打破，缺少合理解释。",
                    "evidence": "第1章明确魔法需要咒语准备，第4章角色直接瞬发魔法。",
                    "suggestion": "补充魔法使用条件的变化说明，或修正其中一处的设定。",
                },
                {
                    "category": "伏笔遗漏",
                    "severity": "low",
                    "chapters": [1, 3],
                    "description": "第1章提到的重要物品在第3章未出现，读者可能遗忘。",
                    "evidence": "第1章结尾强调物品重要性，后续章节未提及。",
                    "suggestion": "在第3章或第4章适当提及该物品，保持读者记忆。",
                },
            ],
            "continuity_threads": [
                {"name": "主角成长线", "status": "stable", "notes": "主角能力逐步提升，逻辑清晰。"},
                {"name": "反派阴谋线", "status": "unstable", "notes": "第2-3章反派行动突然消失，需检查。"},
                {"name": "情感关系线", "status": "stable", "notes": "主要关系发展自然。"},
            ],
            "missing_context": [
                "第4章缺少最终采用稿，使用原始草稿作为 fallback。",
            ],
            "revision_suggestions": [
                {"priority": "high", "target_chapter": 3, "suggestion": "补充角色从受伤到恢复的过渡。"},
                {"priority": "medium", "target_chapter": 4, "suggestion": "说明魔法限制变化的原因。"},
                {"priority": "low", "target_chapter": 3, "suggestion": "在第3章提及第1章的重要物品。"},
            ],
            "next_step": "建议优先修复高优先级人物状态连续性问题和设定不一致项。修复后可再次运行连续性检查。",
        }

    @staticmethod
    def parse_continuity_response(raw_text: str) -> Dict[str, Any]:
        """Parse AI response into structured data."""
        result = {"parsed": None, "raw": raw_text, "parse_warning": None}
        try:
            match = re.search(r'\{[\s\S]*\}', raw_text)
            if match:
                data = json.loads(match.group())
                if isinstance(data, dict) and "overall_score" in data:
                    result["parsed"] = data
                    return result
        except json.JSONDecodeError:
            pass
        try:
            data = json.loads(raw_text)
            if isinstance(data, dict):
                result["parsed"] = data
                return result
        except json.JSONDecodeError:
            pass
        result["parse_warning"] = "AI 返回内容无法解析为 JSON，以下为原始输出。"
        return result

    @staticmethod
    def save_continuity_report(
        db: Session, world_id: int, request_data: Dict[str, Any],
        prompt: str, result_json: str, raw_text: str = None
    ) -> NovelContinuityReport:
        """Save a continuity report."""
        parsed = NovelContinuityService.parse_continuity_response(raw_text or result_json)
        scores = parsed.get("parsed", {}).get("scores", {}) if parsed.get("parsed") else {}

        record = NovelContinuityReport(
            world_id=world_id,
            range_type=request_data.get("range_type", "recent"),
            volume_index=request_data.get("volume_index"),
            start_chapter_index=request_data.get("start_chapter_index"),
            end_chapter_index=request_data.get("end_chapter_index"),
            style_profile_id=request_data.get("style_profile_id"),
            title=request_data.get("title", "") or f"连续性检查 - {request_data.get('range_type', '')}",
            prompt=prompt,
            result_json=result_json,
            raw_text=raw_text or "",
            overall_score=parsed.get("parsed", {}).get("overall_score") if parsed.get("parsed") else None,
            timeline_score=scores.get("timeline"),
            character_state_score=scores.get("character_state"),
            plot_causality_score=scores.get("plot_causality"),
            setting_consistency_score=scores.get("setting_consistency"),
            foreshadowing_score=scores.get("foreshadowing"),
            style_consistency_score=scores.get("style_consistency"),
            status="candidate",
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def list_continuity_reports(
        db: Session, world_id: int
    ) -> List[NovelContinuityReport]:
        """List continuity reports for a world."""
        return (
            db.query(NovelContinuityReport)
            .filter(NovelContinuityReport.world_id == world_id)
            .order_by(NovelContinuityReport.created_at.desc())
            .all()
        )

    @staticmethod
    def get_continuity_report(
        db: Session, world_id: int, report_id: int
    ) -> Optional[NovelContinuityReport]:
        """Get a continuity report with world ownership check."""
        return (
            db.query(NovelContinuityReport)
            .filter(
                NovelContinuityReport.id == report_id,
                NovelContinuityReport.world_id == world_id,
            )
            .first()
        )

    @staticmethod
    def set_current_report(
        db: Session, world_id: int, report_id: int
    ) -> Dict[str, Any]:
        """Mark a report as current, unmarking any previous current."""
        report = NovelContinuityService.get_continuity_report(db, world_id, report_id)
        if not report:
            return {"ok": False, "error": "报告不存在"}
        if report.status == "discarded":
            return {"ok": False, "error": "已废弃报告不能设为当前参考报告"}

        # Unset previous current
        db.query(NovelContinuityReport).filter(
            NovelContinuityReport.world_id == world_id,
            NovelContinuityReport.is_current == True,
        ).update({"is_current": False})

        report.is_current = True
        report.status = "current"
        report.confirmed_at = _utcnow()
        db.commit()
        return {"ok": True}

    @staticmethod
    def discard_report(
        db: Session, world_id: int, report_id: int
    ) -> Dict[str, Any]:
        """Discard a continuity report."""
        report = NovelContinuityService.get_continuity_report(db, world_id, report_id)
        if not report:
            return {"ok": False, "error": "报告不存在"}
        report.status = "discarded"
        report.is_current = False
        db.commit()
        return {"ok": True}
