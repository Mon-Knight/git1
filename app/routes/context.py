"""
AI World Engine - Context Asset Routes
Routes for Style Profiles, Plot Anchors, and Context Packages.
"""

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.services.world_service import WorldService
from app.services.style_profile_service import StyleProfileService
from app.services.plot_anchor_service import PlotAnchorService
from app.services.context_package_service import ContextPackageService

router = APIRouter(prefix="/worlds/{world_id}/context")

templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


def _get_world_or_404(db, world_id):
    """Helper: get world or None."""
    return WorldService.get_world(db, world_id)


# ============================================================
# Context Overview
# ============================================================

@router.get("", response_class=HTMLResponse)
async def context_index(request: Request, world_id: int, db: Session = Depends(get_db)):
    """Show creative context asset overview."""
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    style_count = len(StyleProfileService.list_available_style_profiles_for_world(db, world_id))
    anchor_count = len(PlotAnchorService.list_plot_anchors_by_world(db, world_id))
    package_count = len(ContextPackageService.list_context_packages_by_world(db, world_id))

    return templates.TemplateResponse(request, "context/index.html", {
        "world": world,
        "current_world": world,
        "active_nav": "assets",
        "app_version": settings.VERSION,
        "style_count": style_count,
        "anchor_count": anchor_count,
        "package_count": package_count,
    })


# ============================================================
# Style Profiles
# ============================================================

@router.get("/styles", response_class=HTMLResponse)
async def list_styles(request: Request, world_id: int, db: Session = Depends(get_db)):
    """List style profiles available for this world."""
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    profiles = StyleProfileService.list_available_style_profiles_for_world(db, world_id)

    return templates.TemplateResponse(request, "context/styles.html", {
        "world": world,
        "current_world": world,
        "active_nav": "assets",
        "app_version": settings.VERSION,
        "profiles": profiles,
    })


@router.get("/styles/new", response_class=HTMLResponse)
async def new_style_form(request: Request, world_id: int, db: Session = Depends(get_db)):
    """Show create style profile form."""
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    return templates.TemplateResponse(request, "context/style_form.html", {
        "world": world,
        "current_world": world,
        "active_nav": "assets",
        "app_version": settings.VERSION,
        "profile": None,
        "errors": {},
        "form_data": {},
        "is_edit": False,
    })


@router.post("/styles/new", response_class=HTMLResponse)
async def create_style(
    request: Request,
    world_id: int,
    db: Session = Depends(get_db),
    name: str = Form(default=""),
    description: str = Form(default=""),
    genre: str = Form(default=""),
    narrative_pov: str = Form(default=""),
    pacing: str = Form(default=""),
    dialogue_style: str = Form(default=""),
    conflict_style: str = Form(default=""),
    forbidden_patterns: str = Form(default=""),
    extra_instructions: str = Form(default=""),
    is_global: str = Form(default=""),
):
    """Create a new style profile."""
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    errors = {}
    if not name.strip():
        errors["name"] = "名称不能为空"

    if errors:
        return templates.TemplateResponse(request, "context/style_form.html", {
            "world": world,
            "current_world": world,
            "active_nav": "assets",
            "app_version": settings.VERSION,
            "profile": None,
            "errors": errors,
            "form_data": {
                "name": name, "description": description, "genre": genre,
                "narrative_pov": narrative_pov, "pacing": pacing,
                "dialogue_style": dialogue_style, "conflict_style": conflict_style,
                "forbidden_patterns": forbidden_patterns,
                "extra_instructions": extra_instructions,
                "is_global": is_global,
            },
            "is_edit": False,
        }, status_code=422)

    profile_world_id = None if is_global == "1" else world_id
    StyleProfileService.create_style_profile(
        db=db,
        name=name,
        world_id=profile_world_id,
        description=description,
        genre=genre,
        narrative_pov=narrative_pov,
        pacing=pacing,
        dialogue_style=dialogue_style,
        conflict_style=conflict_style,
        forbidden_patterns=forbidden_patterns,
        extra_instructions=extra_instructions,
    )

    return RedirectResponse(
        url=f"/worlds/{world_id}/context/styles", status_code=303
    )


