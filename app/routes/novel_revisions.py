"""
AI World Engine - Novel Revision Routes
v2.2.0: Routes for generating and managing polished revision candidates.
Only generates revision candidates — never overwrites original drafts.
"""

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.services.world_service import WorldService
from app.services.novel_revision_service import NovelRevisionService
from app.services.novel_quality_service import NovelQualityService
from app.models import NovelDraft, NovelDraftQualityReport

router = APIRouter(prefix="/worlds/{world_id}/novel")

templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


def _get_world_or_404(db, world_id, request):
    world = WorldService.get_world(db, world_id)
    if not world:
        return None, templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)
    return world, None


def _get_draft_or_404(db, world_id, draft_id, request):
    draft = db.query(NovelDraft).filter_by(id=draft_id, world_id=world_id).first()
    if not draft:
        return None, templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)
    return draft, None


# ============================================================
# World-level revision list
# ============================================================

@router.get("/revisions", response_class=HTMLResponse)
async def world_revisions(request: Request, world_id: int, db: Session = Depends(get_db)):
    world, error = _get_world_or_404(db, world_id, request)
    if error: return error
    revisions = NovelRevisionService.list_revisions(db, world_id)
    return templates.TemplateResponse(request, "novel_revisions/index.html", {
        "request": request, "world": world, "current_world": world,
        "active_nav": "novel", "app_version": settings.VERSION, "revisions": revisions,
    })


# ============================================================
# Draft-level revision list
# ============================================================

@router.get("/drafts/{draft_id}/revisions", response_class=HTMLResponse)
async def draft_revisions(request: Request, world_id: int, draft_id: int, db: Session = Depends(get_db)):
    world, error = _get_world_or_404(db, world_id, request)
    if error: return error
    draft, error = _get_draft_or_404(db, world_id, draft_id, request)
    if error: return error
    revisions = NovelRevisionService.list_revisions(db, world_id, draft_id=draft_id)
    return templates.TemplateResponse(request, "novel_revisions/draft_revisions.html", {
        "request": request, "world": world, "current_world": world,
        "active_nav": "novel", "app_version": settings.VERSION,
        "draft": draft, "revisions": revisions,
    })


# ============================================================
# New revision form
# ============================================================

@router.get("/drafts/{draft_id}/revisions/new", response_class=HTMLResponse)
async def new_revision(request: Request, world_id: int, draft_id: int, db: Session = Depends(get_db)):
    world, error = _get_world_or_404(db, world_id, request)
    if error: return error
    draft, error = _get_draft_or_404(db, world_id, draft_id, request)
    if error: return error

    quality_reports = NovelQualityService.list_quality_reports(db, world_id, draft_id=draft_id)
    draft_empty = not draft.content or not draft.content.strip()
    no_reports = len(quality_reports) == 0
    missing_outline = not draft.chapter_outline_id
    missing_style = not draft.style_profile_id

    return templates.TemplateResponse(request, "novel_revisions/new.html", {
        "request": request, "world": world, "current_world": world,
        "active_nav": "novel", "app_version": settings.VERSION,
        "draft": draft, "quality_reports": quality_reports,
        "draft_empty": draft_empty, "no_reports": no_reports,
        "missing_outline": missing_outline, "missing_style": missing_style,
        "errors": {}, "form_data": {},
    })


# ============================================================
# Generate revision (POST)
# ============================================================

@router.post("/drafts/{draft_id}/revisions", response_class=HTMLResponse)
async def create_revision(
    request: Request, world_id: int, draft_id: int, db: Session = Depends(get_db),
    quality_report_id: str = Form(default=""),
    extra_requirements: str = Form(default=""),
):
    world, error = _get_world_or_404(db, world_id, request)
    if error: return error
    draft, error = _get_draft_or_404(db, world_id, draft_id, request)
    if error: return error

    quality_reports = NovelQualityService.list_quality_reports(db, world_id, draft_id=draft_id)
    report_id = int(quality_report_id) if quality_report_id and quality_report_id.strip() else None

    errors = {}
    if not draft.content or not draft.content.strip():
        return templates.TemplateResponse(request, "novel_revisions/new.html", {
            "request": request, "world": world, "current_world": world,
            "active_nav": "novel", "app_version": settings.VERSION,
            "draft": draft, "quality_reports": quality_reports,
            "draft_empty": True, "no_reports": len(quality_reports) == 0,
            "missing_outline": not draft.chapter_outline_id,
            "missing_style": not draft.style_profile_id,
            "errors": {"submit": "正文草稿内容为空，无法生成润色候选"}, "form_data": {},
        }, status_code=422)

    if extra_requirements and len(extra_requirements) > 2000:
        errors["extra_requirements"] = "补充要求不能超过2000个字符"

    if errors:
        return templates.TemplateResponse(request, "novel_revisions/new.html", {
            "request": request, "world": world, "current_world": world,
            "active_nav": "novel", "app_version": settings.VERSION,
            "draft": draft, "quality_reports": quality_reports,
            "draft_empty": False, "no_reports": len(quality_reports) == 0,
            "missing_outline": not draft.chapter_outline_id,
            "missing_style": not draft.style_profile_id,
            "errors": errors, "form_data": {"quality_report_id": quality_report_id, "extra_requirements": extra_requirements},
        }, status_code=422)

    try:
        revision = NovelRevisionService.generate_revision(
            db, world_id, draft_id, report_id or 0,
            {"extra_requirements": extra_requirements}
        )
        return RedirectResponse(url=f"/worlds/{world_id}/novel/revisions/{revision.id}", status_code=303)
    except Exception as e:
        return templates.TemplateResponse(request, "novel_revisions/new.html", {
            "request": request, "world": world, "current_world": world,
            "active_nav": "novel", "app_version": settings.VERSION,
            "draft": draft, "quality_reports": quality_reports,
            "draft_empty": False, "no_reports": len(quality_reports) == 0,
            "missing_outline": not draft.chapter_outline_id,
            "missing_style": not draft.style_profile_id,
            "errors": {"submit": f"生成失败: {str(e)}"},
            "form_data": {"quality_report_id": quality_report_id, "extra_requirements": extra_requirements},
        }, status_code=500)


