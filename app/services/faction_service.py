"""
AI World Engine - Faction Service
Business logic for faction CRUD operations.
"""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.models import Faction


class FactionService:
    """Service for faction management operations."""

    @staticmethod
    def create_faction(
        db: Session,
        world_id: int,
        name: str,
        faction_type: str = "",
        leader_id: Optional[int] = None,
        goal: str = "",
        resources: str = "",
        enemies: str = "",
        allies: str = "",
        notes: str = "",
    ) -> Faction:
        """Create a new faction in a world."""
        faction = Faction(
            world_id=world_id,
            name=name,
            faction_type=faction_type,
            leader_id=leader_id,
            goal=goal,
            resources=resources,
            enemies=enemies,
            allies=allies,
            notes=notes,
        )
        db.add(faction)
        db.commit()
        db.refresh(faction)
        return faction

    @staticmethod
    def list_factions(db: Session, world_id: int) -> List[Faction]:
        """List all factions in a world."""
        return (
            db.query(Faction)
            .options(joinedload(Faction.leader))
            .filter(Faction.world_id == world_id)
            .order_by(Faction.created_at.desc())
            .all()
        )

    @staticmethod
    def get_faction(db: Session, faction_id: int) -> Optional[Faction]:
        """Get a faction by ID with leader loaded."""
        return (
            db.query(Faction)
            .options(joinedload(Faction.leader), joinedload(Faction.members))
            .filter(Faction.id == faction_id)
            .first()
        )

    @staticmethod
    def update_faction(
        db: Session,
        faction_id: int,
        name: str,
        faction_type: str = "",
        leader_id: Optional[int] = None,
        goal: str = "",
        resources: str = "",
        enemies: str = "",
        allies: str = "",
        notes: str = "",
    ) -> Optional[Faction]:
        """Update a faction. Returns None if not found."""
        faction = db.query(Faction).filter(Faction.id == faction_id).first()
        if not faction:
            return None

        faction.name = name
        faction.faction_type = faction_type
        faction.leader_id = leader_id
        faction.goal = goal
        faction.resources = resources
        faction.enemies = enemies
        faction.allies = allies
        faction.notes = notes

        db.commit()
        db.refresh(faction)
        return faction

    @staticmethod
    def delete_faction(db: Session, faction_id: int) -> bool:
        """Delete a faction. Returns True if deleted, False if not found."""
        faction = db.query(Faction).filter(Faction.id == faction_id).first()
        if not faction:
            return False
        db.delete(faction)
        db.commit()
        return True
