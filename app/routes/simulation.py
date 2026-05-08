"""
AI World Engine - Simulation Routes
AI simulation page and submission.
"""

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.world_service import WorldService
from app.services.simulation_service import SimulationService
from app.services.world_context_service import WorldContextService

router = APIRouter(prefix="/worlds/{world_id}/simulation")

templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


@router.get("", response_class=HTMLResponse)
async def simulation_page(request: Request, world_id: int, db: Session = Depends(get_db)):
    """Show the AI simulation page."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    context = WorldContextService.build_world_context(db, world_id)
    context_snapshot = WorldContextService.build_context_snapshot(context)

    return templates.TemplateResponse(request, "simulation/index.html", {
        "world": world,
        "context_snapshot": context_snapshot,
        "errors": {},
        "result": None,
    })


@router.post("", response_class=HTMLResponse)
async def run_simulation(
    request: Request,
    world_id: int,
    question: str = Form(default=""),
    simulation_type: str = Form(default=""),
    db: Session = Depends(get_db),
):
    """Submit a simulation question and show the result."""
    world = WorldService.get_world(db, world_id)
    if not world:
        return templates.TemplateResponse(
            request, "worlds/404.html", {"world_id": world_id}, status_code=404
        )

    errors = {}
    if not question or not question.strip():
        errors["question"] = "推演问题不能为空"
    elif len(question.strip()) > 1000:
        errors["question"] = "推演问题不能超过1000个字符"

    if errors:
        context = WorldContextService.build_world_context(db, world_id)
        context_snapshot = WorldContextService.build_context_snapshot(context)
        return templates.TemplateResponse(request, "simulation/index.html", {
            "world": world,
            "context_snapshot": context_snapshot,
            "errors": errors,
            "form_data": {"question": question, "simulation_type": simulation_type},
            "result": None,
        }, status_code=422)

    try:
        record = SimulationService.run_simulation(
            db=db,
            world_id=world_id,
            question=question.strip(),
            simulation_type=simulation_type.strip(),
        )

        context = WorldContextService.build_world_context(db, world_id)
        context_snapshot = WorldContextService.build_context_snapshot(context)

        return templates.TemplateResponse(request, "simulation/index.html", {
            "world": world,
            "context_snapshot": context_snapshot,
            "errors": {},
            "result": {
                "id": record.id,
                "question": record.question,
                "simulation_type": record.simulation_type,
                "ai_response": record.ai_response,
                "status": record.status,
                "is_mock": record.is_mock,
                "created_at": record.created_at.strftime("%Y-%m-%d %H:%M"),
            },
        })
    except Exception as e:
        context = WorldContextService.build_world_context(db, world_id)
        context_snapshot = WorldContextService.build_context_snapshot(context)
        return templates.TemplateResponse(request, "simulation/index.html", {
            "world": world,
            "context_snapshot": context_snapshot,
            "errors": {"submit": f"AI 推演出错: {str(e)}"},
            "form_data": {"question": question, "simulation_type": simulation_type},
            "result": None,
        }, status_code=500)
