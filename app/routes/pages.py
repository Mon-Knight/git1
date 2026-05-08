"""
AI World Engine - Page Routes
Basic page rendering routes for v0.1.0.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app.config import settings

router = APIRouter()

# Template directory
templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the home page."""
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "version": settings.VERSION,
            "mock_ai": settings.is_mock_ai,
        },
    )
