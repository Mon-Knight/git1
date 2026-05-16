"""
AI World Engine - Simulation Routes
AI simulation page and submission.
"""

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.services.world_service import WorldService
from app.services.simulation_service import SimulationService
from app.services.world_context_service import WorldContextService
from app.services.settings_service import SettingsService
from app.services.ai.model_router import ModelRouter

router = APIRouter(prefix="/worlds/{world_id}/simulation")

templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


def _get_ai_mode_info(db: Session) -> str:
    """Return a human-readable description of the current AI mode."""
    config = SettingsService.get_effective_config(db)
    if not config["ai_enable_live"] or config["ai_provider"] == "mock":
        return "🔵 当前使用 Mock AI，适合测试和演示。前往 <a href=\"/settings/ai\">AI 设置</a> 配置真实 AI。"
    model = config.get("ai_model", "未指定")
    base_url = config.get("ai_base_url", "未指定")
    return f"🟢 当前模型: {model} | Base URL: {base_url}"


def _render_template(request, template, db=None, status_code=200, **kwargs):
    """Helper to always pass ai_mode_info, active_nav, current_world, and app_version."""
    db = db or kwargs.pop("db")
    world = kwargs.get("world")
    defaults = {
        "ai_mode_info": _get_ai_mode_info(db),
        "active_nav": "simulation",
        "app_version": settings.VERSION,
    }
    # v2.0.1.3: Ensure current_world is always passed for sidebar context
    if "current_world" not in kwargs and world is not None:
        defaults["current_world"] = world
    defaults.update(kwargs)
    return templates.TemplateResponse(request, template, defaults, status_code=status_code)


@router.get("", response_class=HTMLResponse)
async def simulation_page(request: Request, world_id: int, db: Session = Depends(get_db)):
    """Show the AI simulation page."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    context = WorldContextService.build_world_context(db, world_id)
    context_snapshot = WorldContextService.build_context_snapshot(context)

    return _render_template(request, "simulation/index.html", db=db,
        world=world,
        context_snapshot=context_snapshot,
        errors={},
        result=None,
    )


@router.post("", response_class=HTMLResponse)
async def run_simulation(
    request: Request,
    world_id: int,
    question: str = Form(default=""),
    simulation_type: str = Form(default=""),
    db: Session = Depends(get_db),
):
    """Submit a simulation question and show the result."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    errors = {}
    if not question or not question.strip():
        errors["question"] = "推演问题不能为空"
    elif len(question.strip()) > 1000:
        errors["question"] = "推演问题不能超过1000个字符"

    if errors:
        context = WorldContextService.build_world_context(db, world_id)
        context_snapshot = WorldContextService.build_context_snapshot(context)
        return _render_template(request, "simulation/index.html", db=db,
            world=world,
            context_snapshot=context_snapshot,
            errors=errors,
            form_data={"question": question, "simulation_type": simulation_type},
            result=None,
            status_code=422,
        )

    # Attempt simulation - uses ModelRouter; failure = no record created
    try:
        record = SimulationService.run_simulation(
            db=db,
            world_id=world_id,
            question=question.strip(),
            simulation_type=simulation_type.strip(),
        )

        context = WorldContextService.build_world_context(db, world_id)
        context_snapshot = WorldContextService.build_context_snapshot(context)

        return _render_template(request, "simulation/index.html", db=db,
            world=world,
            context_snapshot=context_snapshot,
            errors={},
            result={
                "id": record.id,
                "question": record.question,
                "simulation_type": record.simulation_type,
                "ai_response": record.ai_response,
                "status": record.status,
                "is_mock": record.is_mock,
                "ai_model": record.ai_model or ("Mock" if record.is_mock else "unknown"),
                "created_at": record.created_at.strftime("%Y-%m-%d %H:%M"),
            },
        )
    except Exception as e:
        context = WorldContextService.build_world_context(db, world_id)
        context_snapshot = WorldContextService.build_context_snapshot(context)
        error_msg = str(e)
        return _render_template(request, "simulation/index.html", db=db,
            world=world,
            context_snapshot=context_snapshot,
            errors={"submit": f"推演失败: {error_msg}"},
            form_data={"question": question, "simulation_type": simulation_type},
            result=None,
        )