@router.get("/styles/{style_id}/edit", response_class=HTMLResponse)
async def edit_style_form(
    request: Request, world_id: int, style_id: int, db: Session = Depends(get_db)
):
    """Show edit style profile form."""
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    profile = StyleProfileService.get_style_profile(db, style_id)
    if not profile:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    return templates.TemplateResponse(request, "context/style_form.html", {
        "world": world,
        "current_world": world,
        "active_nav": "assets",
        "app_version": settings.VERSION,
        "profile": profile,
        "errors": {},
        "form_data": {},
        "is_edit": True,
    })


@router.post("/styles/{style_id}/edit", response_class=HTMLResponse)
async def update_style(
    request: Request,
    world_id: int,
    style_id: int,
    db: Session = Depends(get_db),
    name: str = Form(default=""),
    description: str = Form(default=""),
    genre: str = Form(default=""),
    narrative_pov: str = Form(default=""),
    pacing: str = Form(default=""),
    dialogue_style: str = Form(default=""),
    conflict_style: str = Form(default=""),
    forbidden_patterns: str = Form(default=""),
    extra_instructions: str = Form(default=""),
    is_global: str = Form(default=""),
):
    """Update a style profile."""
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    profile = StyleProfileService.get_style_profile(db, style_id)
    if not profile:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    errors = {}
    if not name.strip():
        errors["name"] = "名称不能为空"

    if errors:
        return templates.TemplateResponse(request, "context/style_form.html", {
            "world": world,
            "current_world": world,
            "active_nav": "assets",
            "app_version": settings.VERSION,
            "profile": profile,
            "errors": errors,
            "form_data": {
                "name": name, "description": description, "genre": genre,
                "narrative_pov": narrative_pov, "pacing": pacing,
                "dialogue_style": dialogue_style, "conflict_style": conflict_style,
                "forbidden_patterns": forbidden_patterns,
                "extra_instructions": extra_instructions,
                "is_global": is_global,
            },
            "is_edit": True,
        }, status_code=422)

    profile_world_id = None if is_global == "1" else world_id
    StyleProfileService.update_style_profile(
        db=db,
        profile_id=style_id,
        name=name,
        world_id=profile_world_id,
        description=description,
        genre=genre,
        narrative_pov=narrative_pov,
        pacing=pacing,
        dialogue_style=dialogue_style,
        conflict_style=conflict_style,
        forbidden_patterns=forbidden_patterns,
        extra_instructions=extra_instructions,
    )

    return RedirectResponse(
        url=f"/worlds/{world_id}/context/styles", status_code=303
    )


@router.post("/styles/{style_id}/delete", response_class=HTMLResponse)
async def delete_style(
    request: Request, world_id: int, style_id: int, db: Session = Depends(get_db)
):
    """Delete a style profile."""
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    success = StyleProfileService.delete_style_profile(db, style_id)
    if not success:
        # Show error on styles page
        profiles = StyleProfileService.list_available_style_profiles_for_world(db, world_id)
        return templates.TemplateResponse(request, "context/styles.html", {
            "world": world,
            "current_world": world,
            "active_nav": "assets",
            "app_version": settings.VERSION,
            "profiles": profiles,
            "error": "无法删除该风格方案：它正在被某个创作上下文包引用。请先移除引用后再删除。",
        })

    return RedirectResponse(
        url=f"/worlds/{world_id}/context/styles", status_code=303
    )


# ============================================================
# Plot Anchors
# ============================================================

@router.get("/anchors", response_class=HTMLResponse)
async def list_anchors(request: Request, world_id: int, db: Session = Depends(get_db)):
    """List plot anchors for this world."""
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    anchors = PlotAnchorService.list_plot_anchors_by_world(db, world_id)

    return templates.TemplateResponse(request, "context/anchors.html", {
        "world": world,
        "anchors": anchors,
    })


@router.get("/anchors/new", response_class=HTMLResponse)
async def new_anchor_form(request: Request, world_id: int, db: Session = Depends(get_db)):
    """Show create plot anchor form."""
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    return templates.TemplateResponse(request, "context/anchor_form.html", {
        "world": world,
        "anchor": None,
        "errors": {},
        "form_data": {},
        "is_edit": False,
    })


