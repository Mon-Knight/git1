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
from app.services.novel_evolution_service import NovelEvolutionService
from app.config import settings
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
async def novel_overview_page(
    request: Request,
    world_id: int,
    db: Session = Depends(get_db),
):
    """v2.0.1: Show novel engineering overview page."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    # Get world dashboard summary for status counts
    from app.services.world_dashboard_service import WorldDashboardService
    summary = WorldDashboardService.get_world_dashboard_summary(db, world_id)

    # Build recommendations
    recommendations = []
    if summary.get("context_package_count", 0) == 0:
        recommendations.append({
            "title": "创建创作上下文包",
            "desc": "创作上下文包是全书演化的基础，包含风格方案和剧情时间点。",
            "url": "/worlds/" + str(world_id) + "/context/packages/new",
            "label": "创建上下文包",
        })
    elif summary.get("novel_evolution_count", 0) == 0:
        recommendations.append({
            "title": "开始全书演化推演",
            "desc": "已有创作上下文包，可以进行全书演化推演，生成全书主线方案。",
            "url": "/worlds/" + str(world_id) + "/novel/evolution",
            "label": "全书演化",
        })
    elif summary.get("mainline_evolution_count", 0) == 0:
        recommendations.append({
            "title": "审核并采纳主线方案",
            "desc": "已有推演方案，需要审核并采纳一条作为主线方案。",
            "url": "/worlds/" + str(world_id) + "/novel/evolutions",
            "label": "审核方案",
        })
    elif summary.get("volume_outline_count", 0) == 0:
        recommendations.append({
            "title": "生成分卷大纲",
            "desc": "已有主线方案，可基于主线方案生成分卷大纲。",
            "url": "/worlds/" + str(world_id) + "/novel/volume-outlines/new",
            "label": "生成分卷大纲",
        })
    elif summary.get("chapter_outline_count", 0) == 0:
        recommendations.append({
            "title": "生成章节大纲",
            "desc": "已有分卷大纲，可基于分卷生成章节大纲。",
            "url": "/worlds/" + str(world_id) + "/novel/chapter-outlines/new",
            "label": "生成章节大纲",
        })
    elif summary.get("novel_draft_count", 0) == 0:
        recommendations.append({
            "title": "生成正文草稿",
            "desc": "已有章节大纲，可基于章节大纲生成正文草稿。",
            "url": "/worlds/" + str(world_id) + "/novel/drafts/new",
            "label": "生成正文草稿",
        })
    else:
        recommendations.append({
            "title": "查看正文草稿",
            "desc": "已有正文草稿，可继续编辑和完善。正文质量检查将在 v2.1.0 开放。",
            "url": "/worlds/" + str(world_id) + "/novel/drafts",
            "label": "查看草稿",
        })

    return templates.TemplateResponse(request, "novel/overview.html", {
        "world": world,
        "summary": summary,
        "recommendations": recommendations,
        "active_nav": "novel",
        "app_version": settings.VERSION,
    })


@router.post("", response_class=HTMLResponse)
async def run_novel_evolution(
    request: Request,
    world_id: int,
    db: Session = Depends(get_db),
    context_package_id: str = Form(default=""),
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

    # Load available context packages
    from app.services.context_package_service import ContextPackageService
    context_packages = ContextPackageService.list_context_packages_by_world(db, world_id)

    # Load selected context package
    selected_package_id = None
    pkg_context = None
    if context_package_id and context_package_id.strip():
        try:
            pkg_id = int(context_package_id)
            selected_package_id = pkg_id
            pkg_context = ContextPackageService.build_context_for_generation(db, pkg_id)
            if "error" in pkg_context:
                pkg_context = None
            else:
                # Augment context_snapshot with context package info
                import json
                pkg_snapshot = json.dumps(pkg_context, ensure_ascii=False, indent=2)
                context_snapshot = (
                    "【创作上下文包信息】\n" + pkg_snapshot +
                    "\n\n【世界设定快照】\n" + context_snapshot
                )
        except (ValueError, Exception):
            pass

    if errors:
        return templates.TemplateResponse(request, "novel/form.html", {
            "world": world,
            "context_snapshot": context_snapshot,
            "ai_mode_info": _get_ai_mode_info(db),
            "errors": errors,
            "form_data": novel_form,
            "result": None,
            "context_packages": context_packages,
            "selected_package_id": selected_package_id,
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
        if selected_package_id:
            question_parts.append(f"上下文包ID:{selected_package_id}")
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
            "context_packages": context_packages,
            "selected_package_id": selected_package_id,
        })

    except Exception as e:
        return templates.TemplateResponse(request, "novel/form.html", {
            "world": world,
            "context_snapshot": context_snapshot,
            "ai_mode_info": _get_ai_mode_info(db),
            "errors": {"submit": "推演失败: {}".format(str(e))},
            "form_data": novel_form,
            "result": None,
            "context_packages": context_packages,
            "selected_package_id": selected_package_id,
        })


# ================================================================
# v1.7.0: Full-novel Evolution (with Context Package)
# ================================================================

@router.get("/evolution", response_class=HTMLResponse)
async def evolution_form(
    request: Request,
    world_id: int,
    context_package_id: int = None,
    db: Session = Depends(get_db),
):
    """Show the full-novel evolution form with context package support."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    from app.services.context_package_service import ContextPackageService
    context_packages = ContextPackageService.list_context_packages_by_world(db, world_id)

    # If context_package_id is provided, validate it
    selected_pkg = None
    if context_package_id:
        selected_pkg = ContextPackageService.get_context_package(db, context_package_id)
        if not selected_pkg or selected_pkg.world_id != world_id:
            return templates.TemplateResponse(
                request, "worlds/404.html", {"world_id": world_id}, status_code=404
            )

    return templates.TemplateResponse(request, "novel/evolution_form.html", {
        "world": world,
        "active_nav": "novel",
        "current_world": world,
        "app_version": settings.VERSION,
        "context_packages": context_packages,
        "selected_package_id": context_package_id,
        "selected_pkg": selected_pkg,
        "ai_mode_info": _get_ai_mode_info(db),
        "errors": {},
        "form_data": {},
        "result": None,
    })


