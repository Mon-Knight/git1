"""
AI World Engine - Chapter Outline Routes
Routes for generating and managing novel chapter outlines.
"""
import json
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.world_service import WorldService
from app.services.chapter_outline_service import ChapterOutlineService
from app.config import settings

router = APIRouter(prefix="/worlds/{world_id}/novel")

templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


def _get_asset_options(db: Session, world_id: int) -> dict:
    """Get available assets for the chapter outline form."""
    from app.models import StyleProfile, PlotAnchor, ContextPackage, NovelVolumeOutline

    main_vo = db.query(NovelVolumeOutline).filter_by(
        world_id=world_id, is_main=True
    ).first()

    # Also get all volume outlines for selection
    all_volume_outlines = db.query(NovelVolumeOutline).filter_by(
        world_id=world_id
    ).order_by(NovelVolumeOutline.created_at.desc()).limit(20).all()

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
        "main_volume_outline": main_vo,
        "all_volume_outlines": all_volume_outlines,
        "styles": styles,
        "anchors": anchors,
        "packages": packages,
    }


def _get_volumes_from_outline(outline) -> list:
    """Extract volumes from a volume outline result_json."""
    if not outline:
        return []
    try:
        data = json.loads(outline.result_json)
        return data.get("volumes", [])
    except (json.JSONDecodeError, ValueError):
        return []


@router.get("/chapter-outlines", response_class=HTMLResponse)
async def chapter_outlines_list(request: Request, world_id: int, db: Session = Depends(get_db)):
    """List all chapter outlines for a world."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    outlines = ChapterOutlineService.list_chapter_outlines(db, world_id)
    main_vo = ChapterOutlineService.get_main_volume_outline(db, world_id)

    return templates.TemplateResponse(request, "chapter_outlines/index.html", {
        "world": world,
        "outlines": outlines,
        "main_volume_outline": main_vo,
        "active_nav": "novel",
        "current_world": world,
        "app_version": settings.VERSION,
    })


@router.get("/chapter-outlines/new", response_class=HTMLResponse)
async def chapter_outlines_new(request: Request, world_id: int, db: Session = Depends(get_db)):
    """Show the new chapter outline generation form."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    assets = _get_asset_options(db, world_id)
    main_vo = assets.get("main_volume_outline")
    volumes = _get_volumes_from_outline(main_vo)

    # Check for missing prerequisites
    missing_prereqs = []
    if not main_vo:
        missing_prereqs.append("main_volume_outline")
    if main_vo and not volumes:
        missing_prereqs.append("no_volumes")

    return templates.TemplateResponse(request, "chapter_outlines/new.html", {
        "world": world,
        "active_nav": "novel",
        "current_world": world,
        "app_version": settings.VERSION,
        "volumes": volumes,
        "missing_prereqs": missing_prereqs,
        **assets,
    })