@router.post("/anchors/new", response_class=HTMLResponse)
async def create_anchor(
    request: Request,
    world_id: int,
    db: Session = Depends(get_db),
    name: str = Form(default=""),
    stage: str = Form(default=""),
    volume_name: str = Form(default=""),
    protagonist_age: str = Form(default=""),
    current_location: str = Form(default=""),
    occurred_events: str = Form(default=""),
    hidden_secrets: str = Form(default=""),
    current_conflict: str = Form(default=""),
    character_states: str = Form(default=""),
    faction_states: str = Form(default=""),
    current_goal: str = Form(default=""),
    next_goal: str = Form(default=""),
    forbidden_events: str = Form(default=""),
    notes: str = Form(default=""),
):
    """Create a new plot anchor."""
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    errors = {}
    if not name.strip():
        errors["name"] = "名称不能为空"

    if errors:
        return templates.TemplateResponse(request, "context/anchor_form.html", {
            "world": world,
            "anchor": None,
            "errors": errors,
            "form_data": {
                "name": name, "stage": stage, "volume_name": volume_name,
                "protagonist_age": protagonist_age,
                "current_location": current_location,
                "occurred_events": occurred_events,
                "hidden_secrets": hidden_secrets,
                "current_conflict": current_conflict,
                "character_states": character_states,
                "faction_states": faction_states,
                "current_goal": current_goal, "next_goal": next_goal,
                "forbidden_events": forbidden_events, "notes": notes,
            },
            "is_edit": False,
        }, status_code=422)

    PlotAnchorService.create_plot_anchor(
        db=db,
        world_id=world_id,
        name=name,
        stage=stage,
        volume_name=volume_name,
        protagonist_age=protagonist_age,
        current_location=current_location,
        occurred_events=occurred_events,
        hidden_secrets=hidden_secrets,
        current_conflict=current_conflict,
        character_states=character_states,
        faction_states=faction_states,
        current_goal=current_goal,
        next_goal=next_goal,
        forbidden_events=forbidden_events,
        notes=notes,
    )

    return RedirectResponse(
        url=f"/worlds/{world_id}/context/anchors", status_code=303
    )


@router.get("/anchors/{anchor_id}/edit", response_class=HTMLResponse)
async def edit_anchor_form(
    request: Request, world_id: int, anchor_id: int, db: Session = Depends(get_db)
):
    """Show edit plot anchor form."""
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    anchor = PlotAnchorService.get_plot_anchor(db, anchor_id)
    if not anchor:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    return templates.TemplateResponse(request, "context/anchor_form.html", {
        "world": world,
        "anchor": anchor,
        "errors": {},
        "form_data": {},
        "is_edit": True,
    })


@router.post("/anchors/{anchor_id}/edit", response_class=HTMLResponse)
async def update_anchor(
    request: Request,
    world_id: int,
    anchor_id: int,
    db: Session = Depends(get_db),
    name: str = Form(default=""),
    stage: str = Form(default=""),
    volume_name: str = Form(default=""),
    protagonist_age: str = Form(default=""),
    current_location: str = Form(default=""),
    occurred_events: str = Form(default=""),
    hidden_secrets: str = Form(default=""),
    current_conflict: str = Form(default=""),
    character_states: str = Form(default=""),
    faction_states: str = Form(default=""),
    current_goal: str = Form(default=""),
    next_goal: str = Form(default=""),
    forbidden_events: str = Form(default=""),
    notes: str = Form(default=""),
):
    """Update a plot anchor."""
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    anchor = PlotAnchorService.get_plot_anchor(db, anchor_id)
    if not anchor:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    errors = {}
    if not name.strip():
        errors["name"] = "名称不能为空"

    if errors:
        return templates.TemplateResponse(request, "context/anchor_form.html", {
            "world": world,
            "anchor": anchor,
            "errors": errors,
            "form_data": {
                "name": name, "stage": stage, "volume_name": volume_name,
                "protagonist_age": protagonist_age,
                "current_location": current_location,
                "occurred_events": occurred_events,
                "hidden_secrets": hidden_secrets,
                "current_conflict": current_conflict,
                "character_states": character_states,
                "faction_states": faction_states,
                "current_goal": current_goal, "next_goal": next_goal,
                "forbidden_events": forbidden_events, "notes": notes,
            },
            "is_edit": True,
        }, status_code=422)

    PlotAnchorService.update_plot_anchor(
        db=db,
        anchor_id=anchor_id,
        name=name,
        stage=stage,
        volume_name=volume_name,
        protagonist_age=protagonist_age,
        current_location=current_location,
        occurred_events=occurred_events,
        hidden_secrets=hidden_secrets,
        current_conflict=current_conflict,
        character_states=character_states,
        faction_states=faction_states,
        current_goal=current_goal,
        next_goal=next_goal,
        forbidden_events=forbidden_events,
        notes=notes,
    )

    return RedirectResponse(
        url=f"/worlds/{world_id}/context/anchors", status_code=303
    )


