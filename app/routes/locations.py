"""
AI World Engine - Location Routes
CRUD routes for location management within a world.
"""

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.location_service import LocationService
from app.services.world_service import WorldService
from app.services.faction_service import FactionService

router = APIRouter(prefix="/worlds/{world_id}/locations")

templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


def _get_world_or_404(db: Session, world_id: int, request: Request):
    world = WorldService.get_world(db, world_id)
    if not world:
        return None, templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )
    return world, None


def _validate_name(name: str) -> dict:
    errors = {}
    if not name or not name.strip():
        errors["name"] = "名称不能为空"
    elif len(name.strip()) > 100:
        errors["name"] = "名称不能超过100个字符"
    return errors


@router.get("", response_class=HTMLResponse)
async def list_locations(request: Request, world_id: int, db: Session = Depends(get_db)):
    world, error = _get_world_or_404(db, world_id, request)
    if error:
        return error
    locations = LocationService.list_locations(db, world_id)
    return templates.TemplateResponse(request, "locations/list.html", {
        "world": world, "locations": locations
    })


@router.get("/new", response_class=HTMLResponse)
async def new_location_form(request: Request, world_id: int, db: Session = Depends(get_db)):
    world, error = _get_world_or_404(db, world_id, request)
    if error:
        return error
    factions = FactionService.list_factions(db, world_id)
    return templates.TemplateResponse(request, "locations/new.html", {
        "world": world, "factions": factions, "errors": {}
    })


@router.post("")
async def create_location(
    request: Request, world_id: int,
    name: str = Form(default=""), location_type: str = Form(default=""),
    region: str = Form(default=""), description: str = Form(default=""),
    controlling_faction_id: str = Form(default=""), important_events: str = Form(default=""),
    db: Session = Depends(get_db),
):
    world, error = _get_world_or_404(db, world_id, request)
    if error:
        return error

    errors = _validate_name(name)
    if errors:
        factions = FactionService.list_factions(db, world_id)
        return templates.TemplateResponse(request, "locations/new.html", {
            "world": world, "factions": factions, "errors": errors,
            "form_data": {"name": name, "location_type": location_type, "region": region,
                          "description": description, "important_events": important_events,
                          "controlling_faction_id": controlling_faction_id},
        }, status_code=422)

    cfid = int(controlling_faction_id) if controlling_faction_id and controlling_faction_id.strip() else None
    LocationService.create_location(db, world_id, name.strip(), location_type.strip(),
                                     region.strip(), description.strip(), cfid, important_events.strip())
    return RedirectResponse(url=f"/worlds/{world_id}/locations", status_code=303)


@router.get("/{location_id}", response_class=HTMLResponse)
async def location_detail(request: Request, world_id: int, location_id: int, db: Session = Depends(get_db)):
    world, error = _get_world_or_404(db, world_id, request)
    if error:
        return error
    location = LocationService.get_location(db, location_id)
    if not location or location.world_id != world_id:
        return templates.TemplateResponse(request, "locations/404.html",
                                          {"world": world, "resource_id": location_id}, status_code=404)
    return templates.TemplateResponse(request, "locations/detail.html", {
        "world": world, "location": location
    })


@router.get("/{location_id}/edit", response_class=HTMLResponse)
async def edit_location_form(request: Request, world_id: int, location_id: int, db: Session = Depends(get_db)):
    world, error = _get_world_or_404(db, world_id, request)
    if error:
        return error
    location = LocationService.get_location(db, location_id)
    if not location or location.world_id != world_id:
        return templates.TemplateResponse(request, "locations/404.html",
                                          {"world": world, "resource_id": location_id}, status_code=404)
    factions = FactionService.list_factions(db, world_id)
    return templates.TemplateResponse(request, "locations/edit.html", {
        "world": world, "location": location, "factions": factions, "errors": {}
    })


@router.post("/{location_id}/edit")
async def update_location(
    request: Request, world_id: int, location_id: int,
    name: str = Form(default=""), location_type: str = Form(default=""),
    region: str = Form(default=""), description: str = Form(default=""),
    controlling_faction_id: str = Form(default=""), important_events: str = Form(default=""),
    db: Session = Depends(get_db),
):
    world, error = _get_world_or_404(db, world_id, request)
    if error:
        return error

    errors = _validate_name(name)
    if errors:
        location = LocationService.get_location(db, location_id)
        factions = FactionService.list_factions(db, world_id)
        return templates.TemplateResponse(request, "locations/edit.html", {
            "world": world, "location": location, "factions": factions, "errors": errors,
        }, status_code=422)

    cfid = int(controlling_faction_id) if controlling_faction_id and controlling_faction_id.strip() else None
    updated = LocationService.update_location(db, location_id, name.strip(), location_type.strip(),
                                               region.strip(), description.strip(), cfid, important_events.strip())
    if not updated or updated.world_id != world_id:
        return templates.TemplateResponse(request, "locations/404.html",
                                          {"world": world, "resource_id": location_id}, status_code=404)
    return RedirectResponse(url=f"/worlds/{world_id}/locations/{location_id}", status_code=303)


@router.post("/{location_id}/delete")
async def delete_location(world_id: int, location_id: int, db: Session = Depends(get_db)):
    LocationService.delete_location(db, location_id)
    return RedirectResponse(url=f"/worlds/{world_id}/locations", status_code=303)
