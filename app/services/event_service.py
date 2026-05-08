"""
AI World Engine - Event Service
Business logic for historical event CRUD operations.
"""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.models import HistoricalEvent


class EventService:
    """Service for historical event management operations."""

    @staticmethod
    def create_event(
        db: Session,
        world_id: int,
        title: str,
        event_time: str = "",
        involved_characters: str = "",
        involved_factions: str = "",
        location_id: Optional[int] = None,
        content: str = "",
        consequences: str = "",
        is_canon: bool = True,
        source_type: str = "manual",
        source_id: Optional[int] = None,
    ) -> HistoricalEvent:
        """Create a new historical event."""
        event = HistoricalEvent(
            world_id=world_id,
            title=title,
            event_time=event_time,
            involved_characters=involved_characters,
            involved_factions=involved_factions,
            location_id=location_id,
            content=content,
            consequences=consequences,
            is_canon=is_canon,
            source_type=source_type,
            source_id=source_id,
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def list_events(db: Session, world_id: int) -> List[HistoricalEvent]:
        """List all events in a world, newest first."""
        return (
            db.query(HistoricalEvent)
            .options(joinedload(HistoricalEvent.location))
            .filter(HistoricalEvent.world_id == world_id)
            .order_by(HistoricalEvent.created_at.desc())
            .all()
        )

    @staticmethod
    def get_event(db: Session, event_id: int) -> Optional[HistoricalEvent]:
        """Get an event by ID with location loaded."""
        return (
            db.query(HistoricalEvent)
            .options(joinedload(HistoricalEvent.location))
            .filter(HistoricalEvent.id == event_id)
            .first()
        )

    @staticmethod
    def update_event(
        db: Session,
        event_id: int,
        title: str,
        event_time: str = "",
        involved_characters: str = "",
        involved_factions: str = "",
        location_id: Optional[int] = None,
        content: str = "",
        consequences: str = "",
        is_canon: bool = True,
        source_type: str = "manual",
        source_id: Optional[int] = None,
    ) -> Optional[HistoricalEvent]:
        """Update an event. Returns None if not found."""
        event = db.query(HistoricalEvent).filter(HistoricalEvent.id == event_id).first()
        if not event:
            return None

        event.title = title
        event.event_time = event_time
        event.involved_characters = involved_characters
        event.involved_factions = involved_factions
        event.location_id = location_id
        event.content = content
        event.consequences = consequences
        event.is_canon = is_canon
        event.source_type = source_type
        event.source_id = source_id

        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def delete_event(db: Session, event_id: int) -> bool:
        """Delete an event. Returns True if deleted, False if not found."""
        event = db.query(HistoricalEvent).filter(HistoricalEvent.id == event_id).first()
        if not event:
            return False
        db.delete(event)
        db.commit()
        return True