@router.post("/anchors/{anchor_id}/delete", response_class=HTMLResponse)
async def delete_anchor(
    request: Request, world_id: int, anchor_id: int, db: Session = Depends(get_db)
):
    """Delete a plot anchor."""
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    success = PlotAnchorService.delete_plot_anchor(db, anchor_id)
    if not success:
        anchors = PlotAnchorService.list_plot_anchors_by_world(db, world_id)
        return templates.TemplateResponse(request, "context/anchors.html", {
            "world": world,
            "anchors": anchors,
            "error": "无法删除该剧情时间点：它正在被某个创作上下文包引用。请先移除引用后再删除。",
        })

    return RedirectResponse(
        url=f"/worlds/{world_id}/context/anchors", status_code=303
    )


# ============================================================
# Context Packages
# ============================================================

@router.get("/packages", response_class=HTMLResponse)
async def list_packages(request: Request, world_id: int, db: Session = Depends(get_db)):
    """List context packages for this world."""
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    packages = ContextPackageService.list_context_packages_by_world(db, world_id)

    return templates.TemplateResponse(request, "context/packages.html", {
        "world": world,
        "packages": packages,
    })


@router.get("/packages/new", response_class=HTMLResponse)
async def new_package_form(request: Request, world_id: int, db: Session = Depends(get_db)):
    """Show create context package form."""
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    sim_records = ContextPackageService.list_eligible_simulation_records(db, world_id)
    style_profiles = StyleProfileService.list_available_style_profiles_for_world(db, world_id)
    plot_anchors = PlotAnchorService.list_plot_anchors_by_world(db, world_id)

    return templates.TemplateResponse(request, "context/package_form.html", {
        "world": world,
        "pkg": None,
        "sim_records": sim_records,
        "style_profiles": style_profiles,
        "plot_anchors": plot_anchors,
        "errors": {},
        "form_data": {},
        "is_edit": False,
    })


