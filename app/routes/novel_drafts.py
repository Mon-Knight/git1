"""
AI World Engine - Novel Draft Routes
Routes for generating and managing chapter draft content.
"""
import json
import re
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.services.world_service import WorldService
from app.services.novel_draft_service import NovelDraftService
from app.config import settings

router = APIRouter(prefix="/worlds/{world_id}/novel")

templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


def _get_asset_options(db: Session, world_id: int) -> dict:
    """Get available assets for the draft form."""
    from app.models import StyleProfile, PlotAnchor, ContextPackage

    styles = db.query(StyleProfile).filter(
        (StyleProfile.world_id == world_id) | (StyleProfile.world_id == None)
    ).order_by(StyleProfile.created_at.desc()).limit(20).all()

    anchors = db.query(PlotAnchor).filter_by(
        world_id=world_id
    ).order_by(PlotAnchor.created_at.desc()).limit(20).all()

    packages = db.query(ContextPackage).filter_by(
        world_id=world_id
    ).order_by(ContextPackage.created_at.desc()).limit(20).all()

    return {
        "styles": styles,
        "anchors": anchors,
        "packages": packages,
    }


def _get_main_chapter_outlines(db: Session, world_id: int):
    from app.models import NovelChapterOutline
    return db.query(NovelChapterOutline).filter_by(
        world_id=world_id, is_main=True
    ).order_by(NovelChapterOutline.created_at.desc()).all()


def _extract_chapters(result_json: str):
    try:
        data = json.loads(result_json or "")
        return data.get("chapters", []) if isinstance(data, dict) else []
    except (json.JSONDecodeError, ValueError, TypeError):
        return []


def _build_chapter_options(outlines):
    options = []
    for outline in outlines:
        chapters = _extract_chapters(outline.result_json)
        for ch in chapters:
            options.append({
                "outline_id": outline.id,
                "volume_index": outline.volume_index,
                "volume_title": outline.volume_title or "",
                "chapter_index": ch.get("chapter_index"),
                "chapter_title": ch.get("title") or ch.get("chapter_title") or "",
            })
    return options


def _get_asset_counts(db: Session, world_id: int) -> dict:
    from app.models import Character, Faction, Location, WorldRule
    return {
        "character_count": db.query(func.count(Character.id)).filter(Character.world_id == world_id).scalar() or 0,
        "faction_count": db.query(func.count(Faction.id)).filter(Faction.world_id == world_id).scalar() or 0,
        "location_count": db.query(func.count(Location.id)).filter(Location.world_id == world_id).scalar() or 0,
        "rule_count": db.query(func.count(WorldRule.id)).filter(WorldRule.world_id == world_id).scalar() or 0,
    }


@router.get("/drafts", response_class=HTMLResponse)
async def novel_drafts_list(request: Request, world_id: int, db: Session = Depends(get_db)):
    """List all novel drafts for a world."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    drafts = NovelDraftService.list_novel_drafts(db, world_id)
    return templates.TemplateResponse(request, "novel_drafts/index.html", {
        "world": world,
        "drafts": drafts,
        "active_nav": "novel",
        "current_world": world,
        "app_version": settings.VERSION,
    })


@router.get("/drafts/new", response_class=HTMLResponse)
async def novel_drafts_new(request: Request, world_id: int, db: Session = Depends(get_db)):
    """Show the draft generation form."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    outlines = _get_main_chapter_outlines(db, world_id)
    chapter_options = _build_chapter_options(outlines)
    missing_prereqs = []
    if not outlines:
        missing_prereqs.append("main_chapter_outline")
    elif not chapter_options:
        missing_prereqs.append("no_chapters")

    return templates.TemplateResponse(request, "novel_drafts/new.html", {
        "world": world,
        "active_nav": "novel",
        "current_world": world,
        "app_version": settings.VERSION,
        "chapter_outlines": outlines,
        "chapter_options": chapter_options,
        "missing_prereqs": missing_prereqs,
        "asset_counts": _get_asset_counts(db, world_id),
        **_get_asset_options(db, world_id),
    })


