"""
AI World Engine - Branch Routes
Branch listing and detail viewing.
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.world_service import WorldService
from app.services.branch_service import BranchService

router = APIRouter(prefix="/worlds/{world_id}/branches")

templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


@router.get("", response_class=HTMLResponse)
async def list_branches(request: Request, world_id: int, db: Session = Depends(get_db)):
    """List all branches for a world."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    branches = BranchService.list_branches(db, world_id)
    return templates.TemplateResponse(request, "branches/list.html", {
        "world": world, "branches": branches
    })


@router.get("/{branch_id}", response_class=HTMLResponse)
async def branch_detail(request: Request, world_id: int, branch_id: int, db: Session = Depends(get_db)):
    """Show a branch detail."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    branch = BranchService.get_branch(db, branch_id)
    if not branch or branch.world_id != world_id:
        return templates.TemplateResponse(request, "branches/404.html", {
            "world": world, "resource_id": branch_id
        }, status_code=404)

    return templates.TemplateResponse(request, "branches/detail.html", {
        "world": world, "branch": branch
    })
