"""
AI World Engine - Volume Outline Routes
Routes for generating and managing novel volume outlines.
"""
import json
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.world_service import WorldService
from app.services.volume_outline_service import VolumeOutlineService
from app.config import settings

router = APIRouter(prefix="/worlds/{world_id}/novel")

templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


def _get_asset_options(db: Session, world_id: int) -> dict:
    """Get available assets for the volume outline form."""
    from app.models import SimulationRecord, StyleProfile, PlotAnchor, ContextPackage

    evolutions = db.query(SimulationRecord).filter_by(
        world_id=world_id, simulation_type="novel_evolution"
    ).order_by(SimulationRecord.created_at.desc()).limit(20).all()

    styles = db.query(StyleProfile).filter(
        (StyleProfile.world_id == world_id) | (StyleProfile.world_id == None)
    ).order_by(StyleProfile.created_at.desc()).limit(20).all()

    anchors = db.query(PlotAnchor).filter_by(
        world_id=world_id
    ).order_by(PlotAnchor.created_at.desc()).limit(20).all()

    packages = db.query(ContextPackage).filter_by(
        world_id=world_id
    ).order_by(ContextPackage.created_at.desc()).limit(20).all()

    return {
        "evolutions": evolutions,
        "styles": styles,
        "anchors": anchors,
        "packages": packages,
    }


@router.get("/volume-outlines", response_class=HTMLResponse)
async def volume_outlines_list(request: Request, world_id: int, db: Session = Depends(get_db)):
    """List all volume outlines for a world."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    outlines = VolumeOutlineService.list_volume_outlines(db, world_id)
    return templates.TemplateResponse(request, "volume_outlines/index.html", {
        "world": world,
        "outlines": outlines,
        "active_nav": "novel",
        "current_world": world,
        "app_version": settings.VERSION,
    })


@router.get("/volume-outlines/new", response_class=HTMLResponse)
async def volume_outlines_new(request: Request, world_id: int, db: Session = Depends(get_db)):
    """Show the new volume outline generation form."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    assets = _get_asset_options(db, world_id)
    return templates.TemplateResponse(request, "volume_outlines/new.html", {
        "world": world,
        "active_nav": "novel",
        "current_world": world,
        "app_version": settings.VERSION,
        **assets,
    })


@router.post("/volume-outlines", response_class=HTMLResponse)
async def volume_outlines_create(
    request: Request, world_id: int, db: Session = Depends(get_db),
    source_evolution_id: str = Form(default=""),
    style_profile_id: str = Form(default=""),
    plot_anchor_id: str = Form(default=""),
    context_package_id: str = Form(default=""),
    volume_count: str = Form(default="5"),
    extra_requirements: str = Form(default=""),
):
    """Generate a new volume outline."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    # Parse IDs
    evo_id = int(source_evolution_id) if source_evolution_id else None
    sty_id = int(style_profile_id) if style_profile_id else None
    anc_id = int(plot_anchor_id) if plot_anchor_id else None
    pkg_id = int(context_package_id) if context_package_id else None

    try:
        vc = int(volume_count) if volume_count else 5
        vc = max(2, min(vc, 20))
    except ValueError:
        vc = 5

    try:
        result = VolumeOutlineService.generate_volume_outline(
            db, world_id, evo_id, sty_id, anc_id, pkg_id, vc, extra_requirements
        )
        outline = VolumeOutlineService.save_volume_outline(
            db, world_id,
            prompt=result["prompt"],
            result_json=result["result_json"],
            raw_text=result.get("raw_text", ""),
            volume_count=result["volume_count"],
            source_evolution_id=evo_id,
            style_profile_id=sty_id,
            plot_anchor_id=anc_id,
            context_package_id=pkg_id,
            generation_requirement=extra_requirements,
        )
        return RedirectResponse(
            url=f"/worlds/{world_id}/novel/volume-outlines/{outline.id}",
            status_code=303
        )
    except Exception as e:
        assets = _get_asset_options(db, world_id)
        return templates.TemplateResponse(request, "volume_outlines/new.html", {
            "world": world,
            "active_nav": "novel",
            "current_world": world,
            "app_version": settings.VERSION,
            "error": str(e),
            "form_data": {
                "source_evolution_id": source_evolution_id,
                "style_profile_id": style_profile_id,
                "plot_anchor_id": plot_anchor_id,
                "context_package_id": context_package_id,
                "volume_count": volume_count,
                "extra_requirements": extra_requirements,
            },
            **_get_asset_options(db, world_id),
        })


@router.get("/volume-outlines/{outline_id}", response_class=HTMLResponse)
async def volume_outlines_detail(request: Request, world_id: int, outline_id: int, db: Session = Depends(get_db)):
    """Show volume outline detail."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    outline = VolumeOutlineService.get_volume_outline(db, world_id, outline_id)
    if not outline:
        return templates.TemplateResponse(request, "volume_outlines/404.html", {
            "world": world, "outline_id": outline_id, "world_id": world_id
        }, status_code=404)

    volumes = []
    try:
        data = json.loads(outline.result_json)
        volumes = data.get("volumes", [])
    except (json.JSONDecodeError, ValueError):
        pass

    return templates.TemplateResponse(request, "volume_outlines/detail.html", {
        "world": world,
        "outline": outline,
        "volumes": volumes,
        "active_nav": "novel",
        "current_world": world,
        "app_version": settings.VERSION,
    })


