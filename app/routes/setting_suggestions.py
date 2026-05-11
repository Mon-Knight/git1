"""
AI World Engine - Setting Suggestion Routes
Routes for AI-generated setting candidate suggestions.
v1.7.9: Generate candidates only, no adoption.
"""

import json
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.services.world_service import WorldService
from app.services.setting_suggestion_service import SettingSuggestionService

router = APIRouter(prefix="/worlds/{world_id}/setting-suggestions")

templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


def _get_world_or_404(db, world_id):
    world = WorldService.get_world(db, world_id)
    return world


@router.get("", response_class=HTMLResponse)
async def list_suggestions(request: Request, world_id: int, db: Session = Depends(get_db)):
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    suggestions = SettingSuggestionService.list_setting_suggestions(db, world_id)
    return templates.TemplateResponse(request, "setting_suggestions/index.html", {
        "world": world, "suggestions": suggestions,
        "current_world": world, "active_nav": "worlds",
        "app_version": settings.VERSION,
    })


@router.get("/new", response_class=HTMLResponse)
async def new_suggestion_form(request: Request, world_id: int, db: Session = Depends(get_db)):
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    return templates.TemplateResponse(request, "setting_suggestions/new.html", {
        "world": world,
        "suggestion_types": SettingSuggestionService.SUGGESTION_TYPES,
        "world_types": SettingSuggestionService.WORLD_TYPES,
        "reference_styles": SettingSuggestionService.REFERENCE_STYLES,
        "current_world": world, "active_nav": "worlds",
        "app_version": settings.VERSION, "errors": {},
    })


@router.post("")
async def create_suggestion(
    request: Request,
    world_id: int,
    suggestion_type: str = Form(default="character"),
    world_type: str = Form(default="western_fantasy"),
    reference_style: str = Form(default="heroic_epic"),
    generation_count: int = Form(default=3),
    user_requirement: str = Form(default=""),
    db: Session = Depends(get_db),
):
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    req_data = {
        "suggestion_type": suggestion_type,
        "world_type": world_type,
        "reference_style": reference_style,
        "generation_count": generation_count,
        "user_requirement": user_requirement,
    }

    # Generate using mock (v1.7.9: always mock in this version)
    try:
        prompt = SettingSuggestionService.build_setting_suggestion_prompt(db, world_id, req_data)
        mock_results = SettingSuggestionService.mock_generate(suggestion_type, generation_count)
        raw_response = json.dumps(mock_results, ensure_ascii=False, indent=2)

        record = SettingSuggestionService.save_setting_suggestion(
            db, world_id, req_data, prompt, raw_response
        )
        return RedirectResponse(
            url=f"/worlds/{world_id}/setting-suggestions/{record.id}",
            status_code=303,
        )
    except Exception as e:
        return templates.TemplateResponse(request, "setting_suggestions/new.html", {
            "world": world, "errors": {"submit": str(e)},
            "suggestion_types": SettingSuggestionService.SUGGESTION_TYPES,
            "world_types": SettingSuggestionService.WORLD_TYPES,
            "reference_styles": SettingSuggestionService.REFERENCE_STYLES,
            "current_world": world, "active_nav": "worlds",
            "app_version": settings.VERSION,
        })


@router.get("/{suggestion_id}", response_class=HTMLResponse)
async def suggestion_detail(
    request: Request, world_id: int, suggestion_id: int, db: Session = Depends(get_db)
):
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    suggestion = SettingSuggestionService.get_setting_suggestion(db, world_id, suggestion_id)
    if not suggestion:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    # Parse result_json for display
    try:
        result_data = json.loads(suggestion.result_json) if suggestion.result_json else {}
    except json.JSONDecodeError:
        result_data = {"raw": suggestion.result_json, "parse_warning": "无法解析"}

    return templates.TemplateResponse(request, "setting_suggestions/detail.html", {
        "world": world, "suggestion": suggestion, "result_data": result_data,
        "current_world": world, "active_nav": "worlds",
        "app_version": settings.VERSION,
    })


# ── v1.7.10 Adoption Routes ────────────────────────────────────────────

from app.services.setting_suggestion_adoption_service import SettingSuggestionAdoptionService