# ============================================================
# Revision detail
# ============================================================

@router.get("/revisions/{revision_id}", response_class=HTMLResponse)
async def revision_detail(request: Request, world_id: int, revision_id: int, db: Session = Depends(get_db)):
    world, error = _get_world_or_404(db, world_id, request)
    if error: return error
    revision = NovelRevisionService.get_revision(db, world_id, revision_id)
    if not revision:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)
    return templates.TemplateResponse(request, "novel_revisions/detail.html", {
        "request": request, "world": world, "current_world": world,
        "active_nav": "novel", "app_version": settings.VERSION, "revision": revision,
    })


# ============================================================
# Edit revision
# ============================================================

@router.get("/revisions/{revision_id}/edit", response_class=HTMLResponse)
async def edit_revision(request: Request, world_id: int, revision_id: int, db: Session = Depends(get_db)):
    world, error = _get_world_or_404(db, world_id, request)
    if error: return error
    revision = NovelRevisionService.get_revision(db, world_id, revision_id)
    if not revision:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)
    if revision.status == "discarded":
        return templates.TemplateResponse(request, "novel_revisions/detail.html", {
            "request": request, "world": world, "current_world": world,
            "active_nav": "novel", "app_version": settings.VERSION, "revision": revision,
            "action_error": "已废弃的润色稿不能编辑",
        }, status_code=400)
    return templates.TemplateResponse(request, "novel_revisions/edit.html", {
        "request": request, "world": world, "current_world": world,
        "active_nav": "novel", "app_version": settings.VERSION, "revision": revision,
        "errors": {}, "form_data": {},
    })


@router.post("/revisions/{revision_id}/edit", response_class=HTMLResponse)
async def update_revision(
    request: Request, world_id: int, revision_id: int, db: Session = Depends(get_db),
    title: str = Form(default=""), content: str = Form(default=""),
    revision_summary: str = Form(default=""),
):
    world, error = _get_world_or_404(db, world_id, request)
    if error: return error
    revision = NovelRevisionService.get_revision(db, world_id, revision_id)
    if not revision:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    errors = {}
    if not content.strip():
        errors["content"] = "正文内容不能为空"
    if errors:
        return templates.TemplateResponse(request, "novel_revisions/edit.html", {
            "request": request, "world": world, "current_world": world,
            "active_nav": "novel", "app_version": settings.VERSION, "revision": revision,
            "errors": errors, "form_data": {"title": title, "content": content, "revision_summary": revision_summary},
        }, status_code=422)

    try:
        NovelRevisionService.update_revision(db, world_id, revision_id, {
            "title": title.strip(), "content": content, "revision_summary": revision_summary.strip(),
        })
        return RedirectResponse(url=f"/worlds/{world_id}/novel/revisions/{revision_id}", status_code=303)
    except ValueError as e:
        return templates.TemplateResponse(request, "novel_revisions/edit.html", {
            "request": request, "world": world, "current_world": world,
            "active_nav": "novel", "app_version": settings.VERSION, "revision": revision,
            "errors": {"submit": str(e)}, "form_data": {"title": title, "content": content, "revision_summary": revision_summary},
        }, status_code=400)


# ============================================================
# Set accepted
# ============================================================

@router.post("/revisions/{revision_id}/set-accepted")
async def set_accepted(request: Request, world_id: int, revision_id: int, db: Session = Depends(get_db)):
    world, error = _get_world_or_404(db, world_id, request)
    if error: return error
    try:
        NovelRevisionService.set_accepted_revision(db, world_id, revision_id)
    except ValueError as e:
        revision = NovelRevisionService.get_revision(db, world_id, revision_id)
        return templates.TemplateResponse(request, "novel_revisions/detail.html", {
            "request": request, "world": world, "current_world": world,
            "active_nav": "novel", "app_version": settings.VERSION, "revision": revision,
            "action_error": str(e),
        }, status_code=400)
    return RedirectResponse(url=f"/worlds/{world_id}/novel/revisions/{revision_id}", status_code=303)


# ============================================================
# Discard
# ============================================================

@router.post("/revisions/{revision_id}/discard")
async def discard_revision(request: Request, world_id: int, revision_id: int, db: Session = Depends(get_db)):
    world, error = _get_world_or_404(db, world_id, request)
    if error: return error
    try:
        NovelRevisionService.discard_revision(db, world_id, revision_id)
    except ValueError as e:
        revision = NovelRevisionService.get_revision(db, world_id, revision_id)
        return templates.TemplateResponse(request, "novel_revisions/detail.html", {
            "request": request, "world": world, "current_world": world,
            "active_nav": "novel", "app_version": settings.VERSION, "revision": revision,
            "action_error": str(e),
        }, status_code=400)
    return RedirectResponse(url=f"/worlds/{world_id}/novel/revisions/{revision_id}", status_code=303)