@router.post("/packages/new", response_class=HTMLResponse)
async def create_package(
    request: Request,
    world_id: int,
    db: Session = Depends(get_db),
    name: str = Form(default=""),
    description: str = Form(default=""),
    simulation_record_id: str = Form(default=""),
    style_profile_id: str = Form(default=""),
    plot_anchor_id: str = Form(default=""),
    generation_type: str = Form(default=""),
    strict_canon: str = Form(default=""),
    strict_style: str = Form(default=""),
    include_branches: str = Form(default=""),
    include_non_canon: str = Form(default=""),
    target_words: str = Form(default=""),
    extra_requirements: str = Form(default=""),
    is_default: str = Form(default=""),
):
    """Create a new context package."""
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    errors = {}
    if not name.strip():
        errors["name"] = "名称不能为空"

    sim_records = ContextPackageService.list_eligible_simulation_records(db, world_id)
    style_profiles = StyleProfileService.list_available_style_profiles_for_world(db, world_id)
    plot_anchors = PlotAnchorService.list_plot_anchors_by_world(db, world_id)

    if errors:
        return templates.TemplateResponse(request, "context/package_form.html", {
            "world": world,
            "pkg": None,
            "sim_records": sim_records,
            "style_profiles": style_profiles,
            "plot_anchors": plot_anchors,
            "errors": errors,
            "form_data": {
                "name": name, "description": description,
                "simulation_record_id": simulation_record_id,
                "style_profile_id": style_profile_id,
                "plot_anchor_id": plot_anchor_id,
                "generation_type": generation_type,
                "strict_canon": strict_canon, "strict_style": strict_style,
                "include_branches": include_branches,
                "include_non_canon": include_non_canon,
                "target_words": target_words,
                "extra_requirements": extra_requirements,
                "is_default": is_default,
            },
            "is_edit": False,
        }, status_code=422)

    try:
        sim_id = int(simulation_record_id) if simulation_record_id else None
        style_id = int(style_profile_id) if style_profile_id else None
        anchor_id = int(plot_anchor_id) if plot_anchor_id else None

        ContextPackageService.create_context_package(
            db=db,
            world_id=world_id,
            name=name,
            description=description,
            simulation_record_id=sim_id,
            style_profile_id=style_id,
            plot_anchor_id=anchor_id,
            generation_type=generation_type,
            strict_canon=strict_canon == "1" or strict_canon == "on",
            strict_style=strict_style == "1" or strict_style == "on",
            include_branches=include_branches == "1" or include_branches == "on",
            include_non_canon=include_non_canon == "1" or include_non_canon == "on",
            target_words=target_words,
            extra_requirements=extra_requirements,
            is_default=is_default == "1",
        )
    except ValueError as e:
        return templates.TemplateResponse(request, "context/package_form.html", {
            "world": world,
            "pkg": None,
            "sim_records": sim_records,
            "style_profiles": style_profiles,
            "plot_anchors": plot_anchors,
            "errors": {"submit": str(e)},
            "form_data": {
                "name": name, "description": description,
                "simulation_record_id": simulation_record_id,
                "style_profile_id": style_profile_id,
                "plot_anchor_id": plot_anchor_id,
                "generation_type": generation_type,
                "strict_canon": strict_canon, "strict_style": strict_style,
                "include_branches": include_branches,
                "include_non_canon": include_non_canon,
                "target_words": target_words,
                "extra_requirements": extra_requirements,
                "is_default": is_default,
            },
            "is_edit": False,
        })

    return RedirectResponse(
        url=f"/worlds/{world_id}/context/packages", status_code=303
    )


@router.get("/packages/{package_id}", response_class=HTMLResponse)
async def package_detail(
    request: Request, world_id: int, package_id: int, db: Session = Depends(get_db)
):
    """Show context package detail with preview."""
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    pkg = ContextPackageService.get_context_package(db, package_id)
    if not pkg or pkg.world_id != world_id:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    preview = ContextPackageService.build_context_package_preview(db, package_id)

    return templates.TemplateResponse(request, "context/package_detail.html", {
        "world": world,
        "pkg": pkg,
        "preview": preview,
    })


@router.get("/packages/{package_id}/edit", response_class=HTMLResponse)
async def edit_package_form(
    request: Request, world_id: int, package_id: int, db: Session = Depends(get_db)
):
    """Show edit context package form."""
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    pkg = ContextPackageService.get_context_package(db, package_id)
    if not pkg or pkg.world_id != world_id:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    sim_records = ContextPackageService.list_eligible_simulation_records(db, world_id)
    style_profiles = StyleProfileService.list_available_style_profiles_for_world(db, world_id)
    plot_anchors = PlotAnchorService.list_plot_anchors_by_world(db, world_id)

    return templates.TemplateResponse(request, "context/package_form.html", {
        "world": world,
        "pkg": pkg,
        "sim_records": sim_records,
        "style_profiles": style_profiles,
        "plot_anchors": plot_anchors,
        "errors": {},
        "form_data": {},
        "is_edit": True,
    })


