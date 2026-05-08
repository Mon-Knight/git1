"""
AI World Engine - Character Service
Business logic for character CRUD operations.
"""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.models import Character


class CharacterService:
    """Service for character management operations."""

    @staticmethod
    def create_character(
        db: Session,
        world_id: int,
        name: str,
        role: str = "",
        faction_id: Optional[int] = None,
        personality: str = "",
        goal: str = "",
        abilities: str = "",
        current_status: str = "存活",
        notes: str = "",
    ) -> Character:
        """Create a new character in a world."""
        character = Character(
            world_id=world_id,
            name=name,
            role=role,
            faction_id=faction_id,
            personality=personality,
            goal=goal,
            abilities=abilities,
            current_status=current_status,
            notes=notes,
        )
        db.add(character)
        db.commit()
        db.refresh(character)
        return character

    @staticmethod
    def list_characters(db: Session, world_id: int) -> List[Character]:
        """List all characters in a world."""
        return (
            db.query(Character)
            .options(joinedload(Character.faction))
            .filter(Character.world_id == world_id)
            .order_by(Character.created_at.desc())
            .all()
        )

    @staticmethod
    def get_character(db: Session, character_id: int) -> Optional[Character]:
        """Get a character by ID with faction loaded."""
        return (
            db.query(Character)
            .options(joinedload(Character.faction))
            .filter(Character.id == character_id)
            .first()
        )

    @staticmethod
    def update_character(
        db: Session,
        character_id: int,
        name: str,
        role: str = "",
        faction_id: Optional[int] = None,
        personality: str = "",
        goal: str = "",
        abilities: str = "",
        current_status: str = "存活",
        notes: str = "",
    ) -> Optional[Character]:
        """Update a character. Returns None if not found."""
        character = db.query(Character).filter(Character.id == character_id).first()
        if not character:
            return None

        character.name = name
        character.role = role
        character.faction_id = faction_id
        character.personality = personality
        character.goal = goal
        character.abilities = abilities
        character.current_status = current_status
        character.notes = notes

        db.commit()
        db.refresh(character)
        return character

    @staticmethod
    def delete_character(db: Session, character_id: int) -> bool:
        """Delete a character. Returns True if deleted, False if not found."""
        character = db.query(Character).filter(Character.id == character_id).first()
        if not character:
            return False
        db.delete(character)
        db.commit()
        return True
