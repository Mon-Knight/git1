"""
AI World Engine - Novel Quality Service
v2.1.0: Builds prompts, generates quality check reports for novel drafts.
Only generates reports — never modifies drafts, outlines, or world settings.
"""

import json
import re
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session

from app.models import (
    NovelDraft,
    NovelDraftQualityReport,
    NovelChapterOutline,
    NovelVolumeOutline,
    SimulationRecord,
    World,
)


def _utcnow():
    return datetime.now(timezone.utc)


def _to_int(val) -> Optional[int]:
    if val is None or val == "":
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        return None


def _extract_chapters(result_json: str) -> list:
    try:
        data = json.loads(result_json or "") if isinstance(result_json, str) else result_json
        return data.get("chapters", []) if isinstance(data, dict) else []
    except (json.JSONDecodeError, TypeError, ValueError):
        return []


def _safe_json_dumps(obj, default="{}"):
    try:
        return json.dumps(obj, ensure_ascii=False, indent=2)
    except (TypeError, ValueError):
        return default


class NovelQualityService:
    """Service for generating and managing novel draft quality check reports."""

    QUALITY_SYSTEM_PROMPT = """你是长篇小说正文质量检查助手。
你的任务是检查正文草稿的质量，生成结构化质量检查报告。
你只能检查质量，不能修改正文、不能润色、不能重写、不能替换内容。
你必须严格输出 JSON 格式的报告。"""

    @staticmethod
    def build_quality_report_prompt(
        db: Session, world_id: int, draft_id: int, request_data: Dict[str, Any]
    ) -> str:
        """Build prompt for quality check report generation."""
        from app.models import (
            Character, Faction, Location, WorldRule, HistoricalEvent,
            StyleProfile, PlotAnchor, ContextPackage,
        )

        draft = db.query(NovelDraft).filter_by(id=draft_id, world_id=world_id).first()
        if not draft:
            raise ValueError("正文草稿不存在")

        world = db.query(World).filter_by(id=world_id).first()

        # Chapter outline source
        chapter_outline = draft.chapter_outline

        # Volume outline (via chapter outline's volume)
        volume_outline = None
        if chapter_outline:
            volume_outline = db.query(NovelVolumeOutline).filter_by(
                world_id=world_id, volume_index=chapter_outline.volume_index, is_main=True
            ).first()

        # Novel evolution (mainline)
        main_evolution = db.query(SimulationRecord).filter_by(
            world_id=world_id, simulation_type="novel_evolution"
        ).order_by(SimulationRecord.created_at.desc()).first()

        # World settings
        characters = db.query(Character).filter_by(world_id=world_id).all()
        factions = db.query(Faction).filter_by(world_id=world_id).all()
        locations = db.query(Location).filter_by(world_id=world_id).all()
        rules = db.query(WorldRule).filter_by(world_id=world_id).all()
        events = db.query(HistoricalEvent).filter_by(world_id=world_id, is_canon=True).order_by(
            HistoricalEvent.created_at.desc()
        ).limit(30).all()

        # Style profile
        style_profile = draft.style_profile

        # Plot anchor
        plot_anchor = draft.plot_anchor

        # Context package
        context_package = draft.context_package

        # Build prompt sections
        parts = [NovelQualityService.QUALITY_SYSTEM_PROMPT, ""]

        # World overview
        if world:
            parts.append(f"## 世界概览")
            parts.append(f"名称: {world.name}")
            parts.append(f"类型: {world.world_type or '未指定'}")
            parts.append(f"当前纪元: {world.current_era or '未指定'}")
            parts.append(f"基调: {world.tone or '未指定'}")
            if world.description:
                parts.append(f"描述: {world.description[:500]}")
            parts.append("")

        # Draft content
        parts.append("## 正文草稿")
        parts.append(f"标题: {draft.title or draft.chapter_title or '未命名'}")
        parts.append(f"卷索引: {draft.volume_index}")
        parts.append(f"章索引: {draft.chapter_index}")
        if draft.notes:
            parts.append(f"备注: {draft.notes}")
        parts.append("")
        parts.append("### 正文内容")
        if draft.content:
            parts.append(draft.content[:5000])
        else:
            parts.append("（正文内容为空）")
        parts.append("")

        # Chapter outline
        if chapter_outline:
            parts.append("## 来源章节大纲")
            parts.append(f"卷: {chapter_outline.volume_title or '未命名'} (索引 {chapter_outline.volume_index})")
            chapters = _extract_chapters(chapter_outline.result_json)
            target_chapter = None
            for ch in chapters:
                if ch.get("chapter_index") == draft.chapter_index:
                    target_chapter = ch
                    break
            if target_chapter:
                parts.append(f"章目标: {target_chapter.get('chapter_goal', '未指定')}")
                parts.append(f"主要冲突: {target_chapter.get('main_conflict', '未指定')}")
                parts.append(f"剧情事件: {_safe_json_dumps(target_chapter.get('plot_events', []))}")
                parts.append(f"章末钩子: {target_chapter.get('ending_hook', '未指定')}")
            else:
                parts.append(f"(未找到章索引 {draft.chapter_index} 对应的章节方案)")
            parts.append("")

        # Volume outline
        if volume_outline:
            parts.append("## 来源分卷大纲")
            parts.append(f"卷目标: {volume_outline.volume_goal or '未指定'}")
            if volume_outline.result_json:
                parts.append(f"大纲: {volume_outline.result_json[:1000]}")
            parts.append("")

        # Novel evolution
        if main_evolution:
            parts.append("## 全书演化方案")
            if main_evolution.ai_response:
                parts.append(main_evolution.ai_response[:1500])
            parts.append("")

        # World settings
        parts.append("## 世界设定")

        if characters:
            parts.append("### 正式角色")
            for c in characters[:20]:
                parts.append(
                    f"- {c.name}: 身份={c.role or ''}, 性格={c.personality or ''}, "
                    f"目标={c.goal or ''}, 能力={c.abilities or ''}, 状态={c.current_status or ''}"
                )
            parts.append("")

        if factions:
            parts.append("### 正式势力")
            for f_item in factions[:10]:
                parts.append(
                    f"- {f_item.name}: 类型={f_item.faction_type or ''}, "
                    f"目标={f_item.goal or ''}, 资源={f_item.resources or ''}"
                )
            parts.append("")

        if locations:
            parts.append("### 正式地点")
            for l in locations[:10]:
                parts.append(f"- {l.name}: 类型={l.location_type or ''}, 区域={l.region or ''}")
            parts.append("")

        if rules:
            parts.append("### 正式规则")
            for r in rules[:15]:
                parts.append(f"- {r.name}: {r.content or ''}")
            parts.append("")

        if events:
            parts.append("### 最近正史事件")
            for e in events[:15]:
                parts.append(f"- {e.title or ''}: {e.content or ''}")
            parts.append("")

        # Style profile
        if style_profile:
            parts.append("## 写作风格方案")
            parts.append(f"名称: {style_profile.name}")
            if style_profile.description:
                parts.append(f"描述: {style_profile.description}")
            if style_profile.genre:
                parts.append(f"体裁: {style_profile.genre}")
            if style_profile.narrative_pov:
                parts.append(f"叙述视角: {style_profile.narrative_pov}")
            if style_profile.pacing:
                parts.append(f"节奏: {style_profile.pacing}")
            parts.append("")

        # Plot anchor
        if plot_anchor:
            parts.append("## 剧情时间点")
            parts.append(f"{plot_anchor.name}: 阶段={plot_anchor.stage or ''}")
            if plot_anchor.current_goal:
                parts.append(f"当前目标: {plot_anchor.current_goal}")
            if plot_anchor.next_goal:
                parts.append(f"下一目标: {plot_anchor.next_goal}")
            parts.append("")

        # Context package
        if context_package:
            parts.append("## 创作上下文包")
            parts.append(f"名称: {context_package.name or '未命名'}")
            if context_package.description:
                parts.append(f"描述: {context_package.description[:500]}")
            parts.append("")

        # User extra requirements
        extra_requirements = request_data.get("extra_requirements", "").strip()
        check_focus = request_data.get("check_focus", "").strip()

        parts.append("## 检查要求")
        parts.append("请对上述正文草稿进行全面质量检查，必须严格按以下格式输出 JSON。")
        parts.append("")
        parts.append("**重要规则：**")
        parts.append("1. 只能生成质量检查报告，不能修改正文。")
        parts.append("2. 不能润色正文。")
        parts.append("3. 不能重写正文。")
        parts.append("4. 不能覆盖正文草稿。")
        parts.append("5. 不能替换采用稿。")
        parts.append("6. 不能修改章节大纲。")
        parts.append("7. 不能修改世界设定。")
        parts.append("")

        if check_focus:
            parts.append(f"**用户指定检查重点**: {check_focus}")
            parts.append("")

        if extra_requirements:
            parts.append(f"**用户补充要求**: {extra_requirements}")
            parts.append("")

        parts.append("## 检查维度")
        parts.append("1. 章节大纲匹配度：正文是否完成章节目标、主要冲突、剧情事件、章末钩子。")
        parts.append("2. 世界设定一致性：是否违背世界规则、时间线、地点设定、力量体系。")
        parts.append("3. 人物一致性：角色行为是否符合人物设定、目标、状态、阵营关系。")
        parts.append("4. 剧情连贯性：因果是否清晰，事件推进是否顺畅。")
        parts.append("5. 节奏控制：是否过快、拖沓、信息堆砌或缺乏冲突。")
        parts.append("6. 文风一致性：是否符合风格方案或默认写作要求。")
        parts.append("7. 章末钩子：结尾是否有继续阅读动力。")
        parts.append("8. 可修改建议：给出可执行修改方向，但不直接重写正文。")
        parts.append("")

        parts.append("## 输出 JSON 格式")
        parts.append("""```json
{
  "title": "正文质量检查报告",
  "overall_score": 82,
  "summary": "整体评价（中文）",
  "scores": {
    "outline_alignment": 85,
    "world_consistency": 80,
    "character_consistency": 78,
    "plot_coherence": 84,
    "pacing": 76,
    "prose": 82,
    "ending_hook": 88
  },
  "strengths": ["优点1", "优点2"],
  "issues": [
    {
      "category": "章节目标偏离",
      "severity": "medium",
      "description": "问题说明",
      "evidence": "对应文本或概括",
      "suggestion": "修改建议（不要直接重写正文）"
    }
  ],
  "revision_suggestions": [
    {
      "priority": "high",
      "target": "开头 / 中段 / 结尾 / 人物 / 冲突 / 对话",
      "suggestion": "具体修改方向"
    }
  ],
  "risk_flags": ["可能与世界设定冲突"],
  "next_step": "建议下一步先加强主角行动动机"
}
```""")
        parts.append("")
        parts.append("请输出上述 JSON 格式的质量检查报告。只输出 JSON，不要有其他文字。")

        return "\n".join(parts)

    @staticmethod
    def generate_quality_report(
        db: Session, world_id: int, draft_id: int, request_data: Dict[str, Any]
    ) -> NovelDraftQualityReport:
        """Generate a quality check report via AI (or mock)."""
        from app.config import settings
        from app.services.settings_service import SettingsService

        prompt = NovelQualityService.build_quality_report_prompt(
            db, world_id, draft_id, request_data
        )

        config = SettingsService.get_effective_config(db)
        is_mock = not config.get("ai_enable_live") or config.get("ai_provider") == "mock"

        if is_mock:
            result_json, raw_text = NovelQualityService._mock_generate()
        else:
            from app.services.ai.model_router import get_client as get_ai_client
            try:
                ai_client = get_ai_client(db, task_type="simulation")
                raw_text = ai_client.generate(prompt=prompt, max_tokens=4000)
                result_json = NovelQualityService.parse_quality_report_response(raw_text)
            except Exception as e:
                raise RuntimeError(f"AI 生成质量报告失败: {str(e)}")

        report = NovelQualityService.save_quality_report(
            db, world_id, draft_id, prompt, result_json, raw_text
        )
        return report

    @staticmethod
    def _mock_generate() -> Tuple[str, str]:
        """Generate a stable mock quality report."""
        mock_data = {
            "title": "正文质量检查报告（Mock）",
            "overall_score": 82,
            "summary": "本作品整体质量良好，主角形象鲜明，情节推进有张力。部分对话节奏可优化，世界设定一致性需注意细节。",
            "scores": {
                "outline_alignment": 85,
                "world_consistency": 80,
                "character_consistency": 78,
                "plot_coherence": 84,
                "pacing": 76,
                "prose": 82,
                "ending_hook": 88,
            },
            "strengths": [
                "主角行动动机清晰，读者容易代入",
                "章末钩子设计巧妙，悬念感强",
                "世界设定细节丰富，氛围营造到位",
            ],
            "issues": [
                {
                    "category": "章节目标偏离",
                    "severity": "medium",
                    "description": "正文在中段偏离了章节目标中的主要冲突方向",
                    "evidence": "中段大段对话未推进核心冲突",
                    "suggestion": "建议将对话内容压缩，增加一个具体行动事件来推进冲突",
                },
                {
                    "category": "节奏控制",
                    "severity": "low",
                    "description": "开头信息释放偏慢，前两段都是环境描写",
                    "evidence": "开头仅环境描写，缺少人物行动",
                    "suggestion": "建议在第二段加入人物的具体动作或内心活动",
                },
                {
                    "category": "人物一致性",
                    "severity": "low",
                    "description": "主角在某段对话中语气与设定性格略有出入",
                    "evidence": "主角语气突然变得轻浮",
                    "suggestion": "建议统一主角语气，保持与设定一致",
                },
            ],
            "revision_suggestions": [
                {
                    "priority": "high",
                    "target": "中段",
                    "suggestion": "增加一个具体事件来推进核心冲突",
                },
                {
                    "priority": "medium",
                    "target": "开头",
                    "suggestion": "加快开头节奏，更早引入冲突",
                },
                {
                    "priority": "low",
                    "target": "对话",
                    "suggestion": "减少日常对话比例，增加有信息量的对白",
                },
            ],
            "risk_flags": [
                "部分设定细节可能与世界规则存在轻微矛盾，建议进一步核实",
            ],
            "next_step": "建议先修复章节目标偏离和节奏问题，再考虑语句润色。",
        }
        result_json = _safe_json_dumps(mock_data)
        return result_json, result_json

    @staticmethod
    def save_quality_report(
        db: Session,
        world_id: int,
        draft_id: int,
        prompt: str,
        result_json: str,
        raw_text: str = None,
    ) -> NovelDraftQualityReport:
        """Save a quality check report to the database."""
        draft = db.query(NovelDraft).filter_by(id=draft_id, world_id=world_id).first()
        if not draft:
            raise ValueError("正文草稿不存在")

        scores = NovelQualityService._extract_scores(result_json)

        report = NovelDraftQualityReport(
            world_id=world_id,
            draft_id=draft_id,
            chapter_outline_id=draft.chapter_outline_id,
            volume_index=draft.volume_index or 0,
            chapter_index=draft.chapter_index or 0,
            title=scores.get("title", "正文质量检查报告"),
            prompt=prompt,
            result_json=result_json,
            raw_text=raw_text or result_json,
            overall_score=scores.get("overall_score", 0),
            outline_alignment_score=scores.get("outline_alignment_score", 0),
            world_consistency_score=scores.get("world_consistency_score", 0),
            character_consistency_score=scores.get("character_consistency_score", 0),
            plot_coherence_score=scores.get("plot_coherence_score", 0),
            pacing_score=scores.get("pacing_score", 0),
            prose_score=scores.get("prose_score", 0),
            hook_score=scores.get("hook_score", 0),
            status="candidate",
            is_current=False,
            created_at=_utcnow(),
            updated_at=_utcnow(),
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report

    @staticmethod
    def _extract_scores(result_json: str) -> dict:
        """Extract scores and title from result JSON."""
        result = {"title": "正文质量检查报告"}
        try:
            data = json.loads(result_json) if isinstance(result_json, str) else result_json
            if isinstance(data, dict):
                result["title"] = data.get("title", result["title"])
                result["overall_score"] = data.get("overall_score", 0)
                scores = data.get("scores", {})
                if isinstance(scores, dict):
                    result["outline_alignment_score"] = scores.get("outline_alignment", 0)
                    result["world_consistency_score"] = scores.get("world_consistency", 0)
                    result["character_consistency_score"] = scores.get("character_consistency", 0)
                    result["plot_coherence_score"] = scores.get("plot_coherence", 0)
                    result["pacing_score"] = scores.get("pacing", 0)
                    result["prose_score"] = scores.get("prose", 0)
                    result["hook_score"] = scores.get("ending_hook", 0)
        except (json.JSONDecodeError, TypeError, ValueError):
            pass
        return result

    @staticmethod
    def parse_quality_report_response(raw_text: str) -> str:
        """Parse AI response into a JSON string. Falls back gracefully."""
        if not raw_text:
            return _safe_json_dumps({"parse_warning": "AI 未返回内容", "raw_text": ""})

        # Try to extract JSON from code blocks
        json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', raw_text, re.DOTALL)
        if json_match:
            candidate = json_match.group(1).strip()
            try:
                json.loads(candidate)
                return candidate
            except json.JSONDecodeError:
                pass

        # Try direct JSON parse
        try:
            json.loads(raw_text)
            return raw_text
        except json.JSONDecodeError:
            pass

        # Fallback: wrap raw text
        return _safe_json_dumps({
            "parse_warning": "AI 返回格式非 JSON，已保存原始文本",
            "title": "正文质量检查报告（原始）",
            "raw_text": raw_text[:5000],
            "overall_score": 0,
            "summary": "AI 返回非标准 JSON 格式，请查看原始文本。",
            "scores": {},
            "strengths": [],
            "issues": [],
            "revision_suggestions": [],
            "risk_flags": ["AI 返回格式异常"],
            "next_step": "请人工检查原始文本。",
        })

    @staticmethod
    def list_quality_reports(
        db: Session, world_id: int, draft_id: int = None
    ) -> List[NovelDraftQualityReport]:
        """List quality reports for a world, optionally filtered by draft."""
        q = db.query(NovelDraftQualityReport).filter_by(world_id=world_id)
        if draft_id is not None:
            q = q.filter_by(draft_id=draft_id)
        return q.order_by(NovelDraftQualityReport.created_at.desc()).all()

    @staticmethod
    def get_quality_report(
        db: Session, world_id: int, report_id: int
    ) -> Optional[NovelDraftQualityReport]:
        """Get a quality report, ensuring it belongs to the given world."""
        return db.query(NovelDraftQualityReport).filter_by(
            id=report_id, world_id=world_id
        ).first()

    @staticmethod
    def set_current_quality_report(
        db: Session, world_id: int, report_id: int
    ) -> NovelDraftQualityReport:
        """Mark a report as the current reference, unmarking others for the same draft."""
        report = NovelQualityService.get_quality_report(db, world_id, report_id)
        if not report:
            raise ValueError("报告不存在")
        if report.status == "discarded":
            raise ValueError("已废弃的报告不能设为当前参考报告")

        # Unset any existing current report for the same draft
        db.query(NovelDraftQualityReport).filter_by(
            draft_id=report.draft_id, is_current=True
        ).update({"is_current": False, "updated_at": _utcnow()})

        # Set this one as current
        report.is_current = True
        report.status = "current"
        report.confirmed_at = _utcnow()
        report.updated_at = _utcnow()
        db.commit()
        db.refresh(report)
        return report

    @staticmethod
    def discard_quality_report(
        db: Session, world_id: int, report_id: int
    ) -> NovelDraftQualityReport:
        """Discard a quality report."""
        report = NovelQualityService.get_quality_report(db, world_id, report_id)
        if not report:
            raise ValueError("报告不存在")

        report.status = "discarded"
        report.is_current = False
        report.updated_at = _utcnow()
        db.commit()
        db.refresh(report)
        return report
