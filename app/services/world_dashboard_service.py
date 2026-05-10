"""
AI World Engine - World Dashboard Service
Data aggregation for the world console page (/worlds/{id}).
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc


class WorldDashboardService:
    """Service that aggregates data for a single world's console dashboard."""

    @staticmethod
    def get_world_dashboard_summary(db: Session, world_id: int) -> Dict[str, Any]:
        """Return aggregate counts for a single world."""
        from app.models import (
            Character, Faction, Location, WorldRule,
            HistoricalEvent, SimulationRecord, Branch,
            ContextPackage, StyleProfile, PlotAnchor,
        )

        return {
            "character_count": _count(db, Character, world_id),
            "faction_count": _count(db, Faction, world_id),
            "location_count": _count(db, Location, world_id),
            "rule_count": _count(db, WorldRule, world_id),
            "canon_event_count": db.query(func.count(HistoricalEvent.id)).filter(
                HistoricalEvent.world_id == world_id, HistoricalEvent.is_canon == True
            ).scalar() or 0,
            "non_canon_event_count": db.query(func.count(HistoricalEvent.id)).filter(
                HistoricalEvent.world_id == world_id, HistoricalEvent.is_canon == False
            ).scalar() or 0,
            "simulation_record_count": _count(db, SimulationRecord, world_id),
            "pending_simulation_count": db.query(func.count(SimulationRecord.id)).filter(
                SimulationRecord.world_id == world_id, SimulationRecord.status == "pending"
            ).scalar() or 0,
            "branch_count": _count(db, Branch, world_id),
            "context_package_count": _count(db, ContextPackage, world_id),
            "style_profile_count": db.query(func.count(StyleProfile.id)).filter(
                (StyleProfile.world_id == world_id) | (StyleProfile.world_id.is_(None))
            ).scalar() or 0,
            "plot_anchor_count": _count(db, PlotAnchor, world_id),
            "novel_evolution_count": db.query(func.count(SimulationRecord.id)).filter(
                SimulationRecord.world_id == world_id,
                SimulationRecord.simulation_type == "novel_evolution",
            ).scalar() or 0,
            "mainline_evolution_count": db.query(func.count(SimulationRecord.id)).filter(
                SimulationRecord.world_id == world_id,
                SimulationRecord.simulation_type == "novel_evolution",
                SimulationRecord.status == "adopted",
            ).scalar() or 0,
            "candidate_evolution_count": db.query(func.count(SimulationRecord.id)).filter(
                SimulationRecord.world_id == world_id,
                SimulationRecord.simulation_type == "novel_evolution",
                SimulationRecord.status == "branched",
            ).scalar() or 0,
            "discarded_evolution_count": db.query(func.count(SimulationRecord.id)).filter(
                SimulationRecord.world_id == world_id,
                SimulationRecord.simulation_type == "novel_evolution",
                SimulationRecord.status == "discarded",
            ).scalar() or 0,
        }

    @staticmethod
    def get_world_recent_activity(db: Session, world_id: int, limit: int = 8) -> List[Dict[str, Any]]:
        """Return recent activity items for a world."""
        from app.models import (
            HistoricalEvent, SimulationRecord, ContextPackage,
        )

        items = []

        # Recent historical events
        events = (
            db.query(HistoricalEvent)
            .filter(HistoricalEvent.world_id == world_id)
            .order_by(desc(HistoricalEvent.created_at))
            .limit(limit)
            .all()
        )
        for e in events:
            items.append({
                "type": "历史事件",
                "icon": "📋",
                "title": e.title or "(无标题)",
                "time": e.created_at,
                "url": f"/worlds/{world_id}/events",
            })

        # Recent simulation records
        sims = (
            db.query(SimulationRecord)
            .filter(SimulationRecord.world_id == world_id)
            .order_by(desc(SimulationRecord.created_at))
            .limit(limit)
            .all()
        )
        for s in sims:
            items.append({
                "type": "AI 推演",
                "icon": "🤖",
                "title": (s.question or "(无标题)")[:80],
                "time": s.created_at,
                "url": f"/worlds/{world_id}/records/{s.id}",
            })

        # Recent context packages
        pkgs = (
            db.query(ContextPackage)
            .filter(ContextPackage.world_id == world_id)
            .order_by(desc(ContextPackage.updated_at))
            .limit(limit)
            .all()
        )
        for p in pkgs:
            items.append({
                "type": "上下文包",
                "icon": "📦",
                "title": p.name,
                "time": p.updated_at,
                "url": f"/worlds/{world_id}/context/packages/{p.id}",
            })

        # Sort by time descending, take top 'limit'
        items.sort(key=lambda x: x["time"], reverse=True)
        return items[:limit]

    @staticmethod
    def get_world_recommendations(db: Session, world_id: int) -> List[Dict[str, str]]:
        """Generate recommended next steps based on world state."""
        from app.models import (
            Character, Faction, WorldRule, HistoricalEvent,
            SimulationRecord, ContextPackage,
        )

        recs = []

        char_count = _count(db, Character, world_id)
        if char_count == 0:
            recs.append({
                "title": "创建主要角色",
                "desc": "角色是故事的核心，先创建主角和重要配角。",
                "url": f"/worlds/{world_id}/characters/new",
                "label": "创建角色 →",
            })

        faction_count = _count(db, Faction, world_id)
        if faction_count == 0:
            recs.append({
                "title": "建立主要势力",
                "desc": "定义世界中的组织、国家或派系，建立势力格局。",
                "url": f"/worlds/{world_id}/factions/new",
                "label": "创建势力 →",
            })

        rule_count = _count(db, WorldRule, world_id)
        if rule_count == 0:
            recs.append({
                "title": "补充世界规则",
                "desc": "定义魔法体系、物理法则、社会规则等约束条件。",
                "url": f"/worlds/{world_id}/rules/new",
                "label": "创建规则 →",
            })

        canon_count = db.query(func.count(HistoricalEvent.id)).filter(
            HistoricalEvent.world_id == world_id, HistoricalEvent.is_canon == True
        ).scalar() or 0
        if canon_count == 0:
            recs.append({
                "title": "创建初始历史事件",
                "desc": "为世界建立时间线的起点，定义关键背景事件。",
                "url": f"/worlds/{world_id}/events/new",
                "label": "创建事件 →",
            })

        pkg_count = _count(db, ContextPackage, world_id)
        if pkg_count == 0:
            recs.append({
                "title": "创建创作上下文包",
                "desc": "组合推演方案、风格方案和剧情时间点，为全书演化做准备。",
                "url": f"/worlds/{world_id}/context/packages/new",
                "label": "创建上下文包 →",
            })

        evo_count = db.query(func.count(SimulationRecord.id)).filter(
            SimulationRecord.world_id == world_id,
            SimulationRecord.simulation_type == "novel_evolution",
        ).scalar() or 0

        if pkg_count > 0 and evo_count == 0:
            recs.append({
                "title": "开始全书演化推演",
                "desc": "已有创作上下文包，可以开始生成 12 章节全书演化方案。",
                "url": f"/worlds/{world_id}/novel/evolution",
                "label": "开始推演 →",
            })

        pending_evo = db.query(func.count(SimulationRecord.id)).filter(
            SimulationRecord.world_id == world_id,
            SimulationRecord.simulation_type == "novel_evolution",
            SimulationRecord.status == "pending",
        ).scalar() or 0
        if pending_evo > 0:
            recs.append({
                "title": f"查看 {pending_evo} 条待确认全书演化方案",
                "desc": "有待确认的演化方案，审核后设为主线方案或备选方案。",
                "url": f"/worlds/{world_id}/novel/evolutions",
                "label": "查看方案 →",
            })

        pending_sim = db.query(func.count(SimulationRecord.id)).filter(
            SimulationRecord.world_id == world_id, SimulationRecord.status == "pending"
        ).scalar() or 0
        if pending_sim > 0:
            recs.append({
                "title": f"处理 {pending_sim} 条待确认推演记录",
                "desc": "有待处理的 AI 推演结果，审核后采纳为正史或保存为分支。",
                "url": f"/worlds/{world_id}/records",
                "label": "查看记录 →",
            })

        mainline = db.query(func.count(SimulationRecord.id)).filter(
            SimulationRecord.world_id == world_id,
            SimulationRecord.simulation_type == "novel_evolution",
            SimulationRecord.status == "adopted",
        ).scalar() or 0
        if mainline > 0:
            recs.append({
                "title": "已有主线方案",
                "desc": "已存在主线全书演化方案，后续 v1.8.0 可用于生成分卷大纲。",
                "url": f"/worlds/{world_id}/novel/evolutions",
                "label": "查看方案 →",
            })

        return recs

    @staticmethod
    def get_world_quick_actions(world_id: int) -> List[Dict[str, str]]:
        """Return quick action links for the world console."""
        return [
            {"label": "编辑世界", "url": f"/worlds/{world_id}/edit", "icon": "✏️"},
            {"label": "导出世界 JSON", "url": f"/worlds/{world_id}/export", "icon": "📤"},
            {"label": "创建角色", "url": f"/worlds/{world_id}/characters/new", "icon": "👤"},
            {"label": "创建势力", "url": f"/worlds/{world_id}/factions/new", "icon": "🏛️"},
            {"label": "创建地点", "url": f"/worlds/{world_id}/locations/new", "icon": "📍"},
            {"label": "创建规则", "url": f"/worlds/{world_id}/rules/new", "icon": "📜"},
            {"label": "创建历史事件", "url": f"/worlds/{world_id}/events/new", "icon": "📋"},
            {"label": "AI 推演", "url": f"/worlds/{world_id}/simulation", "icon": "🤖"},
            {"label": "创作上下文", "url": f"/worlds/{world_id}/context", "icon": "📦"},
            {"label": "全书演化", "url": f"/worlds/{world_id}/novel/evolution", "icon": "📖"},
            {"label": "演化方案列表", "url": f"/worlds/{world_id}/novel/evolutions", "icon": "📋"},
            {"label": "检查中心", "url": f"/worlds/{world_id}/checks", "icon": "🔍"},
            {"label": "数据管理", "url": "/data", "icon": "💾"},
        ]


def _count(db: Session, model_class, world_id: int) -> int:
    """Count records for a model filtered by world_id."""
    return db.query(func.count(model_class.id)).filter(
        model_class.world_id == world_id
    ).scalar() or 0
