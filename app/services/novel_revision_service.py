"""
AI World Engine - Novel Revision Service
v2.2.0: Builds prompts, generates polished revision candidates for novel drafts.
Only generates revision candidates — never overwrites original drafts.
"""

import json
import re
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session

from app.models import NovelDraft, NovelDraftRevision, NovelDraftQualityReport, World


def _utcnow():
    return datetime.now(timezone.utc)


def _safe_json_dumps(obj, default="{}"):
    try:
        return json.dumps(obj, ensure_ascii=False, indent=2)
    except (TypeError, ValueError):
        return default


class NovelRevisionService:
    """Service for generating and managing polished revision candidates."""

    REVISION_SYSTEM_PROMPT = """你是长篇小说正文润色助手。
你的任务是基于质量检查报告和原正文草稿，生成润色后的单章候选稿。
你只能生成润色候选稿，不能覆盖原正文、不能自动替换采用稿、不能修改世界设定。
必须优先修复质量检查报告中指出的问题，保留原章节目标和核心剧情事件。"""

    @staticmethod
    def build_revision_prompt(
        db: Session, world_id: int, draft_id: int, quality_report_id: int,
        request_data: Dict[str, Any]
    ) -> str:
        """Build prompt for revision candidate generation."""
        from app.models import (
            Character, Faction, Location, WorldRule, HistoricalEvent,
            NovelChapterOutline, NovelVolumeOutline, SimulationRecord,
            StyleProfile, PlotAnchor, ContextPackage,
        )

        draft = db.query(NovelDraft).filter_by(id=draft_id, world_id=world_id).first()
        if not draft:
            raise ValueError("正文草稿不存在")

        quality_report = db.query(NovelDraftQualityReport).filter_by(
            id=quality_report_id, world_id=world_id
        ).first()

        world = db.query(World).filter_by(id=world_id).first()
        chapter_outline = draft.chapter_outline
        style_profile = draft.style_profile

        # Parse quality report
        parsed_report = {}
        if quality_report and quality_report.result_json:
            try:
                parsed_report = json.loads(quality_report.result_json)
            except (json.JSONDecodeError, TypeError):
                parsed_report = {}

        parts = [NovelRevisionService.REVISION_SYSTEM_PROMPT, ""]

        # World overview
        if world:
            parts.append(f"## 世界: {world.name} | 类型: {world.world_type or ''} | 纪元: {world.current_era or ''} | 基调: {world.tone or ''}")
        parts.append("")

        # Original draft
        parts.append("## 原正文草稿")
        parts.append(f"标题: {draft.title or draft.chapter_title or '未命名'}")
        parts.append(f"卷{ draft.volume_index} 章{draft.chapter_index}")
        if draft.content:
            parts.append(draft.content[:5000])
        else:
            parts.append("（正文为空）")
        parts.append("")

        # Quality report summary
        if quality_report:
            parts.append("## 质量检查报告摘要")
            parts.append(f"综合评分: {quality_report.overall_score}")
            if parsed_report.get("summary"):
                parts.append(f"整体评价: {parsed_report['summary']}")
            parts.append("")
        else:
            parts.append("## 质量检查报告")
            parts.append("（未提供质量检查报告，将基于原正文进行通用润色）")
            parts.append("")

        # Issues from report
        issues = parsed_report.get("issues", [])
        if issues:
            parts.append("## 需要修复的问题")
            for i, issue in enumerate(issues, 1):
                sev = issue.get("severity", "medium")
                parts.append(f"{i}. [{sev}] {issue.get('category', '')}: {issue.get('description', '')}")
                if issue.get("suggestion"):
                    parts.append(f"   建议: {issue['suggestion']}")
            parts.append("")

        # Revision suggestions
        suggestions = parsed_report.get("revision_suggestions", [])
        if suggestions:
            parts.append("## 修改建议（优先执行高优先级）")
            for s in suggestions:
                prio = s.get("priority", "medium")
                target = s.get("target", "")
                sug = s.get("suggestion", "")
                parts.append(f"- [{prio}] {target}: {sug}")
            parts.append("")

        # Risk flags
        risks = parsed_report.get("risk_flags", [])
        if risks:
            parts.append("## 风险提示")
            for r in risks:
                parts.append(f"- ⚠️ {r}")
            parts.append("")

        # Chapter outline
        if chapter_outline:
            parts.append("## 章节目标（必须保留）")
            parts.append(f"卷: {chapter_outline.volume_title or ''} 章目标: 请保持与章节大纲一致")
            parts.append("")

        # Style profile
        if style_profile:
            parts.append(f"## 写作风格: {style_profile.name}")
            if style_profile.genre:
                parts.append(f"体裁: {style_profile.genre}")
            if style_profile.pacing:
                parts.append(f"节奏: {style_profile.pacing}")
            parts.append("")

        # Extra requirements
        extra = request_data.get("extra_requirements", "").strip()
        if extra:
            parts.append(f"## 用户补充要求: {extra}")
            parts.append("")

        # Output instructions
        parts.append("## 输出要求")
        parts.append("只生成润色后的单章候选稿。")
        parts.append("必须优先修复质量检查报告中 high priority 的问题。")
        parts.append("必须保留原章节目标和核心剧情事件。")
        parts.append("必须保留或加强章末钩子。")
        parts.append("必须增强人物动机和冲突推进。")
        parts.append("必须优化节奏和信息释放。")
        parts.append("必须尊重世界设定和已确认正史。")
        parts.append("不能覆盖原正文草稿。")
        parts.append("不能自动替换采用稿。")
        parts.append("不能生成下一章或整卷内容。")
        parts.append("不能复制现成作品文本。")
        parts.append("输出格式：")
        parts.append("标题: [润色后标题]")
        parts.append("润色正文:")
        parts.append("[正文内容]")
        parts.append("润色说明:")
        parts.append("[列出主要修改内容]")

        return "\n".join(parts)

    @staticmethod
    def generate_revision(
        db: Session, world_id: int, draft_id: int, quality_report_id: int,
        request_data: Dict[str, Any]
    ) -> NovelDraftRevision:
        """Generate a revision candidate via AI (or mock)."""
        from app.config import settings
        from app.services.settings_service import SettingsService

        draft = db.query(NovelDraft).filter_by(id=draft_id, world_id=world_id).first()
        if not draft:
            raise ValueError("正文草稿不存在")

        prompt = NovelRevisionService.build_revision_prompt(
            db, world_id, draft_id, quality_report_id, request_data
        )

        config = SettingsService.get_effective_config(db)
        is_mock = not config.get("ai_enable_live") or config.get("ai_provider") == "mock"

        if is_mock:
            content, raw_text, revision_summary = NovelRevisionService._mock_generate(draft)
        else:
            from app.services.ai.model_router import get_client as get_ai_client
            try:
                ai_client = get_ai_client(db, task_type="simulation")
                raw_text = ai_client.generate(prompt=prompt, max_tokens=4000)
                content = NovelRevisionService.extract_revision_content(raw_text)
                revision_summary = NovelRevisionService._extract_summary(raw_text)
            except Exception as e:
                raise RuntimeError(f"AI 生成润色候选失败: {str(e)}")

        revision = NovelRevisionService.save_revision(
            db, world_id, draft_id, quality_report_id, prompt, content, raw_text,
            revision_summary, request_data
        )
        return revision

    @staticmethod
    def _mock_generate(draft) -> Tuple[str, str, str]:
        """Generate stable mock revision content."""
        original_title = draft.title or draft.chapter_title or "未命名"
        revised_title = f"{original_title}（润色稿）"

        revision_content = f"""夜幕降临，星光如碎银般洒落在古老的石阶上。

{original_title[:20] if original_title else '主角'}深吸一口气，握紧了手中的武器。这一次，他不再犹豫。记忆中那些失败的片段如潮水般涌来，但此刻他的眼神比任何时候都要坚定。

"我必须前进。"他低声说道，声音里带着不可动摇的决心。

前方的道路依然危险重重。暗影在角落中蠢蠢欲动，古老的机关随时可能触发。但他已经做好了准备——不仅是手中的武器，更重要的是心中的信念。

突然，一阵沉重的脚步声从前方传来。一个巨大的黑影缓缓浮现，地面的石板随之震颤。他握紧武器，调整呼吸，盯着那个越来越近的身影。

这就是他必须面对的命运。

战斗在一瞬间爆发。他灵活地闪避，借力打力，每一次攻击都精准而致命。随着最后一击落下，黑影轰然倒地，化作点点光芒消散在空气中。

他喘着粗气，看着逐渐恢复平静的空间。成功了。但更大的挑战还在后面。

他抬起头，朝着下一个目标走去。这一次，他不再回头。"""

        revision_summary = """润色说明：
1. 增强了主角的内心动机描写，明确了行动驱动力
2. 优化了战斗节奏，从铺垫到爆发的过渡更自然
3. 加强了章末钩子，暗示后续挑战
4. 修正了原文中略显拖沓的描述部分
5. 保留了原章节核心事件和人物设定"""

        return revision_content, revision_content, revision_summary

    @staticmethod
    def extract_revision_content(raw_text: str) -> str:
        """Extract the revision body from raw AI response."""
        if not raw_text:
            return ""
        # Try to extract content after "润色正文:" marker
        match = re.search(r'润色正文[：:]\s*\n?(.*?)(?:润色说明|$)', raw_text, re.DOTALL)
        if match:
            return match.group(1).strip()
        # If no marker, try to find content after title
        match = re.search(r'标题[：:][^\n]*\n+(.*?)(?:润色说明|$)', raw_text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return raw_text.strip()

    @staticmethod
    def _extract_summary(raw_text: str) -> str:
        """Extract revision summary from raw response."""
        match = re.search(r'润色说明[：:]\s*\n?(.*?)$', raw_text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""

    @staticmethod
    def save_revision(
        db: Session, world_id: int, draft_id: int, quality_report_id: int,
        prompt: str, content: str, raw_text: str = None,
        revision_summary: str = "", request_data: Dict = None
    ) -> NovelDraftRevision:
        """Save a revision candidate to the database."""
        draft = db.query(NovelDraft).filter_by(id=draft_id, world_id=world_id).first()
        if not draft:
            raise ValueError("正文草稿不存在")

        word_count = len(content.replace(" ", "").replace("\n", "")) if content else 0

        revision = NovelDraftRevision(
            world_id=world_id,
            draft_id=draft_id,
            quality_report_id=quality_report_id,
            chapter_outline_id=draft.chapter_outline_id,
            volume_index=draft.volume_index or 0,
            chapter_index=draft.chapter_index or 0,
            title=f"{draft.title or draft.chapter_title or '未命名'}（润色稿）",
            original_title=draft.title or draft.chapter_title or "",
            original_content_snapshot=(draft.content or "")[:2000],
            prompt=prompt,
            content=content,
            raw_text=raw_text or content,
            word_count=word_count,
            revision_summary=revision_summary,
            applied_suggestions_json=_safe_json_dumps(request_data or {}),
            status="candidate",
            is_accepted=False,
            created_at=_utcnow(),
            updated_at=_utcnow(),
        )
        db.add(revision)
        db.commit()
        db.refresh(revision)
        return revision

    @staticmethod
    def list_revisions(
        db: Session, world_id: int, draft_id: int = None
    ) -> List[NovelDraftRevision]:
        """List revisions for a world, optionally filtered by draft."""
        q = db.query(NovelDraftRevision).filter_by(world_id=world_id)
        if draft_id is not None:
            q = q.filter_by(draft_id=draft_id)
        return q.order_by(NovelDraftRevision.created_at.desc()).all()

    @staticmethod
    def get_revision(
        db: Session, world_id: int, revision_id: int
    ) -> Optional[NovelDraftRevision]:
        """Get a revision, ensuring it belongs to the given world."""
        return db.query(NovelDraftRevision).filter_by(
            id=revision_id, world_id=world_id
        ).first()

    @staticmethod
    def set_accepted_revision(
        db: Session, world_id: int, revision_id: int
    ) -> NovelDraftRevision:
        """Mark a revision as accepted, unmarking others for the same draft."""
        revision = NovelRevisionService.get_revision(db, world_id, revision_id)
        if not revision:
            raise ValueError("润色候选不存在")
        if revision.status == "discarded":
            raise ValueError("已废弃的润色稿不能设为采用润色稿")

        # Unset existing accepted for same draft
        db.query(NovelDraftRevision).filter_by(
            draft_id=revision.draft_id, is_accepted=True
        ).update({"is_accepted": False, "status": "candidate", "updated_at": _utcnow()})

        revision.is_accepted = True
        revision.status = "accepted"
        revision.accepted_at = _utcnow()
        revision.updated_at = _utcnow()
        db.commit()
        db.refresh(revision)
        return revision

    @staticmethod
    def discard_revision(
        db: Session, world_id: int, revision_id: int
    ) -> NovelDraftRevision:
        """Discard a revision."""
        revision = NovelRevisionService.get_revision(db, world_id, revision_id)
        if not revision:
            raise ValueError("润色候选不存在")

        revision.status = "discarded"
        revision.is_accepted = False
        revision.updated_at = _utcnow()
        db.commit()
        db.refresh(revision)
        return revision

    @staticmethod
    def update_revision(
        db: Session, world_id: int, revision_id: int, edited_data: Dict[str, Any]
    ) -> NovelDraftRevision:
        """Update a revision (title, content, summary)."""
        revision = NovelRevisionService.get_revision(db, world_id, revision_id)
        if not revision:
            raise ValueError("润色候选不存在")
        if revision.status == "discarded":
            raise ValueError("已废弃的润色稿不能编辑")

        if "title" in edited_data:
            revision.title = edited_data["title"]
        if "content" in edited_data:
            revision.content = edited_data["content"]
            revision.word_count = len(edited_data["content"].replace(" ", "").replace("\n", ""))
        if "revision_summary" in edited_data:
            revision.revision_summary = edited_data["revision_summary"]
        revision.updated_at = _utcnow()
        db.commit()
        db.refresh(revision)
        return revision
