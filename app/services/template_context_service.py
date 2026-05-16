"""
AI World Engine - Template Context Service
v2.0.1.3: Centralized base template context builder.

Ensures that ALL world-specific pages have a consistent `current_world`
variable available for the sidebar navigation in base.html.

Usage in routes:
    from app.services.template_context_service import build_base_context
    ctx = build_base_context(request, world=world, active_nav="assets")
    return templates.TemplateResponse(request, "page.html", ctx)
"""

from app.config import settings


def build_base_context(
    request,
    world=None,
    current_world=None,
    active_nav=None,
    **extra_context,
) -> dict:
    """
    Build a consistent base context dict for template rendering.

    Priority for determining the effective world:
    1. Explicit `current_world` parameter
    2. `world` parameter (fallback — critical for pages that pass
       "world" but not "current_world")
    3. None (no world context)

    Args:
        request: The FastAPI Request object (required by Jinja2).
        world: The world object for the current page (fallback).
        current_world: Explicit current_world for sidebar.
        active_nav: Active navigation key (dashboard, worlds, novel,
                    assets, simulation, checks, settings, data).
        **extra_context: Additional template variables.

    Returns:
        dict with at least: request, app_version, active_nav, current_world
    """
    effective_world = current_world or world

    context = {
        "request": request,
        "app_version": settings.VERSION,
        "active_nav": active_nav or "",
    }

    if effective_world is not None:
        context["current_world"] = effective_world
        context["current_world_id"] = effective_world.id

    # Merge extra context (overwrites above keys if intentionally passed)
    context.update(extra_context)

    # Ensure `world` is always available if provided (pages may still reference it)
    if world is not None and "world" not in context:
        context["world"] = world

    return context