@router.post("/evolution", response_class=HTMLResponse)
async def run_evolution(
    request: Request,
    world_id: int,
    db: Session = Depends(get_db),
    context_package_id: str = Form(default=""),
    user_goal: str = Form(default=""),
):
    """Run a full-novel evolution generation using a context package."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    from app.services.context_package_service import ContextPackageService
    context_packages = ContextPackageService.list_context_packages_by_world(db, world_id)

    # Build context
    pkg_id = int(context_package_id) if context_package_id and context_package_id.strip() else None

    ctx = NovelEvolutionService.build_novel_evolution_context(db, world_id, pkg_id or 0)
    if ctx.get("error") and pkg_id:
        return templates.TemplateResponse(request, "novel/evolution_form.html", {
            "world": world,
            "active_nav": "novel",
            "current_world": world,
            "app_version": settings.VERSION,
            "context_packages": context_packages,
            "selected_package_id": pkg_id,
            "selected_pkg": None,
            "ai_mode_info": _get_ai_mode_info(db),
            "errors": {"submit": ctx["error"]},
            "form_data": {"user_goal": user_goal},
            "result": None,
        })

    # Build prompt
    messages = NovelEvolutionService.build_novel_evolution_prompt(
        world_context=ctx["world_context"],
        pkg_data=ctx.get("pkg_data"),
        user_goal=user_goal,
    )

    # Build context_snapshot
    context_snapshot = NovelEvolutionService.build_context_snapshot(
        world_id=world_id,
        context_package_id=pkg_id,
        pkg_data=ctx.get("pkg_data"),
        user_goal=user_goal,
    )

    errors = {}
    if not user_goal.strip():
        errors["user_goal"] = "推演目标不能为空"

    if errors:
        return templates.TemplateResponse(request, "novel/evolution_form.html", {
            "world": world,
            "active_nav": "novel",
            "current_world": world,
            "app_version": settings.VERSION,
            "context_packages": context_packages,
            "selected_package_id": pkg_id,
            "selected_pkg": ctx.get("context_package"),
            "ai_mode_info": _get_ai_mode_info(db),
            "errors": errors,
            "form_data": {"user_goal": user_goal},
            "result": None,
        }, status_code=422)

    # Run AI
    try:
        client = ModelRouter.get_client(db, "novel_evolution")
        config = SettingsService.get_effective_config(db)

        options = {
            "temperature": config.get("ai_temperature", 0.7),
            "max_tokens": config.get("ai_max_tokens", 3000),
            "timeout": config.get("ai_timeout", 120),
        }

        ai_result = client.generate(messages, options)

        if not ai_result.get("success"):
            error = ai_result.get("error", {})
            raise RuntimeError(error.get("message", "AI 调用失败，请检查 AI 设置配置。"))

        # Build question summary
        question_parts = ["[全书演化推演]"]
        if pkg_id:
            question_parts.append(f"上下文包ID:{pkg_id}")
        question_parts.append(user_goal[:100])
        question_summary = " | ".join(question_parts)

        # Save record
        record = NovelEvolutionService.save_novel_evolution_record(
            db=db,
            world_id=world_id,
            question=question_summary,
            ai_response=ai_result["content"],
            context_snapshot=context_snapshot,
            ai_model=ai_result.get("model", "mock"),
            is_mock=ai_result.get("provider") == "mock",
        )

        return templates.TemplateResponse(request, "novel/evolution_form.html", {
            "world": world,
            "active_nav": "novel",
            "current_world": world,
            "app_version": settings.VERSION,
            "context_packages": context_packages,
            "selected_package_id": pkg_id,
            "selected_pkg": ctx.get("context_package"),
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
        return templates.TemplateResponse(request, "novel/evolution_form.html", {
            "world": world,
            "active_nav": "novel",
            "current_world": world,
            "app_version": settings.VERSION,
            "context_packages": context_packages,
            "selected_package_id": pkg_id,
            "selected_pkg": ctx.get("context_package") if "ctx" in dir() else None,
            "ai_mode_info": _get_ai_mode_info(db),
            "errors": {"submit": f"推演失败: {e}"},
            "form_data": {"user_goal": user_goal},
            "result": None,
        })


@router.get("/evolutions", response_class=HTMLResponse)
async def list_evolutions(
    request: Request,
    world_id: int,
    db: Session = Depends(get_db),
):
    """List all novel evolution plans for this world."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    evolutions = NovelEvolutionService.list_novel_evolution_records(db, world_id)

    return templates.TemplateResponse(request, "novel/evolutions.html", {
        "world": world,
        "active_nav": "novel",
        "current_world": world,
        "app_version": settings.VERSION,
        "evolutions": evolutions,
        "get_status_label": NovelEvolutionService.get_status_label,
        "get_status_color": NovelEvolutionService.get_status_color,
    })


