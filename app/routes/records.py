"""
AI World Engine - Records Routes
Simulation record listing, detail viewing, and actions (adopt/branch).
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.world_service import WorldService
from app.services.simulation_service import SimulationService
from app.services.record_action_service import RecordActionService

router = APIRouter(prefix="/worlds/{world_id}/records")

templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


@router.get("", response_class=HTMLResponse)
async def list_records(request: Request, world_id: int, db: Session = Depends(get_db)):
    """List all simulation records for a world."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    records = SimulationService.list_simulation_records(db, world_id)
    return templates.TemplateResponse(request, "records/list.html", {
        "world": world, "records": records
    })


@router.get("/{record_id}", response_class=HTMLResponse)
async def record_detail(request: Request, world_id: int, record_id: int, db: Session = Depends(get_db)):
    """Show a simulation record detail."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    record = SimulationService.get_simulation_record(db, record_id)
    if not record or record.world_id != world_id:
        return templates.TemplateResponse(request, "records/404.html", {
            "world": world, "resource_id": record_id
        }, status_code=404)

    return templates.TemplateResponse(request, "records/detail.html", {
        "world": world, "record": record
    })


@router.post("/{record_id}/adopt")
async def adopt_record(request: Request, world_id: int, record_id: int, db: Session = Depends(get_db)):
    """Adopt a simulation record as a canon historical event."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    # Check record exists and belongs to this world
    record = SimulationService.get_simulation_record(db, record_id)
    if not record or record.world_id != world_id:
        return templates.TemplateResponse(request, "records/404.html", {
            "world": world, "resource_id": record_id
        }, status_code=404)

    event, error = RecordActionService.adopt_record_as_canon(db, record_id, world_id)
    if error:
        record = SimulationService.get_simulation_record(db, record_id)
        return templates.TemplateResponse(request, "records/detail.html", {
            "world": world, "record": record,
            "action_error": error,
        }, status_code=400)

    return RedirectResponse(url=f"/worlds/{world_id}/events/{event.id}", status_code=303)


@router.post("/{record_id}/branch")
async def branch_record(request: Request, world_id: int, record_id: int, db: Session = Depends(get_db)):
    """Save a simulation record as a branch."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    # Check record exists and belongs to this world
    record = SimulationService.get_simulation_record(db, record_id)
    if not record or record.world_id != world_id:
        return templates.TemplateResponse(request, "records/404.html", {
            "world": world, "resource_id": record_id
        }, status_code=404)

    branch, error = RecordActionService.save_record_as_branch(db, record_id, world_id)
    if error:
        record = SimulationService.get_simulation_record(db, record_id)
        return templates.TemplateResponse(request, "records/detail.html", {
            "world": world, "record": record,
            "action_error": error,
        }, status_code=400)

    return RedirectResponse(url=f"/worlds/{world_id}/branches/{branch.id}", status_code=303)
