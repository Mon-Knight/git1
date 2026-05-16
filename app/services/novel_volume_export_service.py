"""
AI World Engine - Novel Volume Export Service
v2.6.0: Volume-level manuscript management and export (TXT/Markdown/JSON).
Does NOT generate new content, modify drafts, or auto-fix missing chapters.
"""

import json
import os
import re
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from pathlib import Path

from app.models import NovelVolumeExport


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class NovelVolumeExportService:
    """Service for volume manuscript management and export."""

    @staticmethod
    def get_export_directory() -> str:
        """Get the export directory. Creates if not exists."""
        import sys
        if getattr(sys, 'frozen', False):
            base = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
            export_dir = os.path.join(base, 'AIWorldEngine', 'exports')
        else:
            export_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'exports')
        os.makedirs(export_dir, exist_ok=True)
        return export_dir

    @staticmethod
    def safe_filename(name: str) -> str:
        """Sanitize filename, removing illegal characters."""
        return re.sub(r'[\\/:*?"<>|]', '_', name)

    @staticmethod
    def build_volume_manuscript_context(
        db: Session, world_id: int, volume_id_or_index: Any
    ) -> Dict[str, Any]:
        """Build context for a volume's manuscript management."""
        from app.models import (
            World, NovelVolumeOutline, NovelChapterOutline,
            NovelDraft, NovelFinalDraft, NovelDraftRevision,
            NovelDraftQualityReport,
        )

        world = db.query(World).filter(World.id == world_id).first()
        if not world:
            return {"ok": False, "error": "世界不存在"}

        # Find volume
        if isinstance(volume_id_or_index, int) and volume_id_or_index > 100:
            volume = db.query(NovelVolumeOutline).filter(
                NovelVolumeOutline.id == volume_id_or_index,
                NovelVolumeOutline.world_id == world_id
            ).first()
        else:
            volume = db.query(NovelVolumeOutline).filter(
                NovelVolumeOutline.world_id == world_id
            ).order_by(NovelVolumeOutline.id).offset(
                (volume_id_or_index or 1) - 1 if isinstance(volume_id_or_index, int) else 0
            ).first()

        if not volume:
            return {"ok": False, "error": "分卷不存在"}

        # Get chapters
        chapters = db.query(NovelChapterOutline).filter(
            NovelChapterOutline.volume_outline_id == volume.id,
            NovelChapterOutline.is_main == True
        ).order_by(NovelChapterOutline.id).all()

        chapter_statuses = []
        total_word_count = 0
        final_draft_count = 0
        fallback_count = 0
        missing_count = 0

        for ch in chapters:
            text = None
            source_type = "none"
            word_count = 0
            has_final = False
            has_quality = False

            # Check final draft
            fd = db.query(NovelFinalDraft).filter(
                NovelFinalDraft.chapter_outline_id == ch.id,
                NovelFinalDraft.is_active == True
            ).first()
            if fd and fd.content_snapshot:
                text = fd.content_snapshot
                source_type = "final_draft"
                word_count = len(text)
                has_final = True

            # Check accepted revision
            if not text:
                rev = db.query(NovelDraftRevision).filter(
                    NovelDraftRevision.chapter_outline_id == ch.id,
                    NovelDraftRevision.status == "accepted"
                ).first()
                if rev and rev.content:
                    text = rev.content
                    source_type = "revision_accepted"
                    word_count = len(text)

            # Check accepted draft
            if not text:
                draft = db.query(NovelDraft).filter(
                    NovelDraft.chapter_outline_id == ch.id,
                    NovelDraft.is_accepted == True
                ).first()
                if draft and draft.content:
                    text = draft.content
                    source_type = "draft_accepted"
                    word_count = len(text)

            # Check raw draft
            if not text:
                draft = db.query(NovelDraft).filter(
                    NovelDraft.chapter_outline_id == ch.id
                ).order_by(NovelDraft.created_at.desc()).first()
                if draft and draft.content:
                    text = draft.content
                    source_type = "draft_only"
                    word_count = len(text)

            # Quality check
            qr = db.query(NovelDraftQualityReport).filter(
                NovelDraftQualityReport.chapter_outline_id == ch.id
            ).first()
            has_quality = qr is not None

            if has_final:
                final_draft_count += 1
            elif text and not has_final:
                fallback_count += 1
            else:
                missing_count += 1

            total_word_count += word_count

            chapter_statuses.append({
                "chapter_id": ch.id,
                "chapter_title": ch.title or f"章节{ch.id}",
                "source_type": source_type,
                "word_count": word_count,
                "has_text": text is not None,
                "has_final": has_final,
                "has_quality": has_quality,
                "text": text,
            })

        return {
            "ok": True,
            "world": {"id": world.id, "name": world.name},
            "volume": {
                "id": volume.id,
                "title": volume.title or f"第{volume.id}卷",
                "volume_count": volume.volume_count or 0,
            },
            "chapters": chapter_statuses,
            "summary": {
                "chapter_count": len(chapters),
                "final_draft_count": final_draft_count,
                "fallback_count": fallback_count,
                "missing_count": missing_count,
                "word_count": total_word_count,
            },
        }

    @staticmethod
    def get_chapter_export_text(
        db: Session, world_id: int, chapter_outline_id: int
    ) -> Dict[str, Any]:
        """Get export-ready text for a chapter following priority rules."""
        from app.models import NovelFinalDraft, NovelDraftRevision, NovelDraft

        # Priority 1: Final draft
        fd = db.query(NovelFinalDraft).filter(
            NovelFinalDraft.chapter_outline_id == chapter_outline_id,
            NovelFinalDraft.is_active == True
        ).first()
        if fd and fd.content_snapshot:
            return {"text": fd.content_snapshot, "source": "final_draft", "ok": True}

        # Priority 2: Accepted revision
        rev = db.query(NovelDraftRevision).filter(
            NovelDraftRevision.chapter_outline_id == chapter_outline_id,
            NovelDraftRevision.status == "accepted"
        ).first()
        if rev and rev.content:
            return {"text": rev.content, "source": "revision_accepted", "ok": True}

        # Priority 3+4: Draft
        draft = db.query(NovelDraft).filter(
            NovelDraft.chapter_outline_id == chapter_outline_id,
            NovelDraft.is_accepted == True
        ).first()
        if not draft:
            draft = db.query(NovelDraft).filter(
                NovelDraft.chapter_outline_id == chapter_outline_id
            ).order_by(NovelDraft.created_at.desc()).first()

        if draft and draft.content:
            source = "draft_accepted" if draft.is_accepted else "draft_only"
            return {"text": draft.content, "source": source, "ok": True}

        return {"text": None, "source": "none", "ok": False}

    @staticmethod
    def build_volume_preview(
        db: Session, world_id: int, volume_id_or_index: Any
    ) -> Dict[str, Any]:
        """Build volume manuscript preview."""
        context = NovelVolumeExportService.build_volume_manuscript_context(
            db, world_id, volume_id_or_index
        )
        return context

    @staticmethod
    def _generate_export_filename(world_name: str, volume_title: str, fmt: str) -> str:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_world = NovelVolumeExportService.safe_filename(world_name)
        safe_volume = NovelVolumeExportService.safe_filename(volume_title)
        return f"{safe_world}_{safe_volume}_{ts}.{fmt}"

    @staticmethod
    def export_volume_txt(
        db: Session, world_id: int, volume_id_or_index: Any,
        options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Export volume as TXT."""
        options = options or {}
        ctx = NovelVolumeExportService.build_volume_manuscript_context(db, world_id, volume_id_or_index)
        if not ctx.get("ok"):
            return ctx

        include_missing = options.get("include_missing_placeholders", True)
        lines = [f"{ctx['volume']['title']}\n"]

        for ch in ctx["chapters"]:
            lines.append(f"第{ch['chapter_id']}章 {ch['chapter_title']}\n")
            if ch["text"]:
                lines.append(ch["text"])
                lines.append("")
            elif include_missing:
                lines.append("【本章暂无最终正文，当前仅有章节大纲或正文缺失。】\n")

        content = "\n".join(lines)
        return NovelVolumeExportService._write_export_file(
            db, world_id, volume_id_or_index, ctx, content, "txt", options
        )

    @staticmethod
    def export_volume_markdown(
        db: Session, world_id: int, volume_id_or_index: Any,
        options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Export volume as Markdown."""
        options = options or {}
        ctx = NovelVolumeExportService.build_volume_manuscript_context(db, world_id, volume_id_or_index)
        if not ctx.get("ok"):
            return ctx

        include_missing = options.get("include_missing_placeholders", True)
        lines = [f"# {ctx['volume']['title']}\n"]

        for ch in ctx["chapters"]:
            lines.append(f"## 第{ch['chapter_id']}章 {ch['chapter_title']}\n")
            if ch["text"]:
                lines.append(ch["text"])
                lines.append("")
            elif include_missing:
                lines.append("> 【本章暂无最终正文，当前仅有章节大纲或正文缺失。】\n")

        content = "\n".join(lines)
        return NovelVolumeExportService._write_export_file(
            db, world_id, volume_id_or_index, ctx, content, "markdown", options
        )

    @staticmethod
    def export_volume_json(
        db: Session, world_id: int, volume_id_or_index: Any,
        options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Export volume as JSON."""
        options = options or {}
        ctx = NovelVolumeExportService.build_volume_manuscript_context(db, world_id, volume_id_or_index)
        if not ctx.get("ok"):
            return ctx

        data = {
            "world": ctx["world"],
            "volume": ctx["volume"],
            "summary": ctx["summary"],
            "chapters": [
                {
                    "chapter_id": ch["chapter_id"],
                    "title": ch["chapter_title"],
                    "source_type": ch["source_type"],
                    "word_count": ch["word_count"],
                    "content": ch["text"] or "",
                }
                for ch in ctx["chapters"]
            ],
        }

        content = json.dumps(data, ensure_ascii=False, indent=2)
        return NovelVolumeExportService._write_export_file(
            db, world_id, volume_id_or_index, ctx, content, "json", options
        )

    @staticmethod
    def _write_export_file(
        db: Session, world_id: int, volume_id_or_index: Any,
        ctx: Dict[str, Any], content: str, fmt: str, options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Write content to export file and save record."""
        try:
            export_dir = NovelVolumeExportService.get_export_directory()
            fname = NovelVolumeExportService._generate_export_filename(
                ctx["world"]["name"], ctx["volume"]["title"], fmt
            )
            fpath = os.path.join(export_dir, fname)
            # Avoid overwriting
            if os.path.exists(fpath):
                base, ext = os.path.splitext(fname)
                ts = datetime.now().strftime("%H%M%S")
                fname = f"{base}_{ts}{ext}"
                fpath = os.path.join(export_dir, fname)

            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(content)

            # Save export record
            volume_id = None
            if isinstance(volume_id_or_index, int) and volume_id_or_index > 100:
                volume_id = volume_id_or_index

            record = NovelVolumeExport(
                world_id=world_id,
                volume_outline_id=volume_id,
                volume_index=ctx["volume"].get("volume_count", 0) or 0,
                title=ctx["volume"]["title"],
                export_format=fmt,
                file_name=fname,
                file_path=fpath,
                chapter_count=ctx["summary"]["chapter_count"],
                final_draft_count=ctx["summary"]["final_draft_count"],
                fallback_count=ctx["summary"]["fallback_count"],
                missing_count=ctx["summary"]["missing_count"],
                word_count=ctx["summary"]["word_count"],
                source_summary_json=json.dumps([
                    {"chapter_id": ch["chapter_id"], "source": ch["source_type"]}
                    for ch in ctx["chapters"]
                ], ensure_ascii=False),
                export_options_json=json.dumps(options, ensure_ascii=False),
                status="completed",
            )
            db.add(record)
            db.commit()
            db.refresh(record)

            return {
                "ok": True,
                "export_id": record.id,
                "file_name": fname,
                "file_path": fpath,
                "format": fmt,
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @staticmethod
    def save_volume_export_record(
        db: Session, world_id: int, export_result: Dict[str, Any]
    ) -> Optional[NovelVolumeExport]:
        """Save an export record."""
        pass  # Handled in _write_export_file

    @staticmethod
    def list_volume_exports(db: Session, world_id: int) -> List[NovelVolumeExport]:
        """List export records for a world."""
        return (
            db.query(NovelVolumeExport)
            .filter(NovelVolumeExport.world_id == world_id)
            .order_by(NovelVolumeExport.created_at.desc())
            .all()
        )

    @staticmethod
    def get_volume_export(
        db: Session, world_id: int, export_id: int
    ) -> Optional[NovelVolumeExport]:
        """Get an export record with world ownership check."""
        return (
            db.query(NovelVolumeExport)
            .filter(
                NovelVolumeExport.id == export_id,
                NovelVolumeExport.world_id == world_id,
            )
            .first()
        )
