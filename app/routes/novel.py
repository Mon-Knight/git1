"""
AI World Engine - Novel Engineering Mode Routes
Full-novel evolution direction generation.
"""

import json
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.world_service import WorldService
from app.services.simulation_service import SimulationService
from app.services.world_context_service import WorldContextService
from app.services.settings_service import SettingsService
from app.services.ai.model_router import ModelRouter
from app.services.ai.prompt_builder import PromptBuilder
from app.constants import (
    SIMULATION_TYPE_NOVEL_EVOLUTION,
    NOVEL_FORM_FIELDS,
)

router = APIRouter(prefix="/worlds/{world_id}/novel")

templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


def _get_ai_mode_info(db: Session) -> str:
    """Return a human-readable description of the current AI mode."""
    config = SettingsService.get_effective_config(db)
    if not config["ai_enable_live"] or config["ai_provider"] == "mock":
        return '<div style="background:rgba(108,99,255,0.06);border:1px solid rgba(108,99,255,0.2);border-radius:8px;padding:0.6rem 1rem;margin-bottom:1rem;font-size:0.82rem;color:var(--color-text-muted)">🔵 当前使用 Mock AI。前往 <a href="/settings/ai" style="color:var(--color-primary)">AI 设置</a> 配置真实 AI 模型。</div>'
    model = config.get("ai_model", "未指定")
    base_url = config.get("ai_base_url", "未指定")
    return '<div style="background:rgba(0,212,170,0.06);border:1px solid rgba(0,212,170,0.2);border-radius:8px;padding:0.6rem 1rem;margin-bottom:1rem;font-size:0.82rem;color:var(--color-text-muted)">🟢 当前 AI 模型: <code>{}</code> | Base URL: <code>{}</code></div>'.format(model, base_url)


@router.get("", response_class=HTMLResponse)
async def novel_form_page(request: Request, world_id: int, db: Session = Depends(get_db)):
    """Show the novel engineering form."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    context = WorldContextService.build_world_context(db, world_id)
    context_snapshot = WorldContextService.build_context_snapshot(context)

    return templates.TemplateResponse(request, "novel/form.html", {
        "world": world,
        "context_snapshot": context_snapshot,
        "ai_mode_info": _get_ai_mode_info(db),
        "errors": {},
        "form_data": {},
        "result": None,
    })


@router.post("", response_class=HTMLResponse)
async def run_novel_evolution(
    request: Request,
    world_id: int,
    db: Session = Depends(get_db),
    protagonist_name: str = Form(default=""),
    protagonist_identity: str = Form(default=""),
    protagonist_power: str = Form(default=""),
    protagonist_start: str = Form(default=""),
    main_story_direction: str = Form(default=""),
    core_conflict: str = Form(default=""),
    genre: str = Form(default=""),
    target_word_count: str = Form(default=""),
    volume_count: str = Form(default=""),
    writing_style: str = Form(default=""),
    pacing_preference: str = Form(default=""),
    conflict_density: str = Form(default=""),
    dialogue_ratio: str = Form(default=""),
    description_density: str = Form(default=""),
    information_release: str = Form(default=""),
    banned_patterns: str = Form(default=""),
    extra_requirements: str = Form(default=""),
):
    """Submit novel engineering form and run AI evolution generation."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    # Collect form data
    novel_form = {
        "protagonist_name": protagonist_name.strip(),
        "protagonist_identity": protagonist_identity.strip(),
        "protagonist_power": protagonist_power.strip(),
        "protagonist_start": protagonist_start.strip(),
        "main_story_direction": main_story_direction.strip(),
        "core_conflict": core_conflict.strip(),
        "genre": genre.strip(),
        "target_word_count": target_word_count.strip(),
        "volume_count": volume_count.strip(),
        "writing_style": writing_style.strip(),
        "pacing_preference": pacing_preference.strip(),
        "conflict_density": conflict_density.strip(),
        "dialogue_ratio": dialogue_ratio.strip(),
        "description_density": description_density.strip(),
        "information_release": information_release.strip(),
        "banned_patterns": banned_patterns.strip(),
        "extra_requirements": extra_requirements.strip(),
    }

    # Validation: main_story_direction is required
    errors = {}
    if not novel_form["main_story_direction"]:
        errors["main_story_direction"] = "主线方向不能为空，请填写小说的核心推进方向。"

    context = WorldContextService.build_world_context(db, world_id)
    context_snapshot = WorldContextService.build_context_snapshot(context)

    if errors:
        return templates.TemplateResponse(request, "novel/form.html", {
            "world": world,
            "context_snapshot": context_snapshot,
            "ai_mode_info": _get_ai_mode_info(db),
            "errors": errors,
            "form_data": novel_form,
            "result": None,
        }, status_code=422)

    # Build prompt and run AI
    try:
        client = ModelRouter.get_client(db, "novel_evolution")
        config = SettingsService.get_effective_config(db)

        messages = PromptBuilder.build_novel_evolution_prompt(context, novel_form)
        options = {
            "temperature": config.get("ai_temperature", 0.7),
            "max_tokens": config.get("ai_max_tokens", 2000),
            "timeout": config.get("ai_timeout", 90),
        }

        ai_result = client.generate(messages, options)

        if not ai_result.get("success"):
            error = ai_result.get("error", {})
            raise RuntimeError(error.get("message", "AI 调用失败，请检查 AI 设置配置。"))

        # Build question summary for record
        question_parts = ["[小说工程推演]"]
        if novel_form["protagonist_name"]:
            question_parts.append("主角:" + novel_form["protagonist_name"])
        question_parts.append("主线:" + novel_form["main_story_direction"][:100])
        question_summary = " | ".join(question_parts)

        # Save to simulation_records
        record = SimulationService.create_simulation_record(
            db=db,
            world_id=world_id,
            question=question_summary,
            simulation_type=SIMULATION_TYPE_NOVEL_EVOLUTION,
            context_snapshot=context_snapshot,
            ai_response=ai_result["content"],
            ai_model=ai_result.get("model", "mock"),
            is_mock=ai_result.get("provider") == "mock",
        )

        return templates.TemplateResponse(request, "novel/form.html", {
            "world": world,
            "context_snapshot": context_snapshot,
            "ai_mode_info": _get_ai_mode_info(db),
            "errors": {},
            "form_data": {},
            "result": {
                "id": record.id,
                "question": record.question,
                "ai_response": record.ai_response,
                "status": record.status,
                "is_mock": record.is_mock,
                "ai_model": record.ai_model or ("Mock" if record.is_mock else "unknown"),
                "created_at": record.created_at.strftime("%Y-%m-%d %H:%M"),
            },
        })

    except Exception as e:
        return templates.TemplateResponse(request, "novel/form.html", {
            "world": world,
            "context_snapshot": context_snapshot,
            "ai_mode_info": _get_ai_mode_info(db),
            "errors": {"submit": "推演失败: {}".format(str(e))},
            "form_data": novel_form,
            "result": None,
        })
