"""
AI World Engine - FastAPI Application Entry Point
"""

from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.config import settings, resource_path
from app.database import init_db
from app.routes.pages import router as pages_router
from app.routes.worlds import router as worlds_router
from app.routes.characters import router as characters_router
from app.routes.factions import router as factions_router
from app.routes.locations import router as locations_router
from app.routes.rules import router as rules_router
from app.routes.events import router as events_router
from app.routes.timeline import router as timeline_router
from app.routes.simulation import router as simulation_router
from app.routes.records import router as records_router
from app.routes.branches import router as branches_router
from app.routes.checks import router as checks_router
from app.routes.settings import router as settings_router
from app.routes.novel import router as novel_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on application startup."""
    from app.database import SessionLocal
    from app.services.settings_service import SettingsService
    init_db()
    # Seed default settings
    db = SessionLocal()
    try:
        SettingsService.init_defaults(db)
    finally:
        db.close()
    yield


# Initialize FastAPI app
app = FastAPI(
    title="AI World Engine",
    description="AI 小说世界观推演系统",
    version=settings.VERSION,
    lifespan=lifespan,
)

# Mount static files (uses resource_path for PyInstaller compatibility)
static_dir = resource_path("app/static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Include routers
app.include_router(pages_router)
app.include_router(worlds_router)
app.include_router(characters_router)
app.include_router(factions_router)
app.include_router(locations_router)
app.include_router(rules_router)
app.include_router(events_router)
app.include_router(timeline_router)
app.include_router(simulation_router)
app.include_router(records_router)
app.include_router(branches_router)
app.include_router(checks_router)
app.include_router(settings_router)
app.include_router(novel_router)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "version": settings.VERSION,
        "mock_ai": settings.is_mock_ai,
    }
