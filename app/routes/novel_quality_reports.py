"""
AI World Engine - Novel Quality Report Routes
v2.1.0: Routes for generating and managing novel draft quality check reports.
Only generates reports — never modifies drafts.
"""

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.services.world_service import WorldService
from app.services.novel_draft_service import NovelDraftService
from app.services.novel_quality_service import NovelQualityService

router = APIRouter(prefix="/worlds/{world_id}/novel")

templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


def _get_world_or_404(db: Session, world_id: int, request: Request):
    """Get world or return 404."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return None, templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )
    return world, None


def _get_draft_or_404(db: Session, world_id: int, draft_id: int, request: Request):
    """Get draft or return 404."""
    from app.models import NovelDraft
    draft = db.query(NovelDraft).filter_by(id=draft_id, world_id=world_id).first()
    if not draft:
        return None, templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )
    return draft, None


# ============================================================
# World-level quality report list
# ============================================================

@router.get("/quality-reports", response_class=HTMLResponse)
async def world_quality_reports(request: Request, world_id: int, db: Session = Depends(get_db)):
    """List all quality reports for the current world."""
    world, error = _get_world_or_404(db, world_id, request)
    if error:
        return error

    reports = NovelQualityService.list_quality_reports(db, world_id)
    return templates.TemplateResponse(request, "novel_quality_reports/index.html", {
        "request": request,
        "world": world,
        "current_world": world,
        "active_nav": "novel",
        "app_version": settings.VERSION,
        "reports": reports,
    })


# ============================================================
# Draft-level quality report list
# ============================================================

@router.get("/drafts/{draft_id}/quality-reports", response_class=HTMLResponse)
async def draft_quality_reports(
    request: Request, world_id: int, draft_id: int, db: Session = Depends(get_db)
):
    """List quality reports for a specific draft."""
    world, error = _get_world_or_404(db, world_id, request)
    if error:
        return error

    draft, error = _get_draft_or_404(db, world_id, draft_id, request)
    if error:
        return error

    reports = NovelQualityService.list_quality_reports(db, world_id, draft_id=draft_id)
    return templates.TemplateResponse(request, "novel_quality_reports/draft_reports.html", {
        "request": request,
        "world": world,
        "current_world": world,
        "active_nav": "novel",
        "app_version": settings.VERSION,
        "draft": draft,
        "reports": reports,
    })


# ============================================================
# New quality report form
# ============================================================

@router.get("/drafts/{draft_id}/quality-reports/new", response_class=HTMLResponse)
async def new_quality_report(
    request: Request, world_id: int, draft_id: int, db: Session = Depends(get_db)
):
    """Show the new quality check report form."""
    world, error = _get_world_or_404(db, world_id, request)
    if error:
        return error

    draft, error = _get_draft_or_404(db, world_id, draft_id, request)
    if error:
        return error

    # Check if draft has content
    draft_empty = not draft.content or not draft.content.strip()
    missing_chapter_outline = not draft.chapter_outline_id
    missing_style = not draft.style_profile_id
    missing_context_package = not draft.context_package_id

    return templates.TemplateResponse(request, "novel_quality_reports/new.html", {
        "request": request,
        "world": world,
        "current_world": world,
        "active_nav": "novel",
        "app_version": settings.VERSION,
        "draft": draft,
        "draft_empty": draft_empty,
        "missing_chapter_outline": missing_chapter_outline,
        "missing_style": missing_style,
        "missing_context_package": missing_context_package,
        "errors": {},
        "form_data": {},
    })


# ============================================================
# Generate quality report (POST)
# ============================================================

@router.post("/drafts/{draft_id}/quality-reports", response_class=HTMLResponse)
async def create_quality_report(
    request: Request,
    world_id: int,
    draft_id: int,
    db: Session = Depends(get_db),
    check_focus: str = Form(default=""),
    extra_requirements: str = Form(default=""),
):
    """Submit a quality check request and generate a report."""
    world, error = _get_world_or_404(db, world_id, request)
    if error:
        return error

    draft, error = _get_draft_or_404(db, world_id, draft_id, request)
    if error:
        return error

    # Validation
    errors = {}
    if not draft.content or not draft.content.strip():
        return templates.TemplateResponse(request, "novel_quality_reports/new.html", {
            "request": request,
            "world": world,
            "current_world": world,
            "active_nav": "novel",
            "app_version": settings.VERSION,
            "draft": draft,
            "draft_empty": True,
            "missing_chapter_outline": not draft.chapter_outline_id,
            "missing_style": not draft.style_profile_id,
            "missing_context_package": not draft.context_package_id,
            "errors": {"submit": "正文草稿内容为空，无法生成检查报告"},
            "form_data": {"check_focus": check_focus, "extra_requirements": extra_requirements},
        }, status_code=422)

    if extra_requirements and len(extra_requirements) > 2000:
        errors["extra_requirements"] = "补充要求不能超过2000个字符"

    if errors:
        return templates.TemplateResponse(request, "novel_quality_reports/new.html", {
            "request": request,
            "world": world,
            "current_world": world,
            "active_nav": "novel",
            "app_version": settings.VERSION,
            "draft": draft,
            "draft_empty": not draft.content or not draft.content.strip(),
            "missing_chapter_outline": not draft.chapter_outline_id,
            "missing_style": not draft.style_profile_id,
            "missing_context_package": not draft.context_package_id,
            "errors": errors,
            "form_data": {"check_focus": check_focus, "extra_requirements": extra_requirements},
        }, status_code=422)

    try:
        report = NovelQualityService.generate_quality_report(
            db, world_id, draft_id,
            {"check_focus": check_focus, "extra_requirements": extra_requirements}
        )
        return RedirectResponse(
            url=f"/worlds/{world_id}/novel/quality-reports/{report.id}",
            status_code=303,
        )
    except Exception as e:
        return templates.TemplateResponse(request, "novel_quality_reports/new.html", {
            "request": request,
            "world": world,
            "current_world": world,
            "active_nav": "novel",
            "app_version": settings.VERSION,
            "draft": draft,
            "draft_empty": not draft.content or not draft.content.strip(),
            "missing_chapter_outline": not draft.chapter_outline_id,
            "missing_style": not draft.style_profile_id,
            "missing_context_package": not draft.context_package_id,
            "errors": {"submit": f"生成失败: {str(e)}"},
            "form_data": {"check_focus": check_focus, "extra_requirements": extra_requirements},
        }, status_code=500)


# ============================================================
# Quality report detail
# ============================================================

@router.get("/quality-reports/{report_id}", response_class=HTMLResponse)
async def quality_report_detail(
    request: Request, world_id: int, report_id: int, db: Session = Depends(get_db)
):
    """Show quality report detail."""
    world, error = _get_world_or_404(db, world_id, request)
    if error:
        return error

    report = NovelQualityService.get_quality_report(db, world_id, report_id)
    if not report:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    # Parse result for display
    import json
    parsed = {}
    parse_warning = None
    try:
        if report.result_json:
            parsed = json.loads(report.result_json)
    except (json.JSONDecodeError, TypeError):
        parse_warning = "报告结果 JSON 解析失败，请查看原始文本。"

    return templates.TemplateResponse(request, "novel_quality_reports/detail.html", {
        "request": request,
        "world": world,
        "current_world": world,
        "active_nav": "novel",
        "app_version": settings.VERSION,
        "report": report,
        "parsed": parsed,
        "parse_warning": parse_warning,
    })


# ============================================================
# Set current reference report
# ============================================================

@router.post("/quality-reports/{report_id}/set-current")
async def set_current_report(
    request: Request, world_id: int, report_id: int, db: Session = Depends(get_db)
):
    """Mark a report as the current reference."""
    world, error = _get_world_or_404(db, world_id, request)
    if error:
        return error

    try:
        NovelQualityService.set_current_quality_report(db, world_id, report_id)
    except ValueError as e:
        report = NovelQualityService.get_quality_report(db, world_id, report_id)
        if not report:
            return templates.TemplateResponse(
                request, "worlds/404.html", {"world_id": world_id}, status_code=404
            )
        # Show error on detail page
        import json
        parsed = {}
        try:
            if report.result_json:
                parsed = json.loads(report.result_json)
        except (json.JSONDecodeError, TypeError):
            pass
        return templates.TemplateResponse(request, "novel_quality_reports/detail.html", {
            "request": request,
            "world": world,
            "current_world": world,
            "active_nav": "novel",
            "app_version": settings.VERSION,
            "report": report,
            "parsed": parsed,
            "parse_warning": None,
            "action_error": str(e),
        }, status_code=400)

    return RedirectResponse(
        url=f"/worlds/{world_id}/novel/quality-reports/{report_id}",
        status_code=303,
    )


# ============================================================
# Discard report
# ============================================================

@router.post("/quality-reports/{report_id}/discard")
async def discard_report(
    request: Request, world_id: int, report_id: int, db: Session = Depends(get_db)
):
    """Discard a quality report."""
    world, error = _get_world_or_404(db, world_id, request)
    if error:
        return error

    try:
        NovelQualityService.discard_quality_report(db, world_id, report_id)
    except ValueError as e:
        return templates.TemplateResponse(request, "novel_quality_reports/detail.html", {
            "request": request,
            "world": world,
            "current_world": world,
            "active_nav": "novel",
            "app_version": settings.VERSION,
            "report": NovelQualityService.get_quality_report(db, world_id, report_id),
            "parsed": {},
            "parse_warning": None,
            "action_error": str(e),
        }, status_code=400)

    return RedirectResponse(
        url=f"/worlds/{world_id}/novel/quality-reports/{report_id}",
        status_code=303,
    )
