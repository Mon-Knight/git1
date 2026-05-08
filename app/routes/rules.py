"""
AI World Engine - World Rule Routes
CRUD routes for world rule management within a world.
"""

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.rule_service import RuleService
from app.services.world_service import WorldService

router = APIRouter(prefix="/worlds/{world_id}/rules")

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
async def list_rules(request: Request, world_id: int, db: Session = Depends(get_db)):
    world, error = _get_world_or_404(db, world_id, request)
    if error:
        return error
    rules = RuleService.list_rules(db, world_id)
    return templates.TemplateResponse(request, "rules/list.html", {
        "world": world, "rules": rules
    })


@router.get("/new", response_class=HTMLResponse)
async def new_rule_form(request: Request, world_id: int, db: Session = Depends(get_db)):
    world, error = _get_world_or_404(db, world_id, request)
    if error:
        return error
    return templates.TemplateResponse(request, "rules/new.html", {
        "world": world, "errors": {}
    })


@router.post("")
async def create_rule(
    request: Request, world_id: int,
    name: str = Form(default=""), rule_type: str = Form(default=""),
    content: str = Form(default=""), constraints: str = Form(default=""),
    scope: str = Form(default=""),
    db: Session = Depends(get_db),
):
    world, error = _get_world_or_404(db, world_id, request)
    if error:
        return error

    errors = _validate_name(name)
    if errors:
        return templates.TemplateResponse(request, "rules/new.html", {
            "world": world, "errors": errors,
            "form_data": {"name": name, "rule_type": rule_type, "content": content,
                          "constraints": constraints, "scope": scope},
        }, status_code=422)

    RuleService.create_rule(db, world_id, name.strip(), rule_type.strip(),
                             content.strip(), constraints.strip(), scope.strip())
    return RedirectResponse(url=f"/worlds/{world_id}/rules", status_code=303)


@router.get("/{rule_id}", response_class=HTMLResponse)
async def rule_detail(request: Request, world_id: int, rule_id: int, db: Session = Depends(get_db)):
    world, error = _get_world_or_404(db, world_id, request)
    if error:
        return error
    rule = RuleService.get_rule(db, rule_id)
    if not rule or rule.world_id != world_id:
        return templates.TemplateResponse(request, "rules/404.html",
                                          {"world": world, "resource_id": rule_id}, status_code=404)
    return templates.TemplateResponse(request, "rules/detail.html", {
        "world": world, "rule": rule
    })


@router.get("/{rule_id}/edit", response_class=HTMLResponse)
async def edit_rule_form(request: Request, world_id: int, rule_id: int, db: Session = Depends(get_db)):
    world, error = _get_world_or_404(db, world_id, request)
    if error:
        return error
    rule = RuleService.get_rule(db, rule_id)
    if not rule or rule.world_id != world_id:
        return templates.TemplateResponse(request, "rules/404.html",
                                          {"world": world, "resource_id": rule_id}, status_code=404)
    return templates.TemplateResponse(request, "rules/edit.html", {
        "world": world, "rule": rule, "errors": {}
    })


@router.post("/{rule_id}/edit")
async def update_rule(
    request: Request, world_id: int, rule_id: int,
    name: str = Form(default=""), rule_type: str = Form(default=""),
    content: str = Form(default=""), constraints: str = Form(default=""),
    scope: str = Form(default=""),
    db: Session = Depends(get_db),
):
    world, error = _get_world_or_404(db, world_id, request)
    if error:
        return error

    errors = _validate_name(name)
    if errors:
        rule = RuleService.get_rule(db, rule_id)
        return templates.TemplateResponse(request, "rules/edit.html", {
            "world": world, "rule": rule, "errors": errors,
        }, status_code=422)

    updated = RuleService.update_rule(db, rule_id, name.strip(), rule_type.strip(),
                                       content.strip(), constraints.strip(), scope.strip())
    if not updated or updated.world_id != world_id:
        return templates.TemplateResponse(request, "rules/404.html",
                                          {"world": world, "resource_id": rule_id}, status_code=404)
    return RedirectResponse(url=f"/worlds/{world_id}/rules/{rule_id}", status_code=303)


@router.post("/{rule_id}/delete")
async def delete_rule(world_id: int, rule_id: int, db: Session = Depends(get_db)):
    RuleService.delete_rule(db, rule_id)
    return RedirectResponse(url=f"/worlds/{world_id}/rules", status_code=303)
