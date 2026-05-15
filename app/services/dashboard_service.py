"""
AI World Engine - Dashboard Service
Data aggregation for the home page / workspace dashboard.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func


class DashboardService:
    """Service that aggregates data for the workspace dashboard."""

    @staticmethod
    def get_dashboard_summary(db: Session) -> Dict[str, Any]:
        """Return aggregate counts for the dashboard overview cards."""
        from app.models import (
            World, Character, Faction, Location, WorldRule,
            HistoricalEvent, SimulationRecord, Branch,
            ContextPackage, StyleProfile, PlotAnchor,
        )

        return {
            "world_count": db.query(func.count(World.id)).scalar() or 0,
            "character_count": db.query(func.count(Character.id)).scalar() or 0,
            "faction_count": db.query(func.count(Faction.id)).scalar() or 0,
            "location_count": db.query(func.count(Location.id)).scalar() or 0,
            "rule_count": db.query(func.count(WorldRule.id)).scalar() or 0,
            "canon_event_count": db.query(func.count(HistoricalEvent.id)).filter(
                HistoricalEvent.is_canon == True
            ).scalar() or 0,
            "simulation_record_count": db.query(func.count(SimulationRecord.id)).scalar() or 0,
            "pending_simulation_count": db.query(func.count(SimulationRecord.id)).filter(
                SimulationRecord.status == "pending"
            ).scalar() or 0,
            "branch_count": db.query(func.count(Branch.id)).scalar() or 0,
            "context_package_count": db.query(func.count(ContextPackage.id)).scalar() or 0,
            "style_profile_count": db.query(func.count(StyleProfile.id)).scalar() or 0,
            "plot_anchor_count": db.query(func.count(PlotAnchor.id)).scalar() or 0,
            "novel_evolution_count": db.query(func.count(SimulationRecord.id)).filter(
                SimulationRecord.simulation_type == "novel_evolution"
            ).scalar() or 0,
            "mainline_evolution_count": db.query(func.count(SimulationRecord.id)).filter(
                SimulationRecord.simulation_type == "novel_evolution",
                SimulationRecord.status == "adopted",
            ).scalar() or 0,
            "candidate_evolution_count": db.query(func.count(SimulationRecord.id)).filter(
                SimulationRecord.simulation_type == "novel_evolution",
                SimulationRecord.status == "branched",
            ).scalar() or 0,
        }

    @staticmethod
    def get_recent_worlds(db: Session, limit: int = 5) -> List[Dict[str, Any]]:
        """Return recent worlds with summary counts (v2.0.1: added novel engineering stats)."""
        from app.models import (
            World, Character, Faction, WorldRule,
            HistoricalEvent, SimulationRecord, ContextPackage,
            NovelVolumeOutline, NovelChapterOutline, NovelDraft,
        )

        worlds = (
            db.query(World)
            .order_by(World.created_at.desc())
            .limit(limit)
            .all()
        )

        result = []
        for w in worlds:
            result.append({
                "id": w.id,
                "name": w.name,
                "world_type": w.world_type or "",
                "description": (w.description or "")[:120],
                "current_era": w.current_era or "",
                "tone": w.tone or "",
                "created_at": w.created_at,
                "updated_at": getattr(w, 'updated_at', w.created_at),
                "character_count": db.query(func.count(Character.id)).filter(
                    Character.world_id == w.id
                ).scalar() or 0,
                "faction_count": db.query(func.count(Faction.id)).filter(
                    Faction.world_id == w.id
                ).scalar() or 0,
                "rule_count": db.query(func.count(WorldRule.id)).filter(
                    WorldRule.world_id == w.id
                ).scalar() or 0,
                "canon_event_count": db.query(func.count(HistoricalEvent.id)).filter(
                    HistoricalEvent.world_id == w.id,
                    HistoricalEvent.is_canon == True,
                ).scalar() or 0,
                "simulation_count": db.query(func.count(SimulationRecord.id)).filter(
                    SimulationRecord.world_id == w.id
                ).scalar() or 0,
                "context_package_count": db.query(func.count(ContextPackage.id)).filter(
                    ContextPackage.world_id == w.id
                ).scalar() or 0,
                "novel_evolution_count": db.query(func.count(SimulationRecord.id)).filter(
                    SimulationRecord.world_id == w.id,
                    SimulationRecord.simulation_type == "novel_evolution",
                ).scalar() or 0,
                # v2.0.1: Novel engineering stats
                "mainline_evolution_count": db.query(func.count(SimulationRecord.id)).filter(
                    SimulationRecord.world_id == w.id,
                    SimulationRecord.simulation_type == "novel_evolution",
                    SimulationRecord.status == "adopted",
                ).scalar() or 0,
                "volume_outline_count": db.query(func.count(NovelVolumeOutline.id)).filter(
                    NovelVolumeOutline.world_id == w.id
                ).scalar() or 0,
                "chapter_outline_count": db.query(func.count(NovelChapterOutline.id)).filter(
                    NovelChapterOutline.world_id == w.id
                ).scalar() or 0,
                "novel_draft_count": db.query(func.count(NovelDraft.id)).filter(
                    NovelDraft.world_id == w.id
                ).scalar() or 0,
            })
        return result

    @staticmethod
    def get_pending_items(db: Session, limit: int = 8) -> List[Dict[str, Any]]:
        """Return pending simulation and novel_evolution records."""
        from app.models import SimulationRecord, World

        records = (
            db.query(SimulationRecord)
            .filter(SimulationRecord.status == "pending")
            .order_by(SimulationRecord.created_at.desc())
            .limit(limit)
            .all()
        )

        result = []
        for r in records:
            world = db.query(World).filter(World.id == r.world_id).first()
            result.append({
                "id": r.id,
                "world_id": r.world_id,
                "world_name": world.name if world else "未知世界",
                "question": (r.question or "")[:100],
                "simulation_type": r.simulation_type or "",
                "status": r.status,
                "created_at": r.created_at,
            })
        return result

    @staticmethod
    def get_recent_context_packages(db: Session, limit: int = 5) -> List[Dict[str, Any]]:
        """Return recent context packages with referenced asset info."""
        from app.models import ContextPackage, World, StyleProfile, PlotAnchor

        packages = (
            db.query(ContextPackage)
            .order_by(ContextPackage.updated_at.desc())
            .limit(limit)
            .all()
        )

        result = []
        for p in packages:
            world = db.query(World).filter(World.id == p.world_id).first()
            style_name = None
            anchor_name = None
            if p.style_profile_id:
                style = db.query(StyleProfile).filter(StyleProfile.id == p.style_profile_id).first()
                if style:
                    style_name = style.name
            if p.plot_anchor_id:
                anchor = db.query(PlotAnchor).filter(PlotAnchor.id == p.plot_anchor_id).first()
                if anchor:
                    anchor_name = anchor.name

            result.append({
                "id": p.id,
                "world_id": p.world_id,
                "world_name": world.name if world else "未知世界",
                "name": p.name,
                "description": (p.description or "")[:80],
                "style_profile_name": style_name,
                "plot_anchor_name": anchor_name,
                "is_default": p.is_default,
                "updated_at": p.updated_at,
            })
        return result

    @staticmethod
    def get_recent_novel_evolutions(db: Session, limit: int = 5) -> List[Dict[str, Any]]:
        """Return recent novel evolution records."""
        from app.models import SimulationRecord, World

        records = (
            db.query(SimulationRecord)
            .filter(SimulationRecord.simulation_type == "novel_evolution")
            .order_by(SimulationRecord.created_at.desc())
            .limit(limit)
            .all()
        )

        result = []
        for r in records:
            world = db.query(World).filter(World.id == r.world_id).first()
            result.append({
                "id": r.id,
                "world_id": r.world_id,
                "world_name": world.name if world else "未知世界",
                "question": (r.question or "")[:100],
                "status": r.status,
                "created_at": r.created_at,
            })
        return result

    @staticmethod
    def get_quick_actions(recent_world_id: Optional[int] = None) -> List[Dict[str, str]]:
        """Return quick action links for the dashboard."""
        actions = [
            {"label": "新建世界", "url": "/worlds/new", "icon": "🏰"},
            {"label": "世界列表", "url": "/worlds", "icon": "🌍"},
            {"label": "数据管理", "url": "/data", "icon": "📦"},
            {"label": "AI 设置", "url": "/settings/ai", "icon": "⚙️"},
        ]
        if recent_world_id:
            actions.insert(2, {
                "label": "全书演化推演",
                "url": f"/worlds/{recent_world_id}/novel/evolution",
                "icon": "📖",
            })
            actions.insert(2, {
                "label": "创作上下文",
                "url": f"/worlds/{recent_world_id}/context",
                "icon": "📦",
            })
        return actions