@router.post("/drafts", response_class=HTMLResponse)
async def novel_drafts_create(
    request: Request,
    world_id: int,
    db: Session = Depends(get_db),
    chapter_key: str = Form(default=""),
    style_profile_id: str = Form(default=""),
    plot_anchor_id: str = Form(default=""),
    context_package_id: str = Form(default=""),
    target_words: str = Form(default=""),
    narrative_pov: str = Form(default=""),
    pacing_requirement: str = Form(default=""),
    extra_requirements: str = Form(default=""),
    strict_outline: str = Form(default=""),
    emphasize_psychology: str = Form(default=""),
    emphasize_scene: str = Form(default=""),
    emphasize_dialogue: str = Form(default=""),
):
    """Generate a novel draft."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    outlines = _get_main_chapter_outlines(db, world_id)
    chapter_options = _build_chapter_options(outlines)
    missing_prereqs = []
    if not outlines:
        missing_prereqs.append("main_chapter_outline")
    elif not chapter_options:
        missing_prereqs.append("no_chapters")

    error = ""
    chapter_outline_id = ""
    chapter_index = ""

    if chapter_key:
        try:
            chapter_outline_id, chapter_index = chapter_key.split(":")
        except ValueError:
            error = "请选择要生成正文的章节"
    else:
        error = "请选择要生成正文的章节"

    if target_words:
        if not re.match(r"^\d+(字)?$", target_words.strip()):
            error = error or "目标字数格式不正确"

    request_data = {
        "chapter_outline_id": chapter_outline_id,
        "chapter_index": chapter_index,
        "style_profile_id": style_profile_id,
        "plot_anchor_id": plot_anchor_id,
        "context_package_id": context_package_id,
        "target_words": target_words,
        "narrative_pov": narrative_pov,
        "pacing_requirement": pacing_requirement,
        "extra_requirements": extra_requirements,
        "strict_outline": strict_outline,
        "emphasize_psychology": emphasize_psychology,
        "emphasize_scene": emphasize_scene,
        "emphasize_dialogue": emphasize_dialogue,
    }

    if error or missing_prereqs:
        return templates.TemplateResponse(request, "novel_drafts/new.html", {
            "world": world,
            "active_nav": "novel",
            "current_world": world,
            "app_version": settings.VERSION,
            "error": error or "请先补齐主线章节方案",
            "form_data": request_data,
            "chapter_outlines": outlines,
            "chapter_options": chapter_options,
            "missing_prereqs": missing_prereqs,
            "asset_counts": _get_asset_counts(db, world_id),
            **_get_asset_options(db, world_id),
        })

    try:
        result = NovelDraftService.generate_novel_draft(db, world_id, request_data)
        draft = NovelDraftService.save_novel_draft(
            db,
            world_id,
            request_data,
            prompt=result["prompt"],
            content=result["content"],
            raw_text=result.get("raw_text", ""),
        )
        return RedirectResponse(
            url=f"/worlds/{world_id}/novel/drafts/{draft.id}",
            status_code=303
        )
    except Exception as e:
        return templates.TemplateResponse(request, "novel_drafts/new.html", {
            "world": world,
            "active_nav": "novel",
            "current_world": world,
            "app_version": settings.VERSION,
            "error": str(e),
            "form_data": request_data,
            "chapter_outlines": outlines,
            "chapter_options": chapter_options,
            "missing_prereqs": missing_prereqs,
            "asset_counts": _get_asset_counts(db, world_id),
            **_get_asset_options(db, world_id),
        })


@router.get("/drafts/{draft_id}", response_class=HTMLResponse)
async def novel_drafts_detail(request: Request, world_id: int, draft_id: int, db: Session = Depends(get_db)):
    """Show novel draft detail."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    draft = NovelDraftService.get_novel_draft(db, world_id, draft_id)
    if not draft:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    from app.models import NovelChapterOutline, NovelDraft
    outline = db.query(NovelChapterOutline).filter_by(
        id=draft.chapter_outline_id, world_id=world_id
    ).first()

    existing_accepted = None
    if not draft.is_accepted:
        existing_accepted = db.query(NovelDraft).filter_by(
            world_id=world_id,
            chapter_outline_id=draft.chapter_outline_id,
            chapter_index=draft.chapter_index,
            is_accepted=True,
        ).first()

    status_labels = {"candidate": "候选", "accepted": "采用稿", "discarded": "已废弃"}

    return templates.TemplateResponse(request, "novel_drafts/detail.html", {
        "world": world,
        "draft": draft,
        "outline": outline,
        "existing_accepted": existing_accepted,
        "status_labels": status_labels,
        "active_nav": "novel",
        "current_world": world,
        "app_version": settings.VERSION,
    })


