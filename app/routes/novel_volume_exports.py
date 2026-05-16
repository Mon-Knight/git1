"""
AI World Engine - Novel Volume Export Routes
v2.6.0: Volume manuscript management and export routes.
"""

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session
import os

from app.database import get_db
from app.config import settings
from app.services.world_service import WorldService
from app.services.novel_volume_export_service import NovelVolumeExportService

router = APIRouter(prefix="/worlds/{world_id}/novel")

templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


def _get_world_or_404(db, world_id):
    return WorldService.get_world(db, world_id)


# ── Volume Manuscript Management ──

@router.get("/volume-manuscripts", response_class=HTMLResponse)
async def list_volumes(request: Request, world_id: int, db: Session = Depends(get_db)):
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    from app.models import NovelVolumeOutline
    volumes = db.query(NovelVolumeOutline).filter(
        NovelVolumeOutline.world_id == world_id, NovelVolumeOutline.is_main == True
    ).order_by(NovelVolumeOutline.id).all()

    # Build summary for each volume
    volume_summaries = []
    for v in volumes:
        ctx = NovelVolumeExportService.build_volume_manuscript_context(db, world_id, v.id)
        volume_summaries.append({"volume": v, "summary": ctx.get("summary", {}), "ok": ctx.get("ok", False)})

    return templates.TemplateResponse(request, "novel_volume_exports/index.html", {
        "world": world, "volume_summaries": volume_summaries,
        "current_world": world, "active_nav": "worlds",
        "app_version": settings.VERSION,
    })


@router.get("/volume-manuscripts/{volume_id}", response_class=HTMLResponse)
async def volume_detail(request: Request, world_id: int, volume_id: int, db: Session = Depends(get_db)):
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    ctx = NovelVolumeExportService.build_volume_manuscript_context(db, world_id, volume_id)
    if not ctx.get("ok"):
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    return templates.TemplateResponse(request, "novel_volume_exports/detail.html", {
        "world": world, "ctx": ctx, "volume_id": volume_id,
        "current_world": world, "active_nav": "worlds",
        "app_version": settings.VERSION,
    })


@router.get("/volume-manuscripts/{volume_id}/preview", response_class=HTMLResponse)
async def volume_preview(request: Request, world_id: int, volume_id: int, db: Session = Depends(get_db)):
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    ctx = NovelVolumeExportService.build_volume_manuscript_context(db, world_id, volume_id)
    if not ctx.get("ok"):
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    return templates.TemplateResponse(request, "novel_volume_exports/preview.html", {
        "world": world, "ctx": ctx, "volume_id": volume_id,
        "current_world": world, "active_nav": "worlds",
        "app_version": settings.VERSION,
    })


@router.post("/volume-manuscripts/{volume_id}/export")
async def export_volume(
    request: Request,
    world_id: int, volume_id: int,
    export_format: str = Form(default="txt"),
    include_missing_placeholders: str = Form(default="1"),
    db: Session = Depends(get_db),
):
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    opts = {"include_missing_placeholders": include_missing_placeholders == "1"}
    if export_format == "markdown":
        result = NovelVolumeExportService.export_volume_markdown(db, world_id, volume_id, opts)
    elif export_format == "json":
        result = NovelVolumeExportService.export_volume_json(db, world_id, volume_id, opts)
    else:
        result = NovelVolumeExportService.export_volume_txt(db, world_id, volume_id, opts)

    if result.get("ok"):
        return RedirectResponse(
            url=f"/worlds/{world_id}/novel/exports/{result['export_id']}",
            status_code=303,
        )

    ctx = NovelVolumeExportService.build_volume_manuscript_context(db, world_id, volume_id)
    return templates.TemplateResponse(request, "novel_volume_exports/detail.html", {
        "world": world, "ctx": ctx, "volume_id": volume_id,
        "current_world": world, "active_nav": "worlds",
        "app_version": settings.VERSION,
        "error": result.get("error", "导出失败"),
    })


# ── Export Records ──

@router.get("/exports", response_class=HTMLResponse)
async def list_exports(request: Request, world_id: int, db: Session = Depends(get_db)):
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    records = NovelVolumeExportService.list_volume_exports(db, world_id)
    return templates.TemplateResponse(request, "novel_volume_exports/exports.html", {
        "world": world, "records": records,
        "current_world": world, "active_nav": "worlds",
        "app_version": settings.VERSION,
    })


@router.get("/exports/{export_id}", response_class=HTMLResponse)
async def export_detail(request: Request, world_id: int, export_id: int, db: Session = Depends(get_db)):
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    record = NovelVolumeExportService.get_volume_export(db, world_id, export_id)
    if not record:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    return templates.TemplateResponse(request, "novel_volume_exports/export_detail.html", {
        "world": world, "record": record,
        "current_world": world, "active_nav": "worlds",
        "app_version": settings.VERSION,
    })


@router.get("/exports/{export_id}/download")
async def download_export(request: Request, world_id: int, export_id: int, db: Session = Depends(get_db)):
    world = _get_world_or_404(db, world_id)
    if not world:
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    record = NovelVolumeExportService.get_volume_export(db, world_id, export_id)
    if not record or not record.file_path or not os.path.exists(record.file_path):
        return templates.TemplateResponse(request, "worlds/404.html", {"world_id": world_id}, status_code=404)

    return FileResponse(
        record.file_path,
        media_type="application/octet-stream",
        filename=record.file_name,
    )