@router.get("/volume-outlines/{outline_id}/edit", response_class=HTMLResponse)
async def volume_outlines_edit(request: Request, world_id: int, outline_id: int, db: Session = Depends(get_db)):
    """Show volume outline edit form."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    outline = VolumeOutlineService.get_volume_outline(db, world_id, outline_id)
    if not outline:
        return templates.TemplateResponse(request, "volume_outlines/404.html", {
            "world": world, "outline_id": outline_id, "world_id": world_id
        }, status_code=404)

    if outline.status == "discarded":
        return templates.TemplateResponse(request, "volume_outlines/detail.html", {
            "world": world, "outline": outline, "volumes": [],
            "active_nav": "novel", "current_world": world,
            "app_version": settings.VERSION, "error": "已废弃的分卷大纲不能编辑",
        })

    volumes = []
    try:
        data = json.loads(outline.result_json)
        volumes = data.get("volumes", [])
    except (json.JSONDecodeError, ValueError):
        pass

    return templates.TemplateResponse(request, "volume_outlines/edit.html", {
        "world": world,
        "outline": outline,
        "volumes": volumes,
        "active_nav": "novel",
        "current_world": world,
        "app_version": settings.VERSION,
    })


@router.post("/volume-outlines/{outline_id}/edit", response_class=HTMLResponse)
async def volume_outlines_update(
    request: Request, world_id: int, outline_id: int, db: Session = Depends(get_db),
    title: str = Form(default=""),
    summary: str = Form(default=""),
    volume_titles: list = Form(default=[]),
    volume_conflicts: list = Form(default=[]),
    volume_goals: list = Form(default=[]),
    volume_events: list = Form(default=[]),
    volume_hooks: list = Form(default=[]),
):
    """Save edited volume outline."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    try:
        VolumeOutlineService.update_volume_outline(db, world_id, outline_id, {
            "title": title,
            "summary": summary,
            "volume_titles": volume_titles,
            "volume_conflicts": volume_conflicts,
            "volume_goals": volume_goals,
            "volume_events": volume_events,
            "volume_hooks": volume_hooks,
        })
        return RedirectResponse(
            url=f"/worlds/{world_id}/novel/volume-outlines/{outline_id}",
            status_code=303
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/worlds/{world_id}/novel/volume-outlines/{outline_id}",
            status_code=303
        )


@router.post("/volume-outlines/{outline_id}/set-main", response_class=HTMLResponse)
async def volume_outlines_set_main(request: Request, world_id: int, outline_id: int, db: Session = Depends(get_db)):
    """Set a volume outline as the main plan."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    try:
        VolumeOutlineService.set_main_volume_outline(db, world_id, outline_id)
    except ValueError as e:
        pass

    return RedirectResponse(
        url=f"/worlds/{world_id}/novel/volume-outlines/{outline_id}",
        status_code=303
    )


@router.post("/volume-outlines/{outline_id}/discard", response_class=HTMLResponse)
async def volume_outlines_discard(request: Request, world_id: int, outline_id: int, db: Session = Depends(get_db)):
    """Discard a volume outline."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    try:
        VolumeOutlineService.discard_volume_outline(db, world_id, outline_id)
    except ValueError:
        pass

    return RedirectResponse(
        url=f"/worlds/{world_id}/novel/volume-outlines",
        status_code=303
    )
