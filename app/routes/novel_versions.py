"""
AI World Engine - Novel Version Routes
v2.3.0: Version comparison and final draft management.
No AI calls — purely management routes.
"""

from fastapi import APIRouter, Request, Form, Depends, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.services.world_service import WorldService
from app.services.novel_version_service import NovelVersionService
from app.models import NovelDraft

router = APIRouter(prefix="/worlds/{world_id}/novel")

templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


def _w(db, wid, req):
    w = WorldService.get_world(db, wid)
    if not w: return None, templates.TemplateResponse(req, "worlds/404.html", {"world_id": wid}, status_code=404)
    return w, None


def _d(db, wid, did, req):
    d = db.query(NovelDraft).filter_by(id=did, world_id=wid).first()
    if not d: return None, templates.TemplateResponse(req, "worlds/404.html", {"world_id": wid}, status_code=404)
    return d, None


# ============================================================
# Draft version management page
# ============================================================

@router.get("/drafts/{draft_id}/versions", response_class=HTMLResponse)
async def draft_versions(req: Request, world_id: int, draft_id: int, db: Session = Depends(get_db)):
    w, e = _w(db, world_id, req)
    if e: return e
    d, e = _d(db, world_id, draft_id, req)
    if e: return e
    versions = NovelVersionService.list_text_versions(db, world_id, draft_id)
    current_final = NovelVersionService.get_current_final_version(db, world_id, draft_id)
    return templates.TemplateResponse(req, "novel_versions/draft_versions.html", {
        "request": req, "world": w, "current_world": w, "active_nav": "novel",
        "app_version": settings.VERSION, "draft": d, "versions": versions,
        "current_final": current_final,
    })


# ============================================================
# Version comparison page
# ============================================================

@router.get("/drafts/{draft_id}/versions/compare", response_class=HTMLResponse)
async def compare_versions(
    req: Request, world_id: int, draft_id: int, db: Session = Depends(get_db),
    left_type: str = Query(default=""), left_id: int = Query(default=0),
    right_type: str = Query(default=""), right_id: int = Query(default=0),
):
    w, e = _w(db, world_id, req)
    if e: return e
    d, e = _d(db, world_id, draft_id, req)
    if e: return e

    diff = None
    error = None
    left_version = None
    right_version = None
    if left_type and right_type and left_id and right_id:
        left_version = NovelVersionService.get_text_version(db, world_id, draft_id, left_type, left_id)
        right_version = NovelVersionService.get_text_version(db, world_id, draft_id, right_type, right_id)
        if not left_version or not right_version:
            error = "版本不存在"
        elif left_type == right_type and left_id == right_id:
            diff = {
                "left_title": left_version.get("title", ""), "right_title": right_version.get("title", ""),
                "left_word_count": left_version.get("word_count", 0), "right_word_count": right_version.get("word_count", 0),
                "word_count_delta": 0, "same_title": True, "same_content": True,
                "similarity": 100.0, "diff_blocks": [{"type": "same", "text": "两个版本完全相同。"}],
                "left_type": left_type, "right_type": right_type,
                "left_status": left_version.get("status", ""), "right_status": right_version.get("status", ""),
            }
        else:
            result = NovelVersionService.compare_text_versions(
                db, world_id, draft_id, left_type, left_id, right_type, right_id
            )
            if "error" in result:
                error = result["error"]
            else:
                diff = result

    versions = NovelVersionService.list_text_versions(db, world_id, draft_id)
    return templates.TemplateResponse(req, "novel_versions/compare.html", {
        "request": req, "world": w, "current_world": w, "active_nav": "novel",
        "app_version": settings.VERSION, "draft": d, "versions": versions,
        "diff": diff, "error": error, "left_version": left_version, "right_version": right_version,
        "left_type": left_type, "left_id": left_id,
        "right_type": right_type, "right_id": right_id,
    })


# ============================================================
# Set final version
# ============================================================

@router.post("/drafts/{draft_id}/versions/final")
async def set_final(
    req: Request, world_id: int, draft_id: int, db: Session = Depends(get_db),
    source_type: str = Form(default=""), source_id: int = Form(default=0),
    note: str = Form(default=""),
):
    w, e = _w(db, world_id, req)
    if e: return e
    try:
        NovelVersionService.set_final_version(db, world_id, draft_id, source_type, source_id, note)
        return RedirectResponse(url=f"/worlds/{world_id}/novel/drafts/{draft_id}/versions", status_code=303)
    except ValueError as e:
        versions = NovelVersionService.list_text_versions(db, world_id, draft_id)
        d, _ = _d(db, world_id, draft_id, req)
        return templates.TemplateResponse(req, "novel_versions/draft_versions.html", {
            "request": req, "world": w, "current_world": w, "active_nav": "novel",
            "app_version": settings.VERSION, "draft": d, "versions": versions,
            "current_final": NovelVersionService.get_current_final_version(db, world_id, draft_id),
            "action_error": str(e),
        }, status_code=400)


# ============================================================
# Revoke final version
# ============================================================

@router.post("/drafts/{draft_id}/versions/final/revoke")
async def revoke_final(req: Request, world_id: int, draft_id: int, db: Session = Depends(get_db)):
    w, e = _w(db, world_id, req)
    if e: return e
    NovelVersionService.revoke_final_version(db, world_id, draft_id)
    return RedirectResponse(url=f"/worlds/{world_id}/novel/drafts/{draft_id}/versions", status_code=303)


# ============================================================
# World final drafts list
# ============================================================

@router.get("/final-drafts", response_class=HTMLResponse)
async def world_final_drafts(req: Request, world_id: int, db: Session = Depends(get_db)):
    w, e = _w(db, world_id, req)
    if e: return e
    finals = NovelVersionService.list_all_final_drafts(db, world_id)
    return templates.TemplateResponse(req, "novel_versions/final_drafts.html", {
        "request": req, "world": w, "current_world": w, "active_nav": "novel",
        "app_version": settings.VERSION, "finals": finals,
    })


# ============================================================
# Final draft detail
# ============================================================

@router.get("/final-drafts/{final_id}", response_class=HTMLResponse)
async def final_draft_detail(req: Request, world_id: int, final_id: int, db: Session = Depends(get_db)):
    w, e = _w(db, world_id, req)
    if e: return e
    final = NovelVersionService.get_final_draft_detail(db, world_id, final_id)
    if not final:
        return templates.TemplateResponse(req, "worlds/404.html", {"world_id": world_id}, status_code=404)
    return templates.TemplateResponse(req, "novel_versions/final_detail.html", {
        "request": req, "world": w, "current_world": w, "active_nav": "novel",
        "app_version": settings.VERSION, "final": final,
    })
