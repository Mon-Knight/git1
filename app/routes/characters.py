"""
AI World Engine - Character Routes
CRUD routes for character management within a world.
"""

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.character_service import CharacterService
from app.services.world_service import WorldService
from app.services.faction_service import FactionService

router = APIRouter(prefix="/worlds/{world_id}/characters")

templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


def _get_world_or_404(db: Session, world_id: int, request: Request):
    """Helper: get world or return 404 template."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return None, templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )
    return world, None


def _validate_name(name: str) -> dict:
    """Validate name field."""
    errors = {}
    if not name or not name.strip():
        errors["name"] = "名称不能为空"
    elif len(name.strip()) > 100:
        errors["name"] = "名称不能超过100个字符"
    return errors


@router.get("", response_class=HTMLResponse)
async def list_characters(request: Request, world_id: int, db: Session = Depends(get_db)):
    world, error = _get_world_or_404(db, world_id, request)
    if error:
        return error
    characters = CharacterService.list_characters(db, world_id)
    return templates.TemplateResponse(request, "characters/list.html", {
        "world": world, "characters": characters
    })


@router.get("/new", response_class=HTMLResponse)
async def new_character_form(request: Request, world_id: int, db: Session = Depends(get_db)):
    world, error = _get_world_or_404(db, world_id, request)
    if error:
        return error
    factions = FactionService.list_factions(db, world_id)
    return templates.TemplateResponse(request, "characters/new.html", {
        "world": world, "factions": factions, "errors": {}
    })


@router.post("")
async def create_character(
    request: Request, world_id: int,
    name: str = Form(default=""), role: str = Form(default=""),
    faction_id: str = Form(default=""), personality: str = Form(default=""),
    goal: str = Form(default=""), abilities: str = Form(default=""),
    current_status: str = Form(default="存活"), notes: str = Form(default=""),
    db: Session = Depends(get_db),
):
    world, error = _get_world_or_404(db, world_id, request)
    if error:
        return error

    errors = _validate_name(name)
    if errors:
        factions = FactionService.list_factions(db, world_id)
        return templates.TemplateResponse(request, "characters/new.html", {
            "world": world, "factions": factions, "errors": errors,
            "form_data": {"name": name, "role": role, "personality": personality,
                          "goal": goal, "abilities": abilities, "current_status": current_status,
                          "notes": notes, "faction_id": faction_id},
        }, status_code=422)

    fid = int(faction_id) if faction_id and faction_id.strip() else None
    CharacterService.create_character(db, world_id, name.strip(), role.strip(),
                                       fid, personality.strip(), goal.strip(),
                                       abilities.strip(), current_status.strip(), notes.strip())
    return RedirectResponse(url=f"/worlds/{world_id}/characters", status_code=303)


@router.get("/{character_id}", response_class=HTMLResponse)
async def character_detail(request: Request, world_id: int, character_id: int, db: Session = Depends(get_db)):
    world, error = _get_world_or_404(db, world_id, request)
    if error:
        return error
    character = CharacterService.get_character(db, character_id)
    if not character or character.world_id != world_id:
        return templates.TemplateResponse(request, "characters/404.html",
                                          {"world": world, "resource_id": character_id}, status_code=404)
    return templates.TemplateResponse(request, "characters/detail.html", {
        "world": world, "character": character
    })


@router.get("/{character_id}/edit", response_class=HTMLResponse)
async def edit_character_form(request: Request, world_id: int, character_id: int, db: Session = Depends(get_db)):
    world, error = _get_world_or_404(db, world_id, request)
    if error:
        return error
    character = CharacterService.get_character(db, character_id)
    if not character or character.world_id != world_id:
        return templates.TemplateResponse(request, "characters/404.html",
                                          {"world": world, "resource_id": character_id}, status_code=404)
    factions = FactionService.list_factions(db, world_id)
    return templates.TemplateResponse(request, "characters/edit.html", {
        "world": world, "character": character, "factions": factions, "errors": {}
    })


@router.post("/{character_id}/edit")
async def update_character(
    request: Request, world_id: int, character_id: int,
    name: str = Form(default=""), role: str = Form(default=""),
    faction_id: str = Form(default=""), personality: str = Form(default=""),
    goal: str = Form(default=""), abilities: str = Form(default=""),
    current_status: str = Form(default="存活"), notes: str = Form(default=""),
    db: Session = Depends(get_db),
):
    world, error = _get_world_or_404(db, world_id, request)
    if error:
        return error

    errors = _validate_name(name)
    if errors:
        character = CharacterService.get_character(db, character_id)
        factions = FactionService.list_factions(db, world_id)
        return templates.TemplateResponse(request, "characters/edit.html", {
            "world": world, "character": character, "factions": factions, "errors": errors,
        }, status_code=422)

    fid = int(faction_id) if faction_id and faction_id.strip() else None
    updated = CharacterService.update_character(db, character_id, name.strip(), role.strip(),
                                                 fid, personality.strip(), goal.strip(),
                                                 abilities.strip(), current_status.strip(), notes.strip())
    if not updated or updated.world_id != world_id:
        return templates.TemplateResponse(request, "characters/404.html",
                                          {"world": world, "resource_id": character_id}, status_code=404)
    return RedirectResponse(url=f"/worlds/{world_id}/characters/{character_id}", status_code=303)


@router.post("/{character_id}/delete")
async def delete_character(world_id: int, character_id: int, db: Session = Depends(get_db)):
    CharacterService.delete_character(db, character_id)
    return RedirectResponse(url=f"/worlds/{world_id}/characters", status_code=303)
