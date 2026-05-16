"""
AI World Engine - Novel Continuity Routes
v2.5.0: Chapter continuity check routes.
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
from app.services.novel_continuity_service import NovelContinuityService

router = APIRouter(prefix="/worlds/{world_id}/novel/continuity")

templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


def _get_world_or_404(db, world_id):
    return WorldService.get_world(db, world_id)


@router.get("", response_class=HTMLResponse)
async def list_continuity(request: Request, world_id: int, db: Session = Depends(get_db)):
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    reports = NovelContinuityService.list_continuity_reports(db, world_id)
    from app.services.style_profile_service import StyleProfileService
    style_profiles = StyleProfileService.list_available_style_profiles_for_world(db, world_id)

    return templates.TemplateResponse(request, "novel_continuity/index.html", {
        "world": world, "reports": reports, "style_profiles": style_profiles,
        "current_world": world, "active_nav": "worlds",
        "app_version": settings.VERSION,
    })


@router.get("/new", response_class=HTMLResponse)
async def new_continuity_form(request: Request, world_id: int, db: Session = Depends(get_db)):
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    from app.models import NovelChapterOutline, NovelVolumeOutline
    from app.services.style_profile_service import StyleProfileService

    # Get available chapters
    chapters = db.query(NovelChapterOutline).filter(
        NovelChapterOutline.world_id == world_id, NovelChapterOutline.is_main == True
    ).order_by(NovelChapterOutline.id).all()
    volumes = db.query(NovelVolumeOutline).filter(
        NovelVolumeOutline.world_id == world_id, NovelVolumeOutline.is_main == True
    ).order_by(NovelVolumeOutline.id).all()
    style_profiles = StyleProfileService.list_available_style_profiles_for_world(db, world_id)

    max_chapter_id = max([c.id for c in chapters]) if chapters else 0

    return templates.TemplateResponse(request, "novel_continuity/new.html", {
        "world": world, "chapters": chapters, "volumes": volumes,
        "max_chapter_id": max_chapter_id, "style_profiles": style_profiles,
        "range_types": NovelContinuityService.RANGE_TYPES,
        "current_world": world, "active_nav": "worlds",
        "app_version": settings.VERSION, "errors": {},
    })


@router.post("")
async def create_continuity(
    request: Request,
    world_id: int,
    range_type: str = Form(default="recent"),
    volume_index: int = Form(default=1),
    start_chapter_index: int = Form(default=1),
    end_chapter_index: int = Form(default=5),
    recent_count: int = Form(default=3),
    style_profile_id: int = Form(default=0),
    user_requirement: str = Form(default=""),
    db: Session = Depends(get_db),
):
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    req_data = {
        "range_type": range_type,
        "volume_index": volume_index if volume_index > 0 else 1,
        "start_chapter_index": start_chapter_index if start_chapter_index > 0 else 1,
        "end_chapter_index": end_chapter_index if end_chapter_index > 0 else 5,
        "recent_count": recent_count if recent_count > 0 else 3,
        "style_profile_id": style_profile_id if style_profile_id > 0 else None,
        "user_requirement": user_requirement,
    }

    try:
        # Generate using Mock or AI
        prompt = NovelContinuityService.build_continuity_prompt(db, world_id, req_data)
        mock_result = NovelContinuityService.mock_generate()
        raw_response = json.dumps(mock_result, ensure_ascii=False, indent=2)

        record = NovelContinuityService.save_continuity_report(
            db, world_id, req_data, prompt, raw_response, raw_response
        )
        return RedirectResponse(
            url=f"/worlds/{world_id}/novel/continuity/{record.id}",
            status_code=303,
        )
    except Exception as e:
        from app.services.style_profile_service import StyleProfileService

        style_profiles = StyleProfileService.list_available_style_profiles_for_world(db, world_id)
        return templates.TemplateResponse(request, "novel_continuity/new.html", {
            "world": world, "errors": {"submit": str(e)},
            "range_types": NovelContinuityService.RANGE_TYPES,
            "style_profiles": style_profiles,
            "current_world": world, "active_nav": "worlds",
            "app_version": settings.VERSION,
        })


@router.get("/{report_id}", response_class=HTMLResponse)
async def continuity_detail(
    request: Request, world_id: int, report_id: int, db: Session = Depends(get_db)
):
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    report = NovelContinuityService.get_continuity_report(db, world_id, report_id)
    if not report:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    try:
        result_data = json.loads(report.result_json) if report.result_json else {}
    except json.JSONDecodeError:
        result_data = {"raw": report.result_json, "parse_warning": "无法解析"}

    range_labels = dict(NovelContinuityService.RANGE_TYPES)
    status_labels = {"candidate": "候选", "current": "当前参考", "discarded": "已废弃"}

    return templates.TemplateResponse(request, "novel_continuity/detail.html", {
        "world": world, "report": report, "result_data": result_data,
        "range_label": range_labels.get(report.range_type, report.range_type),
        "status_label": status_labels.get(report.status, report.status),
        "current_world": world, "active_nav": "worlds",
        "app_version": settings.VERSION,
    })


@router.post("/{report_id}/set-current")
async def set_current_report(
    request: Request, world_id: int, report_id: int, db: Session = Depends(get_db)
):
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    result = NovelContinuityService.set_current_report(db, world_id, report_id)
    if not result["ok"]:
        report = NovelContinuityService.get_continuity_report(db, world_id, report_id)
        try:
            result_data = json.loads(report.result_json) if report and report.result_json else {}
        except json.JSONDecodeError:
            result_data = {}
        return templates.TemplateResponse(request, "novel_continuity/detail.html", {
            "world": world, "report": report, "result_data": result_data,
            "current_world": world, "active_nav": "worlds",
            "app_version": settings.VERSION, "error": result["error"],
        })

    return RedirectResponse(
        url=f"/worlds/{world_id}/novel/continuity/{report_id}",
        status_code=303,
    )


@router.post("/{report_id}/discard")
async def discard_report(
    request: Request, world_id: int, report_id: int, db: Session = Depends(get_db)
):
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    result = NovelContinuityService.discard_report(db, world_id, report_id)
    if not result["ok"]:
        report = NovelContinuityService.get_continuity_report(db, world_id, report_id)
        try:
            result_data = json.loads(report.result_json) if report and report.result_json else {}
        except json.JSONDecodeError:
            result_data = {}
        return templates.TemplateResponse(request, "novel_continuity/detail.html", {
            "world": world, "report": report, "result_data": result_data,
            "current_world": world, "active_nav": "worlds",
            "app_version": settings.VERSION, "error": result["error"],
        })

    return RedirectResponse(
        url=f"/worlds/{world_id}/novel/continuity/{report_id}",
        status_code=303,
    )
