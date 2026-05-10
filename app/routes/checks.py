"""
AI World Engine - Check Routes
Setting conflict checks and character behavior checks.
"""

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.world_service import WorldService
from app.services.character_service import CharacterService
from app.services.check_service import CheckService
from app.services.settings_service import SettingsService

router = APIRouter(prefix="/worlds/{world_id}/checks")

templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


def _get_ai_hint(db: Session) -> str:
    """Return a hint about AI availability for the checks page."""
    config = SettingsService.get_effective_config(db)
    if config.get("ai_enable_live") and config.get("ai_provider") != "mock":
        missing = []
        if not config.get("ai_api_key"):
            missing.append("API Key")
        if not config.get("ai_base_url"):
            missing.append("Base URL")
        if not config.get("ai_model"):
            missing.append("Model")
        if missing:
            return f"AI 配置不完整（缺少 {', '.join(missing)}），AI 补充分析不可用。"
        return "真实 AI 已配置，可在运行规则式检查的同时获得 AI 补充分析。"
    return "当前为 Mock 模式。如需 AI 补充分析，请先前往 <a href=\"/settings/ai\">AI 设置</a> 配置真实 AI。"


@router.get("", response_class=HTMLResponse)
async def checks_index(request: Request, world_id: int, db: Session = Depends(get_db)):
    """Check center page."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )
    return templates.TemplateResponse(request, "checks/index.html", {
        "world": world,
        "ai_hint": _get_ai_hint(db),
    })


@router.get("/conflicts", response_class=HTMLResponse)
async def conflict_check_form(request: Request, world_id: int, db: Session = Depends(get_db)):
    """Setting conflict check form."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )
    return templates.TemplateResponse(request, "checks/conflicts.html", {
        "world": world, "errors": {}, "result": None,
        "ai_hint": _get_ai_hint(db),
    })


@router.post("/conflicts", response_class=HTMLResponse)
async def run_conflict_check(
    request: Request, world_id: int,
    content: str = Form(default=""),
    check_type_rule: str = Form(default=""),
    check_type_event: str = Form(default=""),
    check_type_character: str = Form(default=""),
    check_type_faction: str = Form(default=""),
    check_type_timeline: str = Form(default=""),
    use_ai: str = Form(default=""),
    db: Session = Depends(get_db),
):
    """Run a setting conflict check."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    errors = {}
    if not content or not content.strip():
        errors["content"] = "检查内容不能为空"
    elif len(content.strip()) > 2000:
        errors["content"] = "检查内容不能超过2000个字符"

    if errors:
        return templates.TemplateResponse(request, "checks/conflicts.html", {
            "world": world, "errors": errors,
            "form_data": {"content": content},
            "ai_hint": _get_ai_hint(db),
        }, status_code=422)

    # Build check types
    check_types = []
    if check_type_rule: check_types.append("rule")
    if check_type_event: check_types.append("event")
    if check_type_character: check_types.append("character")
    if check_type_faction: check_types.append("faction")
    if check_type_timeline: check_types.append("timeline")
    if not check_types:
        check_types = ["rule", "event", "character", "faction", "timeline"]

    try:
        result = CheckService.run_conflict_check(
            db, world_id, content.strip(), check_types, use_ai=bool(use_ai)
        )
        return templates.TemplateResponse(request, "checks/conflicts.html", {
            "world": world, "errors": {}, "result": result,
            "form_data": {"content": content},
            "ai_hint": _get_ai_hint(db),
        })
    except Exception as e:
        return templates.TemplateResponse(request, "checks/conflicts.html", {
            "world": world, "errors": {"submit": f"检查出错: {str(e)}"},
            "form_data": {"content": content}, "result": None,
            "ai_hint": _get_ai_hint(db),
        }, status_code=500)


@router.get("/behavior", response_class=HTMLResponse)
async def behavior_check_form(request: Request, world_id: int, db: Session = Depends(get_db)):
    """Character behavior check form."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )
    characters = CharacterService.list_characters(db, world_id)
    return templates.TemplateResponse(request, "checks/behavior.html", {
        "world": world, "characters": characters, "errors": {}, "result": None,
        "ai_hint": _get_ai_hint(db),
    })


@router.post("/behavior", response_class=HTMLResponse)
async def run_behavior_check(
    request: Request, world_id: int,
    character_id: str = Form(default=""),
    behavior: str = Form(default=""),
    context: str = Form(default=""),
    use_ai: str = Form(default=""),
    db: Session = Depends(get_db),
):
    """Run a character behavior check."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    characters = CharacterService.list_characters(db, world_id)

    errors = {}
    if not character_id or not character_id.strip():
        errors["character_id"] = "请选择角色"
    if not behavior or not behavior.strip():
        errors["behavior"] = "行为描述不能为空"
    elif len(behavior.strip()) > 2000:
        errors["behavior"] = "行为描述不能超过2000个字符"

    if errors:
        return templates.TemplateResponse(request, "checks/behavior.html", {
            "world": world, "characters": characters, "errors": errors,
            "form_data": {"character_id": character_id, "behavior": behavior, "context": context},
            "ai_hint": _get_ai_hint(db),
        }, status_code=422)

    cid = int(character_id)
    try:
        result = CheckService.run_behavior_check(
            db, world_id, cid, behavior.strip(), context.strip(), use_ai=bool(use_ai)
        )
        return templates.TemplateResponse(request, "checks/behavior.html", {
            "world": world, "characters": characters, "errors": {}, "result": result,
            "form_data": {"character_id": character_id, "behavior": behavior, "context": context},
            "ai_hint": _get_ai_hint(db),
        })
    except Exception as e:
        return templates.TemplateResponse(request, "checks/behavior.html", {
            "world": world, "characters": characters, "errors": {"submit": f"检查出错: {str(e)}"},
            "form_data": {"character_id": character_id, "behavior": behavior, "context": context},
            "result": None,
            "ai_hint": _get_ai_hint(db),
        })
