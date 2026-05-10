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
