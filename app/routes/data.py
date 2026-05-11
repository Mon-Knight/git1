"""
AI World Engine - Data Management Routes
Export, import, backup, restore.
"""

import os
import json
from fastapi import APIRouter, Request, UploadFile, File, Form, Depends
from fastapi.responses import HTMLResponse, StreamingResponse, Response, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session
from io import BytesIO

from app.database import get_db
from app.services.world_service import WorldService
from app.services.export_service import export_world_to_dict, export_world_json, make_export_filename
from app.services.import_service import import_world_from_payload
from app.services.backup_service import (
    create_backup, list_backups, restore_backup as do_restore_backup,
)

router = APIRouter()

templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


@router.get("/data", response_class=HTMLResponse)
async def data_index(request: Request, db: Session = Depends(get_db)):
    """Data management main page."""
    backups = list_backups()
    worlds = WorldService.list_worlds(db)
    return templates.TemplateResponse(request, "data/index.html", {
        "worlds": worlds,
        "backups": backups,
        "active_nav": "data",
    })


@router.get("/data/import", response_class=HTMLResponse)
async def import_page(request: Request):
    """Import world page."""
    return templates.TemplateResponse(request, "data/import.html", {
        "errors": {},
        "result": None,
    })


@router.post("/data/import", response_class=HTMLResponse)
async def do_import(
    request: Request,
    import_file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Handle JSON world import."""
    errors = {}
    
    # Read and validate file size
    content = await import_file.read()
    if len(content) > 20 * 1024 * 1024:
        errors["file"] = "文件过大（最大 20MB），请选择较小的文件。"
        return templates.TemplateResponse(request, "data/import.html", {
            "errors": errors, "result": None,
        }, status_code=422)

    # Parse JSON
    try:
        payload = json.loads(content.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        errors["file"] = f"JSON 解析失败：{e}"
        return templates.TemplateResponse(request, "data/import.html", {
            "errors": errors, "result": None,
        }, status_code=422)

    # Validate and import
    try:
        result = import_world_from_payload(db, payload)
    except ValueError as e:
        db.rollback()
        return templates.TemplateResponse(request, "data/import.html", {
            "errors": {"file": str(e)},
            "result": None,
        }, status_code=422)
    except Exception as e:
        db.rollback()
        return templates.TemplateResponse(request, "data/import.html", {
            "errors": {"file": f"导入失败：{e}"},
            "result": None,
        })

    return templates.TemplateResponse(request, "data/import.html", {
        "errors": {},
        "result": result,
    })


@router.get("/data/backups", response_class=HTMLResponse)
async def backups_page(request: Request, db: Session = Depends(get_db)):
    """Database backup and restore page."""
    backups = list_backups()
    return templates.TemplateResponse(request, "data/backups.html", {
        "backups": backups,
        "message": None,
        "error": None,
        "restore_result": None,
    })


@router.post("/data/backups/create", response_class=HTMLResponse)
async def create_backup_route(request: Request, db: Session = Depends(get_db)):
    """Create a new database backup."""
    try:
        meta = create_backup(db=db)
        backups = list_backups()
        return templates.TemplateResponse(request, "data/backups.html", {
            "backups": backups,
            "message": f"备份成功：{meta['backup_filename']}",
            "error": None,
            "restore_result": None,
        })
    except Exception as e:
        backups = list_backups()
        return templates.TemplateResponse(request, "data/backups.html", {
            "backups": backups,
            "message": None,
            "error": f"备份失败：{e}",
            "restore_result": None,
        })


@router.post("/data/backups/restore", response_class=HTMLResponse)
async def restore_backup_route(
    request: Request,
    backup_filename: str = Form(default=""),
    confirm: str = Form(default=""),
    db: Session = Depends(get_db),
):
    """Restore database from a backup file."""
    if not backup_filename:
        backups = list_backups()
        return templates.TemplateResponse(request, "data/backups.html", {
            "backups": backups,
            "error": "请选择要恢复的备份文件。",
            "restore_result": None,
        })

    if confirm != "YES_RESTORE":
        backups = list_backups()
        return templates.TemplateResponse(request, "data/backups.html", {
            "backups": backups,
            "error": '请在确认框中输入 "YES_RESTORE" 来确认恢复操作。',
            "restore_result": None,
        })

    try:
        result = do_restore_backup(backup_filename)
        backups = list_backups()
        return templates.TemplateResponse(request, "data/backups.html", {
            "backups": backups,
            "message": None,
            "error": None,
            "restore_result": {
                "success": True,
                "message": "数据库已恢复。请重启 AI World Engine 以确保所有页面使用新数据。",
                "pre_restore_backup": result["pre_restore_backup"],
            },
        })
    except ValueError as e:
        backups = list_backups()
        return templates.TemplateResponse(request, "data/backups.html", {
            "backups": backups,
            "error": str(e),
            "restore_result": None,
        })


@router.get("/worlds/{world_id}/export", response_class=HTMLResponse)
async def export_world_page(request: Request, world_id: int, db: Session = Depends(get_db)):
    """Show export confirmation / info before downloading."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )
    payload = export_world_to_dict(db, world_id)
    return templates.TemplateResponse(request, "data/export_result.html", {
        "world": world,
        "metadata": payload["metadata"],
        "filename": make_export_filename(world.name),
    })


@router.get("/worlds/{world_id}/export.json")
async def export_world_json_endpoint(world_id: int, db: Session = Depends(get_db)):
    """Download a world as a JSON file."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return Response(
            content=json.dumps({"error": "World not found"}),
            media_type="application/json",
            status_code=404,
        )
    json_str = export_world_json(db, world_id)
    filename = make_export_filename(world.name)
    return Response(
        content=json_str,
        media_type="application/json; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ── v1.7.8 Export Center ──────────────────────────────────────────────

from app.services.export_file_service import ExportFileService
from app.config import settings


def _is_desktop_mode() -> bool:
    """Check if running in desktop/EXE mode."""
    return os.environ.get("AIWE_DESKTOP_MODE", "0") == "1"


@router.get("/data/export", response_class=HTMLResponse)
async def export_center(
    request: Request,
    world_id: int = None,
    db: Session = Depends(get_db),
):
    """Export center page."""
    worlds = WorldService.list_worlds(db)
    pre_selected = None
    if world_id:
        pre_selected = WorldService.get_world(db, world_id)
    return templates.TemplateResponse(request, "data/export.html", {
        "worlds": worlds,
        "pre_selected_world": pre_selected,
        "active_nav": "data",
        "app_version": settings.VERSION,
    })


@router.get("/data/export/backup")
async def export_backup_download(db: Session = Depends(get_db)):
    """Download a full backup JSON (web mode)."""
    from app.services.backup_service import create_backup
    try:
        backup_path = create_backup()
        with open(backup_path, "r", encoding="utf-8") as f:
            content = f.read()
        filename = ExportFileService.build_export_filename("backup")
        return Response(
            content=content,
            media_type="application/json; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as e:
        return Response(
            content=json.dumps({"error": str(e)}),
            media_type="application/json",
            status_code=500,
        )


@router.post("/data/export/backup")
async def export_backup_desktop_save(
    request: Request,
    save_path: str = Form(default=""),
    db: Session = Depends(get_db),
):
    """Desktop mode: save backup to user-chosen path."""
    if not _is_desktop_mode():
        return Response(
            content=json.dumps({"error": "桌面模式不可用，请使用浏览器下载"}),
            media_type="application/json",
            status_code=403,
        )

    validation = ExportFileService.validate_desktop_export_path(save_path)
    if not validation["ok"]:
        return Response(
            content=json.dumps({"error": validation["error"]}),
            media_type="application/json",
            status_code=400,
        )

    try:
        from app.services.backup_service import create_backup
        backup_path = create_backup()
        with open(backup_path, "r", encoding="utf-8") as f:
            content = f.read()
        result = ExportFileService.write_export_file(save_path, json.loads(content))
        if result["ok"]:
            return {"ok": True, "path": save_path, "export_type": "backup"}
        else:
            return Response(
                content=json.dumps({"error": result["error"]}),
                media_type="application/json",
                status_code=500,
            )
    except Exception as e:
        return Response(
            content=json.dumps({"error": str(e)}),
            media_type="application/json",
            status_code=500,
        )


@router.post("/worlds/{world_id}/export.json")
async def export_world_desktop_save(
    world_id: int,
    request: Request,
    save_path: str = Form(default=""),
    db: Session = Depends(get_db),
):
    """Desktop mode: save world export to user-chosen path."""
    if not _is_desktop_mode():
        return Response(
            content=json.dumps({"error": "桌面模式不可用，请使用浏览器下载"}),
            media_type="application/json",
            status_code=403,
        )

    world = WorldService.get_world(db, world_id)
    if not world:
        return Response(
            content=json.dumps({"error": "World not found"}),
            media_type="application/json",
            status_code=404,
        )

    validation = ExportFileService.validate_desktop_export_path(save_path)
    if not validation["ok"]:
        return Response(
            content=json.dumps({"error": validation["error"]}),
            media_type="application/json",
            status_code=400,
        )

    try:
        payload = ExportFileService.build_world_export_payload(db, world_id)
        payload = ExportFileService.sanitize_payload_for_export(payload)
        result = ExportFileService.write_export_file(save_path, payload)
        if result["ok"]:
            return {"ok": True, "path": save_path, "export_type": "world"}
        else:
            return Response(
                content=json.dumps({"error": result["error"]}),
                media_type="application/json",
                status_code=500,
            )
    except Exception as e:
        return Response(
            content=json.dumps({"error": str(e)}),
            media_type="application/json",
            status_code=500,
        )


@router.get("/worlds/{world_id}/context/export")
async def export_context_assets(world_id: int, db: Session = Depends(get_db)):
    """Download context assets JSON (web mode)."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return Response(
            content=json.dumps({"error": "World not found"}),
            media_type="application/json",
            status_code=404,
        )
    try:
        payload = ExportFileService.build_context_assets_payload(db, world_id)
        payload = ExportFileService.sanitize_payload_for_export(payload)
        content = json.dumps(payload, ensure_ascii=False, indent=2, default=str)
        filename = ExportFileService.build_export_filename("assets", world.name)
        return Response(
            content=content,
            media_type="application/json; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as e:
        return Response(
            content=json.dumps({"error": str(e)}),
            media_type="application/json",
            status_code=500,
        )