@router.get("/drafts/{draft_id}/edit", response_class=HTMLResponse)
async def novel_drafts_edit(request: Request, world_id: int, draft_id: int, db: Session = Depends(get_db)):
    """Show edit form for a draft."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    draft = NovelDraftService.get_novel_draft(db, world_id, draft_id)
    if not draft:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)
    if draft.status == "discarded":
        return templates.TemplateResponse(request, "novel_drafts/detail.html", {
            "world": world,
            "draft": draft,
            "outline": None,
            "existing_accepted": None,
            "status_labels": {"candidate": "候选", "accepted": "采用稿", "discarded": "已废弃"},
            "active_nav": "novel",
            "current_world": world,
            "app_version": settings.VERSION,
            "error": "已废弃的正文草稿不能编辑",
        })

    return templates.TemplateResponse(request, "novel_drafts/edit.html", {
        "world": world,
        "draft": draft,
        "active_nav": "novel",
        "current_world": world,
        "app_version": settings.VERSION,
    })


@router.post("/drafts/{draft_id}/edit", response_class=HTMLResponse)
async def novel_drafts_update(
    request: Request,
    world_id: int,
    draft_id: int,
    db: Session = Depends(get_db),
    title: str = Form(default=""),
    content: str = Form(default=""),
    notes: str = Form(default=""),
):
    """Save edited draft content."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    draft = NovelDraftService.get_novel_draft(db, world_id, draft_id)
    if not draft:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    if draft.status == "discarded":
        return templates.TemplateResponse(request, "novel_drafts/detail.html", {
            "world": world,
            "draft": draft,
            "outline": None,
            "existing_accepted": None,
            "status_labels": {"candidate": "候选", "accepted": "采用稿", "discarded": "已废弃"},
            "active_nav": "novel",
            "current_world": world,
            "app_version": settings.VERSION,
            "error": "已废弃的正文草稿不能编辑",
        })

    if not content.strip():
        return templates.TemplateResponse(request, "novel_drafts/edit.html", {
            "world": world,
            "draft": draft,
            "active_nav": "novel",
            "current_world": world,
            "app_version": settings.VERSION,
            "error": "正文内容不能为空",
            "form_data": {"title": title, "content": content, "notes": notes},
        })

    try:
        NovelDraftService.update_novel_draft(db, world_id, draft_id, {
            "title": title,
            "content": content,
            "notes": notes,
        })
        return RedirectResponse(
            url=f"/worlds/{world_id}/novel/drafts/{draft_id}",
            status_code=303
        )
    except Exception as e:
        return templates.TemplateResponse(request, "novel_drafts/edit.html", {
            "world": world,
            "draft": draft,
            "active_nav": "novel",
            "current_world": world,
            "app_version": settings.VERSION,
            "error": str(e),
            "form_data": {"title": title, "content": content, "notes": notes},
        })


@router.post("/drafts/{draft_id}/set-accepted", response_class=HTMLResponse)
async def novel_drafts_set_accepted(request: Request, world_id: int, draft_id: int, db: Session = Depends(get_db)):
    """Set a draft as accepted."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    try:
        NovelDraftService.set_accepted_novel_draft(db, world_id, draft_id)
        return RedirectResponse(
            url=f"/worlds/{world_id}/novel/drafts/{draft_id}",
            status_code=303
        )
    except Exception as e:
        draft = NovelDraftService.get_novel_draft(db, world_id, draft_id)
        if not draft:
            return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)
        return templates.TemplateResponse(request, "novel_drafts/detail.html", {
            "world": world,
            "draft": draft,
            "outline": None,
            "existing_accepted": None,
            "status_labels": {"candidate": "候选", "accepted": "采用稿", "discarded": "已废弃"},
            "active_nav": "novel",
            "current_world": world,
            "app_version": settings.VERSION,
            "error": str(e),
        })


@router.post("/drafts/{draft_id}/discard", response_class=HTMLResponse)
async def novel_drafts_discard(request: Request, world_id: int, draft_id: int, db: Session = Depends(get_db)):
    """Discard a draft."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    try:
        NovelDraftService.discard_novel_draft(db, world_id, draft_id)
        return RedirectResponse(
            url=f"/worlds/{world_id}/novel/drafts/{draft_id}",
            status_code=303
        )
    except Exception as e:
        draft = NovelDraftService.get_novel_draft(db, world_id, draft_id)
        if not draft:
            return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)
        return templates.TemplateResponse(request, "novel_drafts/detail.html", {
            "world": world,
            "draft": draft,
            "outline": None,
            "existing_accepted": None,
            "status_labels": {"candidate": "候选", "accepted": "采用稿", "discarded": "已废弃"},
            "active_nav": "novel",
            "current_world": world,
            "app_version": settings.VERSION,
            "error": str(e),
        })
