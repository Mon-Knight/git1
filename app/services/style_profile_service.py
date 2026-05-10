"""
AI World Engine - Style Profile Service
CRUD operations for writing style profiles.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.models import StyleProfile


class StyleProfileService:
    """Service for style profile operations."""

    @staticmethod
    def create_style_profile(
        db: Session,
        name: str,
        world_id: Optional[int] = None,
        description: str = "",
        genre: str = "",
        narrative_pov: str = "",
        pacing: str = "",
        sentence_style: str = "",
        paragraph_style: str = "",
        description_ratio: str = "",
        dialogue_style: str = "",
        action_style: str = "",
        psychology_style: str = "",
        info_release_style: str = "",
        conflict_style: str = "",
        character_style: str = "",
        battle_style: str = "",
        emotion_style: str = "",
        opening_style: str = "",
        ending_hook_style: str = "",
        forbidden_patterns: str = "",
        extra_instructions: str = "",
        is_active: bool = True,
    ) -> StyleProfile:
        """Create a new style profile."""
        profile = StyleProfile(
            world_id=world_id,
            name=name.strip(),
            description=description.strip(),
            genre=genre.strip(),
            narrative_pov=narrative_pov.strip(),
            pacing=pacing.strip(),
            sentence_style=sentence_style.strip(),
            paragraph_style=paragraph_style.strip(),
            description_ratio=description_ratio.strip(),
            dialogue_style=dialogue_style.strip(),
            action_style=action_style.strip(),
            psychology_style=psychology_style.strip(),
            info_release_style=info_release_style.strip(),
            conflict_style=conflict_style.strip(),
            character_style=character_style.strip(),
            battle_style=battle_style.strip(),
            emotion_style=emotion_style.strip(),
            opening_style=opening_style.strip(),
            ending_hook_style=ending_hook_style.strip(),
            forbidden_patterns=forbidden_patterns.strip(),
            extra_instructions=extra_instructions.strip(),
            is_active=is_active,
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile

    @staticmethod
    def get_style_profile(db: Session, profile_id: int) -> Optional[StyleProfile]:
        """Get a style profile by ID."""
        return db.query(StyleProfile).filter(StyleProfile.id == profile_id).first()

    @staticmethod
    def list_style_profiles(db: Session) -> List[StyleProfile]:
        """List all style profiles."""
        return (
            db.query(StyleProfile)
            .order_by(StyleProfile.updated_at.desc())
            .all()
        )

    @staticmethod
    def list_available_style_profiles_for_world(
        db: Session, world_id: int
    ) -> List[StyleProfile]:
        """List style profiles available for a specific world.
        Includes global profiles (world_id IS NULL) and world-specific profiles.
        """
        return (
            db.query(StyleProfile)
            .filter(
                (StyleProfile.world_id == world_id) | (StyleProfile.world_id.is_(None))
            )
            .filter(StyleProfile.is_active == True)
            .order_by(StyleProfile.updated_at.desc())
            .all()
        )

    @staticmethod
    def update_style_profile(
        db: Session,
        profile_id: int,
        **kwargs,
    ) -> Optional[StyleProfile]:
        """Update a style profile. Returns updated profile or None if not found."""
        profile = db.query(StyleProfile).filter(StyleProfile.id == profile_id).first()
        if not profile:
            return None

        updatable_fields = [
            "name", "world_id", "description", "genre", "narrative_pov",
            "pacing", "sentence_style", "paragraph_style", "description_ratio",
            "dialogue_style", "action_style", "psychology_style",
            "info_release_style", "conflict_style", "character_style",
            "battle_style", "emotion_style", "opening_style",
            "ending_hook_style", "forbidden_patterns", "extra_instructions",
            "is_active",
        ]
        for field in updatable_fields:
            if field in kwargs:
                val = kwargs[field]
                if isinstance(val, str) and field not in ("world_id", "is_active"):
                    val = val.strip()
                setattr(profile, field, val)

        db.commit()
        db.refresh(profile)
        return profile

    @staticmethod
    def delete_style_profile(db: Session, profile_id: int) -> bool:
        """Delete a style profile. Returns False if referenced by any ContextPackage."""
        from app.models import ContextPackage
        ref_count = (
            db.query(ContextPackage)
            .filter(ContextPackage.style_profile_id == profile_id)
            .count()
        )
        if ref_count > 0:
            return False  # Referenced, cannot delete

        profile = db.query(StyleProfile).filter(StyleProfile.id == profile_id).first()
        if not profile:
            return False

        db.delete(profile)
        db.commit()
        return True
