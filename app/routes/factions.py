"""
AI World Engine - Faction Routes
CRUD routes for faction management within a world.
"""

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.faction_service import FactionService
from app.services.world_service import WorldService
from app.services.character_service import CharacterService

router = APIRouter(prefix="/worlds/{world_id}/factions")

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
async def list_factions(request: Request, world_id: int, db: Session = Depends(get_db)):
    world, error = _get_world_or_404(db, world_id, request)
    if error:
        return error
    factions = FactionService.list_factions(db, world_id)
    return templates.TemplateResponse(request, "factions/list.html", {
        "world": world, "factions": factions
    })


@router.get("/new", response_class=HTMLResponse)
async def new_faction_form(request: Request, world_id: int, db: Session = Depends(get_db)):
    world, error = _get_world_or_404(db, world_id, request)
    if error:
        return error
    characters = CharacterService.list_characters(db, world_id)
    return templates.TemplateResponse(request, "factions/new.html", {
        "world": world, "characters": characters, "errors": {}
    })


@router.post("")
async def create_faction(
    request: Request, world_id: int,
    name: str = Form(default=""), faction_type: str = Form(default=""),
    leader_id: str = Form(default=""), goal: str = Form(default=""),
    resources: str = Form(default=""), enemies: str = Form(default=""),
    allies: str = Form(default=""), notes: str = Form(default=""),
    db: Session = Depends(get_db),
):
    world, error = _get_world_or_404(db, world_id, request)
    if error:
        return error

    errors = _validate_name(name)
    if errors:
        characters = CharacterService.list_characters(db, world_id)
        return templates.TemplateResponse(request, "factions/new.html", {
            "world": world, "characters": characters, "errors": errors,
            "form_data": {"name": name, "faction_type": faction_type, "goal": goal,
                          "resources": resources, "enemies": enemies, "allies": allies,
                          "notes": notes, "leader_id": leader_id},
        }, status_code=422)

    lid = int(leader_id) if leader_id and leader_id.strip() else None
    FactionService.create_faction(db, world_id, name.strip(), faction_type.strip(),
                                   lid, goal.strip(), resources.strip(),
                                   enemies.strip(), allies.strip(), notes.strip())
    return RedirectResponse(url=f"/worlds/{world_id}/factions", status_code=303)


@router.get("/{faction_id}", response_class=HTMLResponse)
async def faction_detail(request: Request, world_id: int, faction_id: int, db: Session = Depends(get_db)):
    world, error = _get_world_or_404(db, world_id, request)
    if error:
        return error
    faction = FactionService.get_faction(db, faction_id)
    if not faction or faction.world_id != world_id:
        return templates.TemplateResponse(request, "factions/404.html",
                                          {"world": world, "resource_id": faction_id}, status_code=404)
    return templates.TemplateResponse(request, "factions/detail.html", {
        "world": world, "faction": faction
    })


@router.get("/{faction_id}/edit", response_class=HTMLResponse)
async def edit_faction_form(request: Request, world_id: int, faction_id: int, db: Session = Depends(get_db)):
    world, error = _get_world_or_404(db, world_id, request)
    if error:
        return error
    faction = FactionService.get_faction(db, faction_id)
    if not faction or faction.world_id != world_id:
        return templates.TemplateResponse(request, "factions/404.html",
                                          {"world": world, "resource_id": faction_id}, status_code=404)
    characters = CharacterService.list_characters(db, world_id)
    return templates.TemplateResponse(request, "factions/edit.html", {
        "world": world, "faction": faction, "characters": characters, "errors": {}
    })


@router.post("/{faction_id}/edit")
async def update_faction(
    request: Request, world_id: int, faction_id: int,
    name: str = Form(default=""), faction_type: str = Form(default=""),
    leader_id: str = Form(default=""), goal: str = Form(default=""),
    resources: str = Form(default=""), enemies: str = Form(default=""),
    allies: str = Form(default=""), notes: str = Form(default=""),
    db: Session = Depends(get_db),
):
    world, error = _get_world_or_404(db, world_id, request)
    if error:
        return error

    errors = _validate_name(name)
    if errors:
        faction = FactionService.get_faction(db, faction_id)
        characters = CharacterService.list_characters(db, world_id)
        return templates.TemplateResponse(request, "factions/edit.html", {
            "world": world, "faction": faction, "characters": characters, "errors": errors,
        }, status_code=422)

    lid = int(leader_id) if leader_id and leader_id.strip() else None
    updated = FactionService.update_faction(db, faction_id, name.strip(), faction_type.strip(),
                                             lid, goal.strip(), resources.strip(),
                                             enemies.strip(), allies.strip(), notes.strip())
    if not updated or updated.world_id != world_id:
        return templates.TemplateResponse(request, "factions/404.html",
                                          {"world": world, "resource_id": faction_id}, status_code=404)
    return RedirectResponse(url=f"/worlds/{world_id}/factions/{faction_id}", status_code=303)


@router.post("/{faction_id}/delete")
async def delete_faction(world_id: int, faction_id: int, db: Session = Depends(get_db)):
    FactionService.delete_faction(db, faction_id)
    return RedirectResponse(url=f"/worlds/{world_id}/factions", status_code=303)
