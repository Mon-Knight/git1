"""
AI World Engine - Timeline Service
Business logic for timeline viewing and filtering.
"""

from typing import List
from sqlalchemy.orm import Session, joinedload

from app.models import HistoricalEvent


class TimelineService:
    """Service for timeline operations."""

    @staticmethod
    def get_timeline_events(
        db: Session,
        world_id: int,
        view: str = "canon",
    ) -> List[HistoricalEvent]:
        """
        Get timeline events for a world, filtered by view mode.

        Args:
            db: Database session
            world_id: World ID
            view: Filter mode - 'canon' (default), 'all', or 'non_canon'

        Returns:
            List of HistoricalEvent ordered by event_time (text sort), then created_at.
            Events with empty event_time are sorted last.
        """
        query = (
            db.query(HistoricalEvent)
            .options(joinedload(HistoricalEvent.location))
            .filter(HistoricalEvent.world_id == world_id)
        )

        if view == "canon":
            query = query.filter(HistoricalEvent.is_canon == True)
        elif view == "non_canon":
            query = query.filter(HistoricalEvent.is_canon != True)
        # view == "all": no additional filter

        # Sort: events with event_time first (alphabetically), then by created_at.
        # Empty event_time goes to the end.
        events = query.order_by(
            HistoricalEvent.event_time == "",
            HistoricalEvent.event_time,
            HistoricalEvent.created_at,
        ).all()

        return events

    @staticmethod
    def get_canon_events(db: Session, world_id: int) -> List[HistoricalEvent]:
        """Get only canon events."""
        return TimelineService.get_timeline_events(db, world_id, view="canon")

    @staticmethod
    def get_non_canon_events(db: Session, world_id: int) -> List[HistoricalEvent]:
        """Get only non-canon events."""
        return TimelineService.get_timeline_events(db, world_id, view="non_canon")