@router.post("/packages/{package_id}/edit", response_class=HTMLResponse)
async def update_package(
    request: Request,
    world_id: int,
    package_id: int,
    db: Session = Depends(get_db),
    name: str = Form(default=""),
    description: str = Form(default=""),
    simulation_record_id: str = Form(default=""),
    style_profile_id: str = Form(default=""),
    plot_anchor_id: str = Form(default=""),
    generation_type: str = Form(default=""),
    strict_canon: str = Form(default=""),
    strict_style: str = Form(default=""),
    include_branches: str = Form(default=""),
    include_non_canon: str = Form(default=""),
    target_words: str = Form(default=""),
    extra_requirements: str = Form(default=""),
    is_default: str = Form(default=""),
):
    """Update a context package."""
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    pkg = ContextPackageService.get_context_package(db, package_id)
    if not pkg or pkg.world_id != world_id:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    errors = {}
    if not name.strip():
        errors["name"] = "名称不能为空"

    sim_records = ContextPackageService.list_eligible_simulation_records(db, world_id)
    style_profiles = StyleProfileService.list_available_style_profiles_for_world(db, world_id)
    plot_anchors = PlotAnchorService.list_plot_anchors_by_world(db, world_id)

    if errors:
        return templates.TemplateResponse(request, "context/package_form.html", {
            "world": world,
            "pkg": pkg,
            "sim_records": sim_records,
            "style_profiles": style_profiles,
            "plot_anchors": plot_anchors,
            "errors": errors,
            "form_data": {
                "name": name, "description": description,
                "simulation_record_id": simulation_record_id,
                "style_profile_id": style_profile_id,
                "plot_anchor_id": plot_anchor_id,
                "generation_type": generation_type,
                "strict_canon": strict_canon, "strict_style": strict_style,
                "include_branches": include_branches,
                "include_non_canon": include_non_canon,
                "target_words": target_words,
                "extra_requirements": extra_requirements,
                "is_default": is_default,
            },
            "is_edit": True,
        }, status_code=422)

    try:
        sim_id = int(simulation_record_id) if simulation_record_id else 0
        style_id = int(style_profile_id) if style_profile_id else 0
        anchor_id = int(plot_anchor_id) if plot_anchor_id else 0

        ContextPackageService.update_context_package(
            db=db,
            package_id=package_id,
            world_id=world_id,
            name=name,
            description=description,
            simulation_record_id=sim_id,
            style_profile_id=style_id,
            plot_anchor_id=anchor_id,
            generation_type=generation_type,
            strict_canon=strict_canon == "1" or strict_canon == "on",
            strict_style=strict_style == "1" or strict_style == "on",
            include_branches=include_branches == "1" or include_branches == "on",
            include_non_canon=include_non_canon == "1" or include_non_canon == "on",
            target_words=target_words,
            extra_requirements=extra_requirements,
            is_default=is_default == "1",
        )
    except ValueError as e:
        return templates.TemplateResponse(request, "context/package_form.html", {
            "world": world,
            "pkg": pkg,
            "sim_records": sim_records,
            "style_profiles": style_profiles,
            "plot_anchors": plot_anchors,
            "errors": {"submit": str(e)},
            "form_data": {
                "name": name, "description": description,
                "simulation_record_id": simulation_record_id,
                "style_profile_id": style_profile_id,
                "plot_anchor_id": plot_anchor_id,
                "generation_type": generation_type,
                "strict_canon": strict_canon, "strict_style": strict_style,
                "include_branches": include_branches,
                "include_non_canon": include_non_canon,
                "target_words": target_words,
                "extra_requirements": extra_requirements,
                "is_default": is_default,
            },
            "is_edit": True,
        })

    return RedirectResponse(
        url=f"/worlds/{world_id}/context/packages", status_code=303
    )


@router.post("/packages/{package_id}/delete", response_class=HTMLResponse)
async def delete_package(
    request: Request, world_id: int, package_id: int, db: Session = Depends(get_db)
):
    """Delete a context package."""
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    pkg = ContextPackageService.get_context_package(db, package_id)
    if not pkg or pkg.world_id != world_id:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    ContextPackageService.delete_context_package(db, package_id)

    return RedirectResponse(
        url=f"/worlds/{world_id}/context/packages", status_code=303
    )