@router.get("/evolutions/{record_id}", response_class=HTMLResponse)
async def evolution_detail(
    request: Request,
    world_id: int,
    record_id: int,
    db: Session = Depends(get_db),
):
    """Show a single novel evolution plan detail."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    record = NovelEvolutionService.get_novel_evolution_record(db, record_id)
    if not record or record.world_id != world_id:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    return templates.TemplateResponse(request, "novel/evolution_detail.html", {
        "world": world,
        "active_nav": "novel",
        "current_world": world,
        "app_version": settings.VERSION,
        "record": record,
        "get_status_label": NovelEvolutionService.get_status_label,
        "get_status_color": NovelEvolutionService.get_status_color,
    })


@router.post("/evolutions/{record_id}/set-mainline", response_class=HTMLResponse)
async def set_mainline(
    request: Request,
    world_id: int,
    record_id: int,
    db: Session = Depends(get_db),
):
    """Set a novel evolution record as the mainline plan."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    result = NovelEvolutionService.set_record_status(db, record_id, "adopted", world_id)
    if not result:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    return RedirectResponse(
        url=f"/worlds/{world_id}/novel/evolutions", status_code=303
    )


@router.post("/evolutions/{record_id}/set-candidate", response_class=HTMLResponse)
async def set_candidate(
    request: Request,
    world_id: int,
    record_id: int,
    db: Session = Depends(get_db),
):
    """Set a novel evolution record as a candidate plan."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    result = NovelEvolutionService.set_record_status(db, record_id, "branched", world_id)
    if not result:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    return RedirectResponse(
        url=f"/worlds/{world_id}/novel/evolutions", status_code=303
    )


@router.post("/evolutions/{record_id}/discard", response_class=HTMLResponse)
async def discard_evolution(
    request: Request,
    world_id: int,
    record_id: int,
    db: Session = Depends(get_db),
):
    """Discard a novel evolution record."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    result = NovelEvolutionService.set_record_status(db, record_id, "discarded", world_id)
    if not result:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    return RedirectResponse(
        url=f"/worlds/{world_id}/novel/evolutions", status_code=303
    )
