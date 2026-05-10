"""
AI World Engine - Page Routes
Basic page rendering routes for v0.1.0.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app.config import settings
from app.database import SessionLocal
from app.services.settings_service import SettingsService
from app.services.dashboard_service import DashboardService

router = APIRouter()

# Template directory
templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the workspace dashboard home page."""
    db = SessionLocal()
    try:
        ai_summary = SettingsService.get_ai_summary(db)
        dashboard_summary = DashboardService.get_dashboard_summary(db)
        recent_worlds = DashboardService.get_recent_worlds(db, limit=5)
        pending_items = DashboardService.get_pending_items(db, limit=8)
        recent_packages = DashboardService.get_recent_context_packages(db, limit=5)
        recent_evolutions = DashboardService.get_recent_novel_evolutions(db, limit=5)
        first_world_id = recent_worlds[0]["id"] if recent_worlds else None
        quick_actions = DashboardService.get_quick_actions(first_world_id)
    except Exception:
        ai_summary = {"mode_label": "Mock AI", "is_functional": False}
        dashboard_summary = {}
        recent_worlds = []
        pending_items = []
        recent_packages = []
        recent_evolutions = []
        quick_actions = DashboardService.get_quick_actions(None)
    finally:
        db.close()

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "version": settings.VERSION,
            "app_version": settings.VERSION,
            "mock_ai": settings.is_mock_ai,
            "ai_summary": ai_summary,
            "active_nav": "dashboard",
            "dashboard_summary": dashboard_summary,
            "recent_worlds": recent_worlds,
            "pending_items": pending_items,
            "recent_packages": recent_packages,
            "recent_evolutions": recent_evolutions,
            "quick_actions": quick_actions,
        },
    )
