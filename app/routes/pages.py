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

router = APIRouter()

# Template directory
templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the home page."""
    # Get AI status summary (safe - no full API key)
    db = SessionLocal()
    try:
        ai_summary = SettingsService.get_ai_summary(db)
    except Exception:
        ai_summary = {"mode_label": "Mock AI", "is_functional": False}
    finally:
        db.close()

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "version": settings.VERSION,
            "mock_ai": settings.is_mock_ai,
            "ai_summary": ai_summary,
        },
    )
