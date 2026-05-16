"""
AI World Engine - Novel Version Service
v2.3.0: Version comparison and final draft management.
No AI calls — purely management and difflib-based comparison.
"""

import difflib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session

from app.models import (
    NovelDraft, NovelDraftRevision, NovelFinalDraft,
)


def _utcnow():
    return datetime.now(timezone.utc)


class NovelVersionService:
    """Service for text version management and final draft adoption."""

    @staticmethod
    def list_text_versions(db: Session, world_id: int, draft_id: int) -> List[Dict]:
        """List all comparable versions for a draft."""
        draft = db.query(NovelDraft).filter_by(id=draft_id, world_id=world_id).first()
        if not draft:
            return []

        versions = []

        # 1. Original draft
        versions.append({
            "version_type": "draft",
            "source_id": draft.id,
            "title": draft.title or draft.chapter_title or "(无标题)",
            "content": draft.content or "",
            "word_count": draft.word_count or 0,
            "status": draft.status,
            "is_accepted": draft.is_accepted,
            "label": {"candidate": "原始正文草稿", "accepted": "正文采用稿", "discarded": "已废弃正文草稿"}.get(draft.status, draft.status),
            "created_at": draft.created_at,
            "can_be_final": draft.status != "discarded",
        })

        # 2. Revision candidates
        revisions = db.query(NovelDraftRevision).filter_by(
            draft_id=draft_id, world_id=world_id
        ).order_by(NovelDraftRevision.created_at.desc()).all()

        for rev in revisions:
            versions.append({
                "version_type": "revision",
                "source_id": rev.id,
                "title": rev.title or "(无标题)",
                "content": rev.content or "",
                "word_count": rev.word_count or 0,
                "status": rev.status,
                "is_accepted": rev.is_accepted,
                "label": {"candidate": "润色候选稿", "accepted": "采用润色稿", "discarded": "已废弃润色稿"}.get(rev.status, rev.status),
                "created_at": rev.created_at,
                "can_be_final": rev.status != "discarded",
            })

        return versions

    @staticmethod
    def get_text_version(
        db: Session, world_id: int, draft_id: int, source_type: str, source_id: int
    ) -> Optional[Dict]:
        """Get a specific version's content by source type and id."""
        if source_type == "draft":
            draft = db.query(NovelDraft).filter_by(
                id=source_id, world_id=world_id
            ).first()
            if draft and draft.id == draft_id:
                return {
                    "version_type": "draft", "source_id": draft.id,
                    "title": draft.title or "", "content": draft.content or "",
                    "word_count": draft.word_count or 0, "status": draft.status,
                }
        elif source_type == "revision":
            rev = db.query(NovelDraftRevision).filter_by(
                id=source_id, world_id=world_id, draft_id=draft_id
            ).first()
            if rev:
                return {
                    "version_type": "revision", "source_id": rev.id,
                    "title": rev.title or "", "content": rev.content or "",
                    "word_count": rev.word_count or 0, "status": rev.status,
                }
        return None

    @staticmethod
    def compare_text_versions(
        db: Session, world_id: int, draft_id: int,
        left_type: str, left_id: int, right_type: str, right_id: int
    ) -> Dict:
        """Compare two text versions and return diff results."""
        left = NovelVersionService.get_text_version(
            db, world_id, draft_id, left_type, left_id
        )
        right = NovelVersionService.get_text_version(
            db, world_id, draft_id, right_type, right_id
        )

        if not left or not right:
            return {"error": "版本不存在"}

        left_text = left.get("content", "")
        right_text = right.get("content", "")
        left_lines = left_text.splitlines(keepends=True)
        right_lines = right_text.splitlines(keepends=True)

        # Similarity
        matcher = difflib.SequenceMatcher(None, left_text, right_text)
        similarity = round(matcher.ratio() * 100, 1)

        # Diff blocks
        diff_blocks = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                block_text = left_text[i1:i2]
                if len(block_text) > 200:
                    block_text = block_text[:200] + "..."
                diff_blocks.append({"type": "same", "text": block_text})
            elif tag == "replace":
                diff_blocks.append({"type": "removed", "text": left_text[i1:i2][:300]})
                diff_blocks.append({"type": "added", "text": right_text[j1:j2][:300]})
            elif tag == "delete":
                diff_blocks.append({"type": "removed", "text": left_text[i1:i2][:300]})
            elif tag == "insert":
                diff_blocks.append({"type": "added", "text": right_text[j1:j2][:300]})

        return {
            "left_title": left.get("title", ""),
            "right_title": right.get("title", ""),
            "left_word_count": left.get("word_count", 0),
            "right_word_count": right.get("word_count", 0),
            "word_count_delta": right.get("word_count", 0) - left.get("word_count", 0),
            "same_title": left.get("title") == right.get("title"),
            "same_content": left_text == right_text,
            "similarity": similarity,
            "diff_blocks": diff_blocks,
            "left_type": left_type,
            "right_type": right_type,
            "left_status": left.get("status", ""),
            "right_status": right.get("status", ""),
        }

    @staticmethod
    def set_final_version(
        db: Session, world_id: int, draft_id: int,
        source_type: str, source_id: int, note: str = None
    ) -> NovelFinalDraft:
        """Set a version as the final adopted draft."""
        if source_type not in ("draft", "revision"):
            raise ValueError("source_type 必须是 draft 或 revision")

        # Validate source
        source = NovelVersionService.get_text_version(
            db, world_id, draft_id, source_type, source_id
        )
        if not source:
            raise ValueError("来源版本不存在或不属于当前草稿")

        if source.get("status") == "discarded":
            raise ValueError("已废弃的版本不能设为最终采用稿")

        # Deactivate old final for this draft
        db.query(NovelFinalDraft).filter_by(
            draft_id=draft_id, is_active=True
        ).update({"is_active": False, "revoked_at": _utcnow(), "updated_at": _utcnow()})

        # Create new final draft record
        draft = db.query(NovelDraft).filter_by(id=draft_id).first()
        final = NovelFinalDraft(
            world_id=world_id,
            draft_id=draft_id,
            source_type=source_type,
            source_id=source_id,
            chapter_outline_id=draft.chapter_outline_id if draft else None,
            volume_index=draft.volume_index if draft else 0,
            chapter_index=draft.chapter_index if draft else 0,
            title=source.get("title", ""),
            content_snapshot=source.get("content", ""),
            word_count=source.get("word_count", 0),
            source_title=source.get("title", ""),
            source_status=source.get("status", ""),
            note=note or "",
            is_active=True,
            accepted_at=_utcnow(),
            created_at=_utcnow(),
            updated_at=_utcnow(),
        )
        db.add(final)
        db.commit()
        db.refresh(final)
        return final

    @staticmethod
    def get_current_final_version(
        db: Session, world_id: int, draft_id: int
    ) -> Optional[NovelFinalDraft]:
        """Get the current active final draft for a chapter."""
        return db.query(NovelFinalDraft).filter_by(
            world_id=world_id, draft_id=draft_id, is_active=True
        ).first()

    @staticmethod
    def revoke_final_version(
        db: Session, world_id: int, draft_id: int
    ) -> bool:
        """Revoke the current final draft."""
        final = NovelVersionService.get_current_final_version(db, world_id, draft_id)
        if not final:
            return False
        final.is_active = False
        final.revoked_at = _utcnow()
        final.updated_at = _utcnow()
        db.commit()
        return True

    @staticmethod
    def list_final_version_history(
        db: Session, world_id: int, draft_id: int
    ) -> List[NovelFinalDraft]:
        """List all final draft records for a chapter, including historical."""
        return db.query(NovelFinalDraft).filter_by(
            world_id=world_id, draft_id=draft_id
        ).order_by(NovelFinalDraft.created_at.desc()).all()

    @staticmethod
    def list_all_final_drafts(
        db: Session, world_id: int
    ) -> List[NovelFinalDraft]:
        """List all final draft records for a world."""
        return db.query(NovelFinalDraft).filter_by(
            world_id=world_id
        ).order_by(NovelFinalDraft.created_at.desc()).all()

    @staticmethod
    def get_final_draft_detail(
        db: Session, world_id: int, final_id: int
    ) -> Optional[NovelFinalDraft]:
        """Get a specific final draft detail."""
        return db.query(NovelFinalDraft).filter_by(
            id=final_id, world_id=world_id
        ).first()

    @staticmethod
    def get_best_context_text_for_draft(
        db: Session, world_id: int, draft_id: int
    ) -> str:
        """
        Get the best text for subsequent context building.
        Priority: final draft snapshot > accepted revision > original draft.
        """
        # 1. Current final draft
        final = NovelVersionService.get_current_final_version(db, world_id, draft_id)
        if final and final.content_snapshot:
            return final.content_snapshot

        # 2. Accepted revision
        rev = db.query(NovelDraftRevision).filter_by(
            draft_id=draft_id, world_id=world_id, is_accepted=True
        ).first()
        if rev and rev.content:
            return rev.content

        # 3. Original draft
        draft = db.query(NovelDraft).filter_by(id=draft_id, world_id=world_id).first()
        if draft and draft.content:
            return draft.content

        return ""
