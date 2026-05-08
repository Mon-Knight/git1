"""
AI World Engine - Location Service
Business logic for location CRUD operations.
"""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.models import Location


class LocationService:
    """Service for location management operations."""

    @staticmethod
    def create_location(
        db: Session,
        world_id: int,
        name: str,
        location_type: str = "",
        region: str = "",
        description: str = "",
        controlling_faction_id: Optional[int] = None,
        important_events: str = "",
    ) -> Location:
        """Create a new location in a world."""
        location = Location(
            world_id=world_id,
            name=name,
            location_type=location_type,
            region=region,
            description=description,
            controlling_faction_id=controlling_faction_id,
            important_events=important_events,
        )
        db.add(location)
        db.commit()
        db.refresh(location)
        return location

    @staticmethod
    def list_locations(db: Session, world_id: int) -> List[Location]:
        """List all locations in a world."""
        return (
            db.query(Location)
            .options(joinedload(Location.controlling_faction))
            .filter(Location.world_id == world_id)
            .order_by(Location.created_at.desc())
            .all()
        )

    @staticmethod
    def get_location(db: Session, location_id: int) -> Optional[Location]:
        """Get a location by ID with controlling faction loaded."""
        return (
            db.query(Location)
            .options(joinedload(Location.controlling_faction))
            .filter(Location.id == location_id)
            .first()
        )

    @staticmethod
    def update_location(
        db: Session,
        location_id: int,
        name: str,
        location_type: str = "",
        region: str = "",
        description: str = "",
        controlling_faction_id: Optional[int] = None,
        important_events: str = "",
    ) -> Optional[Location]:
        """Update a location. Returns None if not found."""
        location = db.query(Location).filter(Location.id == location_id).first()
        if not location:
            return None

        location.name = name
        location.location_type = location_type
        location.region = region
        location.description = description
        location.controlling_faction_id = controlling_faction_id
        location.important_events = important_events

        db.commit()
        db.refresh(location)
        return location

    @staticmethod
    def delete_location(db: Session, location_id: int) -> bool:
        """Delete a location. Returns True if deleted, False if not found."""
        location = db.query(Location).filter(Location.id == location_id).first()
        if not location:
            return False
        db.delete(location)
        db.commit()
        return True
