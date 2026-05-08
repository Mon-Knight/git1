"""
AI World Engine - World Service
Business logic for world CRUD operations.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.models import World


class WorldService:
    """Service for world management operations."""

    @staticmethod
    def create_world(
        db: Session,
        name: str,
        world_type: str = "",
        description: str = "",
        current_era: str = "",
        tone: str = "",
    ) -> World:
        """Create a new world."""
        world = World(
            name=name,
            world_type=world_type,
            description=description,
            current_era=current_era,
            tone=tone,
        )
        db.add(world)
        db.commit()
        db.refresh(world)
        return world

    @staticmethod
    def list_worlds(db: Session) -> List[World]:
        """List all worlds ordered by creation time (newest first)."""
        return db.query(World).order_by(World.created_at.desc()).all()

    @staticmethod
    def get_world(db: Session, world_id: int) -> Optional[World]:
        """Get a world by ID, or None if not found."""
        return db.query(World).filter(World.id == world_id).first()

    @staticmethod
    def update_world(
        db: Session,
        world_id: int,
        name: str,
        world_type: str = "",
        description: str = "",
        current_era: str = "",
        tone: str = "",
    ) -> Optional[World]:
        """Update an existing world. Returns None if not found."""
        world = db.query(World).filter(World.id == world_id).first()
        if not world:
            return None

        world.name = name
        world.world_type = world_type
        world.description = description
        world.current_era = current_era
        world.tone = tone

        db.commit()
        db.refresh(world)
        return world

    @staticmethod
    def delete_world(db: Session, world_id: int) -> bool:
        """Delete a world by ID. Returns True if deleted, False if not found."""
        world = db.query(World).filter(World.id == world_id).first()
        if not world:
            return False

        db.delete(world)
        db.commit()
        return True
