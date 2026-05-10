"""
AI World Engine - Context Package Service
CRUD and context-building operations for creative context packages.
"""

import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models import ContextPackage, SimulationRecord, StyleProfile, PlotAnchor
from app.constants import SIMULATION_TYPES


class ContextPackageService:
    """Service for context package operations."""

    # Simulation types eligible for context package selection
    ELIGIBLE_SIM_TYPES = [
        "novel_evolution",
        "protagonist_route",
        "world_reaction",
        "world_simulation",
        "general",
    ]

    # Status priority order for display
    STATUS_PRIORITY = {"adopted": 0, "branched": 1, "pending": 2}

    @staticmethod
    def create_context_package(
        db: Session,
        world_id: int,
        name: str,
        description: str = "",
        simulation_record_id: Optional[int] = None,
        style_profile_id: Optional[int] = None,
        plot_anchor_id: Optional[int] = None,
        generation_type: str = "",
        strict_canon: bool = True,
        strict_style: bool = True,
        include_branches: bool = False,
        include_non_canon: bool = False,
        target_words: str = "",
        extra_requirements: str = "",
        is_default: bool = False,
    ) -> ContextPackage:
        """Create a new context package with cross-world validation."""
        # Validate simulation_record belongs to same world
        if simulation_record_id:
            sim = (
                db.query(SimulationRecord)
                .filter(SimulationRecord.id == simulation_record_id)
                .first()
            )
            if not sim:
                raise ValueError(f"推演记录不存在: id={simulation_record_id}")
            if sim.world_id != world_id:
                raise ValueError("推演记录不属于当前世界")

        # Validate plot_anchor belongs to same world
        if plot_anchor_id:
            anchor = (
                db.query(PlotAnchor)
                .filter(PlotAnchor.id == plot_anchor_id)
                .first()
            )
            if not anchor:
                raise ValueError(f"剧情时间点不存在: id={plot_anchor_id}")
            if anchor.world_id != world_id:
                raise ValueError("剧情时间点不属于当前世界")

        # Validate style_profile: if not global, must belong to same world
        if style_profile_id:
            style = (
                db.query(StyleProfile)
                .filter(StyleProfile.id == style_profile_id)
                .first()
            )
            if not style:
                raise ValueError(f"风格方案不存在: id={style_profile_id}")
            if style.world_id is not None and style.world_id != world_id:
                raise ValueError("风格方案不属于当前世界且不是全局方案")

        pkg = ContextPackage(
            world_id=world_id,
            name=name.strip(),
            description=description.strip(),
            simulation_record_id=simulation_record_id,
            style_profile_id=style_profile_id,
            plot_anchor_id=plot_anchor_id,
            generation_type=generation_type.strip(),
            strict_canon=strict_canon,
            strict_style=strict_style,
            include_branches=include_branches,
            include_non_canon=include_non_canon,
            target_words=target_words.strip(),
            extra_requirements=extra_requirements.strip(),
            is_default=is_default,
        )
        db.add(pkg)
        db.commit()
        db.refresh(pkg)
        return pkg

    @staticmethod
    def get_context_package(db: Session, package_id: int) -> Optional[ContextPackage]:
        """Get a context package by ID."""
        return (
            db.query(ContextPackage)
            .filter(ContextPackage.id == package_id)
            .first()
        )

    @staticmethod
    def list_context_packages_by_world(
        db: Session, world_id: int
    ) -> List[ContextPackage]:
        """List all context packages for a specific world."""
        return (
            db.query(ContextPackage)
            .filter(ContextPackage.world_id == world_id)
            .order_by(ContextPackage.updated_at.desc())
            .all()
        )

    @staticmethod
    def update_context_package(
        db: Session,
        package_id: int,
        world_id: Optional[int] = None,
        **kwargs,
    ) -> Optional[ContextPackage]:
        """Update a context package with cross-world validation."""
        pkg = (
            db.query(ContextPackage)
            .filter(ContextPackage.id == package_id)
            .first()
        )
        if not pkg:
            return None

        effective_world_id = world_id if world_id is not None else pkg.world_id

        # Validate simulation_record if being updated
        sim_id = kwargs.get("simulation_record_id")
        if sim_id is not None and sim_id != 0:
            sim = (
                db.query(SimulationRecord)
                .filter(SimulationRecord.id == sim_id)
                .first()
            )
            if not sim:
                raise ValueError(f"推演记录不存在: id={sim_id}")
            if sim.world_id != effective_world_id:
                raise ValueError("推演记录不属于当前世界")

        # Validate plot_anchor if being updated
        anchor_id = kwargs.get("plot_anchor_id")
        if anchor_id is not None and anchor_id != 0:
            anchor = (
                db.query(PlotAnchor)
                .filter(PlotAnchor.id == anchor_id)
                .first()
            )
            if not anchor:
                raise ValueError(f"剧情时间点不存在: id={anchor_id}")
            if anchor.world_id != effective_world_id:
                raise ValueError("剧情时间点不属于当前世界")

        # Validate style_profile if being updated
        style_id = kwargs.get("style_profile_id")
        if style_id is not None and style_id != 0:
            style = (
                db.query(StyleProfile)
                .filter(StyleProfile.id == style_id)
                .first()
            )
            if not style:
                raise ValueError(f"风格方案不存在: id={style_id}")
            if style.world_id is not None and style.world_id != effective_world_id:
                raise ValueError("风格方案不属于当前世界且不是全局方案")

        updatable_fields = [
            "name", "description", "simulation_record_id", "style_profile_id",
            "plot_anchor_id", "generation_type", "strict_canon", "strict_style",
            "include_branches", "include_non_canon", "target_words",
            "extra_requirements", "is_default",
        ]
        for field in updatable_fields:
            if field in kwargs:
                val = kwargs[field]
                if isinstance(val, str) and field not in (
                    "strict_canon", "strict_style", "include_branches",
                    "include_non_canon", "is_default",
                ):
                    val = val.strip()
                # Allow setting to 0 to clear reference
                if val == 0 and field in (
                    "simulation_record_id", "style_profile_id", "plot_anchor_id",
                ):
                    val = None
                setattr(pkg, field, val)

        db.commit()
        db.refresh(pkg)
        return pkg

    @staticmethod
    def delete_context_package(db: Session, package_id: int) -> bool:
        """Delete a context package."""
        pkg = (
            db.query(ContextPackage)
            .filter(ContextPackage.id == package_id)
            .first()
        )
        if not pkg:
            return False

        db.delete(pkg)
        db.commit()
        return True

    @staticmethod
    def list_eligible_simulation_records(
        db: Session, world_id: int
    ) -> List[SimulationRecord]:
        """List simulation records eligible for context package selection.
        Shows eligible types, ordered by status priority.
        Discarded records are excluded by default.
        """
        records = (
            db.query(SimulationRecord)
            .filter(SimulationRecord.world_id == world_id)
            .filter(SimulationRecord.simulation_type.in_(
                ContextPackageService.ELIGIBLE_SIM_TYPES
            ))
            .filter(SimulationRecord.status != "discarded")
            .all()
        )

        # Sort by status priority
        def sort_key(r):
            return ContextPackageService.STATUS_PRIORITY.get(r.status, 99)

        records.sort(key=sort_key)
        return records

    @staticmethod
    def build_context_package_preview(
        db: Session, package_id: int
    ) -> Dict[str, Any]:
        """Build a preview of what a context package contains."""
        pkg = ContextPackageService.get_context_package(db, package_id)
        if not pkg:
            return {"error": "上下文包不存在"}

        preview: Dict[str, Any] = {
            "package_id": pkg.id,
            "package_name": pkg.name,
            "description": pkg.description,
            "generation_type": pkg.generation_type,
            "strict_canon": pkg.strict_canon,
            "strict_style": pkg.strict_style,
            "include_branches": pkg.include_branches,
            "include_non_canon": pkg.include_non_canon,
            "target_words": pkg.target_words,
            "extra_requirements": pkg.extra_requirements,
            "simulation_record": None,
            "style_profile": None,
            "plot_anchor": None,
        }

        if pkg.simulation_record_id:
            sim = (
                db.query(SimulationRecord)
                .filter(SimulationRecord.id == pkg.simulation_record_id)
                .first()
            )
            if sim:
                preview["simulation_record"] = {
                    "id": sim.id,
                    "question": sim.question,
                    "simulation_type": sim.simulation_type,
                    "status": sim.status,
                    "ai_response": sim.ai_response[:500] if sim.ai_response else "",
                }

        if pkg.style_profile_id:
            style = (
                db.query(StyleProfile)
                .filter(StyleProfile.id == pkg.style_profile_id)
                .first()
            )
            if style:
                preview["style_profile"] = {
                    "id": style.id,
                    "name": style.name,
                    "genre": style.genre,
                    "narrative_pov": style.narrative_pov,
                    "pacing": style.pacing,
                    "description": style.description,
                }

        if pkg.plot_anchor_id:
            anchor = (
                db.query(PlotAnchor)
                .filter(PlotAnchor.id == pkg.plot_anchor_id)
                .first()
            )
            if anchor:
                preview["plot_anchor"] = {
                    "id": anchor.id,
                    "name": anchor.name,
                    "stage": anchor.stage,
                    "current_location": anchor.current_location,
                    "current_conflict": anchor.current_conflict,
                }

        return preview

    @staticmethod
    def build_context_for_generation(
        db: Session, package_id: int
    ) -> Dict[str, Any]:
        """Build the full context for AI generation from a context package."""
        pkg = ContextPackageService.get_context_package(db, package_id)
        if not pkg:
            return {"error": "上下文包不存在"}

        context: Dict[str, Any] = {
            "package_name": pkg.name,
            "generation_type": pkg.generation_type,
            "strict_canon": pkg.strict_canon,
            "strict_style": pkg.strict_style,
            "target_words": pkg.target_words,
            "extra_requirements": pkg.extra_requirements,
            "simulation_record_content": None,
            "style_profile_content": None,
            "plot_anchor_content": None,
        }

        if pkg.simulation_record_id:
            sim = (
                db.query(SimulationRecord)
                .filter(SimulationRecord.id == pkg.simulation_record_id)
                .first()
            )
            if sim:
                context["simulation_record_content"] = {
                    "question": sim.question,
                    "simulation_type": sim.simulation_type,
                    "ai_response": sim.ai_response,
                    "status": sim.status,
                }

        if pkg.style_profile_id:
            style = (
                db.query(StyleProfile)
                .filter(StyleProfile.id == pkg.style_profile_id)
                .first()
            )
            if style:
                context["style_profile_content"] = {
                    "name": style.name,
                    "genre": style.genre,
                    "narrative_pov": style.narrative_pov,
                    "pacing": style.pacing,
                    "sentence_style": style.sentence_style,
                    "paragraph_style": style.paragraph_style,
                    "description_ratio": style.description_ratio,
                    "dialogue_style": style.dialogue_style,
                    "action_style": style.action_style,
                    "psychology_style": style.psychology_style,
                    "info_release_style": style.info_release_style,
                    "conflict_style": style.conflict_style,
                    "character_style": style.character_style,
                    "battle_style": style.battle_style,
                    "emotion_style": style.emotion_style,
                    "opening_style": style.opening_style,
                    "ending_hook_style": style.ending_hook_style,
                    "forbidden_patterns": style.forbidden_patterns,
                    "extra_instructions": style.extra_instructions,
                }

        if pkg.plot_anchor_id:
            anchor = (
                db.query(PlotAnchor)
                .filter(PlotAnchor.id == pkg.plot_anchor_id)
                .first()
            )
            if anchor:
                context["plot_anchor_content"] = {
                    "name": anchor.name,
                    "stage": anchor.stage,
                    "volume_name": anchor.volume_name,
                    "chapter_range": anchor.chapter_range,
                    "protagonist_age": anchor.protagonist_age,
                    "current_time": anchor.current_time,
                    "current_location": anchor.current_location,
                    "occurred_events": anchor.occurred_events,
                    "hidden_secrets": anchor.hidden_secrets,
                    "current_conflict": anchor.current_conflict,
                    "character_states": anchor.character_states,
                    "faction_states": anchor.faction_states,
                    "current_goal": anchor.current_goal,
                    "next_goal": anchor.next_goal,
                    "forbidden_events": anchor.forbidden_events,
                }

        return context
