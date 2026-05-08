"""
AI World Engine - Event Routes
CRUD routes for historical event management within a world.
"""

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.event_service import EventService
from app.services.world_service import WorldService
from app.services.location_service import LocationService

router = APIRouter(prefix="/worlds/{world_id}/events")

templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


def _get_world_or_404(db: Session, world_id: int, request: Request):
    world = WorldService.get_world(db, world_id)
    if not world:
        return None, templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )
    return world, None


@router.get("", response_class=HTMLResponse)
async def list_events(request: Request, world_id: int, db: Session = Depends(get_db)):
    world, error = _get_world_or_404(db, world_id, request)
    if error:
        return error
    events = EventService.list_events(db, world_id)
    return templates.TemplateResponse(request, "events/list.html", {
        "world": world, "events": events
    })


@router.get("/new", response_class=HTMLResponse)
async def new_event_form(request: Request, world_id: int, db: Session = Depends(get_db)):
    world, error = _get_world_or_404(db, world_id, request)
    if error:
        return error
    locations = LocationService.list_locations(db, world_id)
    return templates.TemplateResponse(request, "events/new.html", {
        "world": world, "locations": locations, "errors": {}
    })


@router.post("")
async def create_event(
    request: Request, world_id: int,
    title: str = Form(default=""), event_time: str = Form(default=""),
    involved_characters: str = Form(default=""), involved_factions: str = Form(default=""),
    location_id: str = Form(default=""), content: str = Form(default=""),
    consequences: str = Form(default=""), is_canon: str = Form(default="true"),
    db: Session = Depends(get_db),
):
    world, error = _get_world_or_404(db, world_id, request)
    if error:
        return error

    errors = {}
    if not title or not title.strip():
        errors["title"] = "事件标题不能为空"
    elif len(title.strip()) > 150:
        errors["title"] = "标题不能超过150个字符"

    if errors:
        locations = LocationService.list_locations(db, world_id)
        return templates.TemplateResponse(request, "events/new.html", {
            "world": world, "locations": locations, "errors": errors,
            "form_data": {"title": title, "event_time": event_time,
                          "involved_characters": involved_characters,
                          "involved_factions": involved_factions,
                          "content": content, "consequences": consequences,
                          "is_canon": is_canon, "location_id": location_id},
        }, status_code=422)

    lid = int(location_id) if location_id and location_id.strip() else None
    canon = is_canon == "true"
    EventService.create_event(
        db, world_id, title.strip(), event_time.strip(),
        involved_characters.strip(), involved_factions.strip(),
        lid, content.strip(), consequences.strip(), canon,
    )
    return RedirectResponse(url=f"/worlds/{world_id}/events", status_code=303)


@router.get("/{event_id}", response_class=HTMLResponse)
async def event_detail(request: Request, world_id: int, event_id: int, db: Session = Depends(get_db)):
    world, error = _get_world_or_404(db, world_id, request)
    if error:
        return error
    event = EventService.get_event(db, event_id)
    if not event or event.world_id != world_id:
        return templates.TemplateResponse(request, "events/404.html",
                                          {"world": world, "resource_id": event_id}, status_code=404)
    return templates.TemplateResponse(request, "events/detail.html", {
        "world": world, "event": event
    })


@router.get("/{event_id}/edit", response_class=HTMLResponse)
async def edit_event_form(request: Request, world_id: int, event_id: int, db: Session = Depends(get_db)):
    world, error = _get_world_or_404(db, world_id, request)
    if error:
        return error
    event = EventService.get_event(db, event_id)
    if not event or event.world_id != world_id:
        return templates.TemplateResponse(request, "events/404.html",
                                          {"world": world, "resource_id": event_id}, status_code=404)
    locations = LocationService.list_locations(db, world_id)
    return templates.TemplateResponse(request, "events/edit.html", {
        "world": world, "event": event, "locations": locations, "errors": {}
    })


@router.post("/{event_id}/edit")
async def update_event(
    request: Request, world_id: int, event_id: int,
    title: str = Form(default=""), event_time: str = Form(default=""),
    involved_characters: str = Form(default=""), involved_factions: str = Form(default=""),
    location_id: str = Form(default=""), content: str = Form(default=""),
    consequences: str = Form(default=""), is_canon: str = Form(default="true"),
    db: Session = Depends(get_db),
):
    world, error = _get_world_or_404(db, world_id, request)
    if error:
        return error

    errors = {}
    if not title or not title.strip():
        errors["title"] = "事件标题不能为空"
    elif len(title.strip()) > 150:
        errors["title"] = "标题不能超过150个字符"

    if errors:
        event = EventService.get_event(db, event_id)
        locations = LocationService.list_locations(db, world_id)
        return templates.TemplateResponse(request, "events/edit.html", {
            "world": world, "event": event, "locations": locations, "errors": errors,
        }, status_code=422)

    lid = int(location_id) if location_id and location_id.strip() else None
    canon = is_canon == "true"
    updated = EventService.update_event(
        db, event_id, title.strip(), event_time.strip(),
        involved_characters.strip(), involved_factions.strip(),
        lid, content.strip(), consequences.strip(), canon,
    )
    if not updated or updated.world_id != world_id:
        return templates.TemplateResponse(request, "events/404.html",
                                          {"world": world, "resource_id": event_id}, status_code=404)
    return RedirectResponse(url=f"/worlds/{world_id}/events/{event_id}", status_code=303)


@router.post("/{event_id}/delete")
async def delete_event(world_id: int, event_id: int, db: Session = Depends(get_db)):
    EventService.delete_event(db, event_id)
    return RedirectResponse(url=f"/worlds/{world_id}/events", status_code=303)