@router.post("/{suggestion_id}/adopt")
async def adopt_suggestion(
    request: Request,
    world_id: int, suggestion_id: int,
    item_index: int = Form(default=0),
    db: Session = Depends(get_db),
):
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    result = SettingSuggestionAdoptionService.adopt(db, world_id, suggestion_id, item_index)
    if not result["ok"]:
        suggestion = SettingSuggestionService.get_setting_suggestion(db, world_id, suggestion_id)
        try:
            result_data = json.loads(suggestion.result_json) if suggestion and suggestion.result_json else {}
        except json.JSONDecodeError:
            result_data = {}
        return templates.TemplateResponse(request, "setting_suggestions/detail.html", {
            "world": world, "suggestion": suggestion, "result_data": result_data,
            "current_world": world, "active_nav": "worlds",
            "app_version": settings.VERSION,
            "error": result["error"],
        })

    return RedirectResponse(
        url=f"/worlds/{world_id}/setting-suggestions/{suggestion_id}",
        status_code=303,
    )


@router.get("/{suggestion_id}/edit-adopt", response_class=HTMLResponse)
async def edit_adopt_form(
    request: Request, world_id: int, suggestion_id: int,
    item_index: int = 0,
    db: Session = Depends(get_db),
):
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    suggestion = SettingSuggestionService.get_setting_suggestion(db, world_id, suggestion_id)
    if not suggestion:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    items = SettingSuggestionAdoptionService.extract_items(suggestion)
    if item_index < 0 or item_index >= len(items):
        return templates.TemplateResponse(request, "setting_suggestions/edit_adopt.html", {
            "world": world, "suggestion": suggestion, "item": {},
            "item_index": item_index, "error": f"item_index {item_index} 不合法",
            "current_world": world, "active_nav": "worlds", "app_version": settings.VERSION,
        })

    return templates.TemplateResponse(request, "setting_suggestions/edit_adopt.html", {
        "world": world, "suggestion": suggestion, "item": items[item_index],
        "item_index": item_index,
        "current_world": world, "active_nav": "worlds",
        "app_version": settings.VERSION,
    })


@router.post("/{suggestion_id}/edit-adopt")
async def do_edit_adopt(
    request: Request,
    world_id: int, suggestion_id: int,
    item_index: int = Form(default=0),
    name: str = Form(default=""),
    description: str = Form(default=""),
    db: Session = Depends(get_db),
):
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    if not name.strip():
        suggestion = SettingSuggestionService.get_setting_suggestion(db, world_id, suggestion_id)
        items = SettingSuggestionAdoptionService.extract_items(suggestion) if suggestion else []
        item = items[item_index] if 0 <= item_index < len(items) else {}
        return templates.TemplateResponse(request, "setting_suggestions/edit_adopt.html", {
            "world": world, "suggestion": suggestion, "item": item,
            "item_index": item_index, "error": "名称不能为空",
            "current_world": world, "active_nav": "worlds", "app_version": settings.VERSION,
        })

    edited = {"name": name.strip(), "description": description.strip()}
    # Preserve other candidate fields
    suggestion = SettingSuggestionService.get_setting_suggestion(db, world_id, suggestion_id)
    if suggestion:
        items = SettingSuggestionAdoptionService.extract_items(suggestion)
        if 0 <= item_index < len(items):
            for k, v in items[item_index].items():
                if k not in edited and v:
                    edited[k] = v

    result = SettingSuggestionAdoptionService.adopt_with_edit(
        db, world_id, suggestion_id, item_index, edited
    )
    if not result["ok"]:
        return templates.TemplateResponse(request, "setting_suggestions/edit_adopt.html", {
            "world": world, "suggestion": suggestion, "item": edited,
            "item_index": item_index, "error": result["error"],
            "current_world": world, "active_nav": "worlds", "app_version": settings.VERSION,
        })

    return RedirectResponse(
        url=f"/worlds/{world_id}/setting-suggestions/{suggestion_id}",
        status_code=303,
    )


@router.post("/{suggestion_id}/discard")
async def discard_suggestion(
    request: Request,
    world_id: int, suggestion_id: int,
    db: Session = Depends(get_db),
):
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    result = SettingSuggestionAdoptionService.discard(db, world_id, suggestion_id)
    if not result["ok"]:
        suggestion = SettingSuggestionService.get_setting_suggestion(db, world_id, suggestion_id)
        try:
            result_data = json.loads(suggestion.result_json) if suggestion and suggestion.result_json else {}
        except json.JSONDecodeError:
            result_data = {}
        return templates.TemplateResponse(request, "setting_suggestions/detail.html", {
            "world": world, "suggestion": suggestion, "result_data": result_data,
            "current_world": world, "active_nav": "worlds",
            "app_version": settings.VERSION,
            "error": result["error"],
        })

    return RedirectResponse(
        url=f"/worlds/{world_id}/setting-suggestions/{suggestion_id}",
        status_code=303,
    )
