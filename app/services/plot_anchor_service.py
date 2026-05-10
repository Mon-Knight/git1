"""
AI World Engine - Plot Anchor Service
CRUD operations for plot anchors (story progress markers).
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.models import PlotAnchor


class PlotAnchorService:
    """Service for plot anchor operations."""

    @staticmethod
    def create_plot_anchor(
        db: Session,
        world_id: int,
        name: str,
        stage: str = "",
        volume_name: str = "",
        chapter_range: str = "",
        protagonist_age: str = "",
        current_time: str = "",
        current_location: str = "",
        occurred_events: str = "",
        hidden_secrets: str = "",
        current_conflict: str = "",
        character_states: str = "",
        faction_states: str = "",
        current_goal: str = "",
        next_goal: str = "",
        forbidden_events: str = "",
        notes: str = "",
        is_locked: bool = False,
    ) -> PlotAnchor:
        """Create a new plot anchor."""
        anchor = PlotAnchor(
            world_id=world_id,
            name=name.strip(),
            stage=stage.strip(),
            volume_name=volume_name.strip(),
            chapter_range=chapter_range.strip(),
            protagonist_age=protagonist_age.strip(),
            current_time=current_time.strip(),
            current_location=current_location.strip(),
            occurred_events=occurred_events.strip(),
            hidden_secrets=hidden_secrets.strip(),
            current_conflict=current_conflict.strip(),
            character_states=character_states.strip(),
            faction_states=faction_states.strip(),
            current_goal=current_goal.strip(),
            next_goal=next_goal.strip(),
            forbidden_events=forbidden_events.strip(),
            notes=notes.strip(),
            is_locked=is_locked,
        )
        db.add(anchor)
        db.commit()
        db.refresh(anchor)
        return anchor

    @staticmethod
    def get_plot_anchor(db: Session, anchor_id: int) -> Optional[PlotAnchor]:
        """Get a plot anchor by ID."""
        return db.query(PlotAnchor).filter(PlotAnchor.id == anchor_id).first()

    @staticmethod
    def list_plot_anchors_by_world(db: Session, world_id: int) -> List[PlotAnchor]:
        """List all plot anchors for a specific world."""
        return (
            db.query(PlotAnchor)
            .filter(PlotAnchor.world_id == world_id)
            .order_by(PlotAnchor.updated_at.desc())
            .all()
        )

    @staticmethod
    def update_plot_anchor(
        db: Session,
        anchor_id: int,
        **kwargs,
    ) -> Optional[PlotAnchor]:
        """Update a plot anchor. Returns updated anchor or None if not found."""
        anchor = db.query(PlotAnchor).filter(PlotAnchor.id == anchor_id).first()
        if not anchor:
            return None

        updatable_fields = [
            "name", "stage", "volume_name", "chapter_range",
            "protagonist_age", "current_time", "current_location",
            "occurred_events", "hidden_secrets", "current_conflict",
            "character_states", "faction_states", "current_goal",
            "next_goal", "forbidden_events", "notes", "is_locked",
        ]
        for field in updatable_fields:
            if field in kwargs:
                val = kwargs[field]
                if isinstance(val, str) and field != "is_locked":
                    val = val.strip()
                setattr(anchor, field, val)

        db.commit()
        db.refresh(anchor)
        return anchor

    @staticmethod
    def delete_plot_anchor(db: Session, anchor_id: int) -> bool:
        """Delete a plot anchor. Returns False if referenced by any ContextPackage."""
        from app.models import ContextPackage
        ref_count = (
            db.query(ContextPackage)
            .filter(ContextPackage.plot_anchor_id == anchor_id)
            .count()
        )
        if ref_count > 0:
            return False  # Referenced, cannot delete

        anchor = db.query(PlotAnchor).filter(PlotAnchor.id == anchor_id).first()
        if not anchor:
            return False

        db.delete(anchor)
        db.commit()
        return True