@router.post("/chapter-outlines", response_class=HTMLResponse)
async def chapter_outlines_create(
    request: Request, world_id: int, db: Session = Depends(get_db),
    volume_outline_id: str = Form(default=""),
    volume_index: str = Form(default=""),
    style_profile_id: str = Form(default=""),
    plot_anchor_id: str = Form(default=""),
    context_package_id: str = Form(default=""),
    chapter_count: str = Form(default="8"),
    extra_requirements: str = Form(default=""),
):
    """Generate a new chapter outline."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    # Parse IDs
    vo_id = int(volume_outline_id) if volume_outline_id else None
    v_idx = int(volume_index) if volume_index else None
    sty_id = int(style_profile_id) if style_profile_id else None
    anc_id = int(plot_anchor_id) if plot_anchor_id else None
    pkg_id = int(context_package_id) if context_package_id else None

    # Validate required fields
    if not vo_id:
        assets = _get_asset_options(db, world_id)
        return templates.TemplateResponse(request, "chapter_outlines/new.html", {
            "world": world, "active_nav": "novel", "current_world": world,
            "app_version": settings.VERSION,
            "error": "请选择主线分卷方案",
            "form_data": {
                "volume_outline_id": volume_outline_id, "volume_index": volume_index,
                "style_profile_id": style_profile_id, "plot_anchor_id": plot_anchor_id,
                "context_package_id": context_package_id, "chapter_count": chapter_count,
                "extra_requirements": extra_requirements,
            },
            "volumes": _get_volumes_from_outline(assets.get("main_volume_outline")),
            **assets,
        })

    if not v_idx:
        assets = _get_asset_options(db, world_id)
        return templates.TemplateResponse(request, "chapter_outlines/new.html", {
            "world": world, "active_nav": "novel", "current_world": world,
            "app_version": settings.VERSION,
            "error": "请选择要生成章节大纲的分卷",
            "form_data": {
                "volume_outline_id": volume_outline_id, "volume_index": volume_index,
                "style_profile_id": style_profile_id, "plot_anchor_id": plot_anchor_id,
                "context_package_id": context_package_id, "chapter_count": chapter_count,
                "extra_requirements": extra_requirements,
            },
            "volumes": _get_volumes_from_outline(assets.get("main_volume_outline")),
            **assets,
        })

    try:
        cc = int(chapter_count) if chapter_count else 8
        cc = max(4, min(cc, 60))
    except ValueError:
        cc = 8

    try:
        result = ChapterOutlineService.generate_chapter_outline(
            db, world_id, vo_id, v_idx,
            sty_id, anc_id, pkg_id, cc, extra_requirements
        )
        outline = ChapterOutlineService.save_chapter_outline(
            db, world_id,
            volume_outline_id=vo_id,
            volume_index=v_idx,
            prompt=result["prompt"],
            result_json=result["result_json"],
            raw_text=result.get("raw_text", ""),
            chapter_count=result["chapter_count"],
            style_profile_id=sty_id,
            plot_anchor_id=anc_id,
            context_package_id=pkg_id,
            generation_requirement=extra_requirements,
        )
        return RedirectResponse(
            url=f"/worlds/{world_id}/novel/chapter-outlines/{outline.id}",
            status_code=303
        )
    except Exception as e:
        assets = _get_asset_options(db, world_id)
        return templates.TemplateResponse(request, "chapter_outlines/new.html", {
            "world": world, "active_nav": "novel", "current_world": world,
            "app_version": settings.VERSION,
            "error": str(e),
            "form_data": {
                "volume_outline_id": volume_outline_id, "volume_index": volume_index,
                "style_profile_id": style_profile_id, "plot_anchor_id": plot_anchor_id,
                "context_package_id": context_package_id, "chapter_count": chapter_count,
                "extra_requirements": extra_requirements,
            },
            "volumes": _get_volumes_from_outline(assets.get("main_volume_outline")),
            **assets,
        })


@router.get("/chapter-outlines/{outline_id}", response_class=HTMLResponse)
async def chapter_outlines_detail(request: Request, world_id: int, outline_id: int, db: Session = Depends(get_db)):
    """Show chapter outline detail."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    outline = ChapterOutlineService.get_chapter_outline(db, world_id, outline_id)
    if not outline:
        return templates.TemplateResponse(request, "chapter_outlines/404.html", {
            "world": world, "outline_id": outline_id, "world_id": world_id
        }, status_code=404)

    chapters = []
    parse_error = False
    try:
        data = json.loads(outline.result_json)
        chapters = data.get("chapters", [])
        if data.get("parse_error"):
            parse_error = True
    except (json.JSONDecodeError, ValueError):
        parse_error = True

    # Check if source volume outline still exists
    source_vo_exists = True
    try:
        from app.models import NovelVolumeOutline
        vo = db.query(NovelVolumeOutline).filter_by(id=outline.volume_outline_id, world_id=world_id).first()
        source_vo_exists = vo is not None
    except Exception:
        source_vo_exists = False

    return templates.TemplateResponse(request, "chapter_outlines/detail.html", {
        "world": world,
        "outline": outline,
        "chapters": chapters,
        "parse_error": parse_error,
        "source_vo_exists": source_vo_exists,
        "active_nav": "novel",
        "current_world": world,
        "app_version": settings.VERSION,
    })


