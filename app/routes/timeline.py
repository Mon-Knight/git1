"""
AI World Engine - Timeline Routes
Timeline viewing routes.
"""

from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.timeline_service import TimelineService
from app.services.world_service import WorldService

router = APIRouter(prefix="/worlds/{world_id}/timeline")

templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


@router.get("", response_class=HTMLResponse)
async def view_timeline(
    request: Request,
    world_id: int,
    view: str = Query(default="canon"),
    db: Session = Depends(get_db),
):
    """View the timeline for a world."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    if view not in ("canon", "all", "non_canon"):
        view = "canon"

    events = TimelineService.get_timeline_events(db, world_id, view=view)
    return templates.TemplateResponse(request, "timeline/index.html", {
        "world": world, "events": events, "view": view,
    })
