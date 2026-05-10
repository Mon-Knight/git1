"""
AI World Engine - World Routes
CRUD routes for world management.
"""

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.world_service import WorldService
from app.services.world_dashboard_service import WorldDashboardService
from app.config import settings

router = APIRouter(prefix="/worlds")

# Template directory
templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


@router.get("", response_class=HTMLResponse)
async def list_worlds(request: Request, db: Session = Depends(get_db)):
    """List all worlds."""
    worlds = WorldService.list_worlds(db)
    return templates.TemplateResponse(
        request,
        "worlds/list.html",
        {"worlds": worlds, "active_nav": "worlds", "app_version": settings.VERSION},
    )


@router.get("/new", response_class=HTMLResponse)
async def new_world_form(request: Request):
    """Show the create world form."""
    return templates.TemplateResponse(
        request,
        "worlds/new.html",
        {"errors": {}},
    )


@router.post("")
async def create_world(
    request: Request,
    name: str = Form(default=""),
    world_type: str = Form(default=""),
    description: str = Form(default=""),
    current_era: str = Form(default=""),
    tone: str = Form(default=""),
    db: Session = Depends(get_db),
):
    """Create a new world."""
    errors = validate_world_form(name, world_type, current_era, tone)

    if errors:
        return templates.TemplateResponse(
            request,
            "worlds/new.html",
            {
                "errors": errors,
                "form_data": {
                    "name": name,
                    "world_type": world_type,
                    "description": description,
                    "current_era": current_era,
                    "tone": tone,
                },
            },
            status_code=422,
        )

    WorldService.create_world(
        db,
        name=name.strip(),
        world_type=world_type.strip(),
        description=description.strip(),
        current_era=current_era.strip(),
        tone=tone.strip(),
    )
    return RedirectResponse(url="/worlds", status_code=303)


@router.get("/{world_id}", response_class=HTMLResponse)
async def world_detail(request: Request, world_id: int, db: Session = Depends(get_db)):
    """Show world console dashboard."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request,
            "worlds/404.html",
            {"world_id": world_id},
            status_code=404,
        )
    summary = WorldDashboardService.get_world_dashboard_summary(db, world_id)
    recent = WorldDashboardService.get_world_recent_activity(db, world_id)
    recommendations = WorldDashboardService.get_world_recommendations(db, world_id)
    quick_actions = WorldDashboardService.get_world_quick_actions(world_id)

    return templates.TemplateResponse(
        request,
        "worlds/detail.html",
        {
            "world": world,
            "active_nav": "worlds",
            "current_world": world,
            "app_version": settings.VERSION,
            "summary": summary,
            "recent_activity": recent,
            "recommendations": recommendations,
            "quick_actions": quick_actions,
        },
    )


@router.get("/{world_id}/edit", response_class=HTMLResponse)
async def edit_world_form(request: Request, world_id: int, db: Session = Depends(get_db)):
    """Show the edit world form."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request,
            "worlds/404.html",
            {"world_id": world_id},
            status_code=404,
        )
    return templates.TemplateResponse(
        request,
        "worlds/edit.html",
        {"world": world, "errors": {}},
    )


@router.post("/{world_id}/edit")
async def update_world(
    request: Request,
    world_id: int,
    name: str = Form(default=""),
    world_type: str = Form(default=""),
    description: str = Form(default=""),
    current_era: str = Form(default=""),
    tone: str = Form(default=""),
    db: Session = Depends(get_db),
):
    """Update an existing world."""
    errors = validate_world_form(name, world_type, current_era, tone)

    if errors:
        world = WorldService.get_world(db, world_id)
        if not world:
            return templates.TemplateResponse(
                request,
                "worlds/404.html",
                {"world_id": world_id},
                status_code=404,
            )
        return templates.TemplateResponse(
            request,
            "worlds/edit.html",
            {
                "world": world,
                "errors": errors,
            },
            status_code=422,
        )

    updated = WorldService.update_world(
        db,
        world_id=world_id,
        name=name.strip(),
        world_type=world_type.strip(),
        description=description.strip(),
        current_era=current_era.strip(),
        tone=tone.strip(),
    )

    if not updated:
        return templates.TemplateResponse(
            request,
            "worlds/404.html",
            {"world_id": world_id},
            status_code=404,
        )

    return RedirectResponse(url=f"/worlds/{world_id}", status_code=303)


@router.post("/{world_id}/delete")
async def delete_world(world_id: int, db: Session = Depends(get_db)):
    """Delete a world."""
    WorldService.delete_world(db, world_id)
    return RedirectResponse(url="/worlds", status_code=303)


def validate_world_form(name: str, world_type: str, current_era: str, tone: str) -> dict:
    """Validate world form data. Returns dict of field -> error message."""
    errors = {}

    if not name or not name.strip():
        errors["name"] = "世界名称不能为空"
    elif len(name.strip()) > 100:
        errors["name"] = "世界名称不能超过100个字符"

    if world_type and len(world_type.strip()) > 50:
        errors["world_type"] = "世界类型不能超过50个字符"

    if current_era and len(current_era.strip()) > 100:
        errors["current_era"] = "当前时代不能超过100个字符"

    if tone and len(tone.strip()) > 100:
        errors["tone"] = "世界基调不能超过100个字符"

    return errors