@router.get("/chapter-outlines/{outline_id}/edit", response_class=HTMLResponse)
async def chapter_outlines_edit(request: Request, world_id: int, outline_id: int, db: Session = Depends(get_db)):
    """Show chapter outline edit form."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    outline = ChapterOutlineService.get_chapter_outline(db, world_id, outline_id)
    if not outline:
        return templates.TemplateResponse(request, "chapter_outlines/404.html", {
            "world": world, "outline_id": outline_id, "world_id": world_id
        }, status_code=404)

    if outline.status == "discarded":
        return templates.TemplateResponse(request, "chapter_outlines/detail.html", {
            "world": world, "outline": outline, "chapters": [],
            "active_nav": "novel", "current_world": world,
            "app_version": settings.VERSION, "error": "已废弃的章节大纲不能编辑",
        })

    chapters = []
    try:
        data = json.loads(outline.result_json)
        chapters = data.get("chapters", [])
    except (json.JSONDecodeError, ValueError):
        pass

    return templates.TemplateResponse(request, "chapter_outlines/edit.html", {
        "world": world,
        "outline": outline,
        "chapters": chapters,
        "active_nav": "novel",
        "current_world": world,
        "app_version": settings.VERSION,
    })


@router.post("/chapter-outlines/{outline_id}/edit", response_class=HTMLResponse)
async def chapter_outlines_update(
    request: Request, world_id: int, outline_id: int, db: Session = Depends(get_db),
    title: str = Form(default=""),
    summary: str = Form(default=""),
    chapter_titles: list = Form(default=[]),
    chapter_goals: list = Form(default=[]),
    chapter_conflicts: list = Form(default=[]),
    chapter_events: list = Form(default=[]),
    chapter_hooks: list = Form(default=[]),
    chapter_words: list = Form(default=[]),
):
    """Save edited chapter outline."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    try:
        ChapterOutlineService.update_chapter_outline(db, world_id, outline_id, {
            "title": title,
            "summary": summary,
            "chapter_titles": chapter_titles,
            "chapter_goals": chapter_goals,
            "chapter_conflicts": chapter_conflicts,
            "chapter_events": chapter_events,
            "chapter_hooks": chapter_hooks,
            "chapter_words": chapter_words,
        })
        return RedirectResponse(
            url=f"/worlds/{world_id}/novel/chapter-outlines/{outline_id}",
            status_code=303
        )
    except Exception as e:
        # Reload outline data and show error
        outline = ChapterOutlineService.get_chapter_outline(db, world_id, outline_id)
        chapters = []
        if outline:
            try:
                data = json.loads(outline.result_json)
                chapters = data.get("chapters", [])
            except (json.JSONDecodeError, ValueError):
                pass
        return templates.TemplateResponse(request, "chapter_outlines/edit.html", {
            "world": world, "outline": outline, "chapters": chapters,
            "active_nav": "novel", "current_world": world,
            "app_version": settings.VERSION, "error": str(e),
        })


@router.post("/chapter-outlines/{outline_id}/set-main", response_class=HTMLResponse)
async def chapter_outlines_set_main(request: Request, world_id: int, outline_id: int, db: Session = Depends(get_db)):
    """Set a chapter outline as the main plan."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    try:
        ChapterOutlineService.set_main_chapter_outline(db, world_id, outline_id)
    except Exception as e:
        outline = ChapterOutlineService.get_chapter_outline(db, world_id, outline_id)
        chapters = []
        if outline:
            try:
                data = json.loads(outline.result_json)
                chapters = data.get("chapters", [])
            except (json.JSONDecodeError, ValueError):
                pass
        return templates.TemplateResponse(request, "chapter_outlines/detail.html", {
            "world": world, "outline": outline, "chapters": chapters,
            "active_nav": "novel", "current_world": world,
            "app_version": settings.VERSION, "error": str(e),
        })

    return RedirectResponse(
        url=f"/worlds/{world_id}/novel/chapter-outlines/{outline_id}",
        status_code=303
    )


@router.post("/chapter-outlines/{outline_id}/discard", response_class=HTMLResponse)
async def chapter_outlines_discard(request: Request, world_id: int, outline_id: int, db: Session = Depends(get_db)):
    """Discard a chapter outline."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    try:
        ChapterOutlineService.discard_chapter_outline(db, world_id, outline_id)
    except Exception as e:
        outline = ChapterOutlineService.get_chapter_outline(db, world_id, outline_id)
        chapters = []
        if outline:
            try:
                data = json.loads(outline.result_json)
                chapters = data.get("chapters", [])
            except (json.JSONDecodeError, ValueError):
                pass
        return templates.TemplateResponse(request, "chapter_outlines/detail.html", {
            "world": world, "outline": outline, "chapters": chapters,
            "active_nav": "novel", "current_world": world,
            "app_version": settings.VERSION, "error": str(e),
        })

    return RedirectResponse(
        url=f"/worlds/{world_id}/novel/chapter-outlines",
        status_code=303
    )
