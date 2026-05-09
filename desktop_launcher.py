#!/usr/bin/env python
"""
AI World Engine - Desktop Launcher
Launches the FastAPI backend in a background thread and opens a
pywebview desktop window.
"""

import os
import sys
import socket
import threading
import time
import logging

# Suppress pywebview's default logging unless debugging
logging.getLogger("pywebview").setLevel(logging.WARNING)


def find_free_port(start: int = 8000, end: int = 9000) -> int:
    """Find a free TCP port in the given range."""
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.1)
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise RuntimeError(f"No free port found in range {start}-{end}")


def wait_for_server(url: str, timeout: int = 30) -> bool:
    """Wait until the server responds or timeout is reached."""
    import urllib.request
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(url, timeout=1)
            return True
        except Exception:
            time.sleep(0.5)
    return False


def run_uvicorn(host: str, port: int):
    """Run uvicorn in the current thread (for background thread use)."""
    import uvicorn
    from app.main import app
    uvicorn.run(app, host=host, port=port, log_level="warning")


def _ensure_pyinstaller_imports():
    """Force PyInstaller to bundle all app modules at analysis time.
    This function is never actually called at runtime — it exists only
    so that PyInstaller's import tracer discovers all app.* modules."""
    import app.main  # noqa: F401
    import app.config  # noqa: F401
    import app.database  # noqa: F401
    import app.models  # noqa: F401
    import app.routes.pages  # noqa: F401
    import app.routes.worlds  # noqa: F401
    import app.routes.characters  # noqa: F401
    import app.routes.factions  # noqa: F401
    import app.routes.locations  # noqa: F401
    import app.routes.rules  # noqa: F401
    import app.routes.events  # noqa: F401
    import app.routes.timeline  # noqa: F401
    import app.routes.simulation  # noqa: F401
    import app.routes.records  # noqa: F401
    import app.routes.branches  # noqa: F401
    import app.routes.checks  # noqa: F401
    import app.services.ai_service  # noqa: F401
    import app.services.world_service  # noqa: F401
    import app.services.character_service  # noqa: F401
    import app.services.faction_service  # noqa: F401
    import app.services.location_service  # noqa: F401
    import app.services.rule_service  # noqa: F401
    import app.services.event_service  # noqa: F401
    import app.services.timeline_service  # noqa: F401
    import app.services.simulation_service  # noqa: F401
    import app.services.record_action_service  # noqa: F401
    import app.services.branch_service  # noqa: F401
    import app.services.check_service  # noqa: F401
    import app.services.consistency_service  # noqa: F401
    import app.services.behavior_service  # noqa: F401
    import app.services.world_context_service  # noqa: F401


def main():
    """Main entry point for the desktop launcher."""
    # Configure database path for desktop mode
    _configure_desktop_db()

    # Find a free port
    try:
        port = find_free_port()
    except RuntimeError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    host = "127.0.0.1"
    url = f"http://{host}:{port}"

    # Start FastAPI in background thread
    server_thread = threading.Thread(
        target=run_uvicorn,
        args=(host, port),
        daemon=True,
    )
    server_thread.start()

    # Wait for server to be ready
    print(f"Starting AI World Engine server on {url} ...")
    if not wait_for_server(f"{url}/health"):
        print("ERROR: Server failed to start within timeout.")
        sys.exit(1)

    print(f"Server ready. Opening desktop window...")

    # Open desktop window
    try:
        import webview
        window = webview.create_window(
            title="AI World Engine",
            url=url,
            width=1280,
            height=800,
            min_size=(800, 600),
            resizable=True,
        )
        webview.start()
    except Exception as e:
        print(f"ERROR: Failed to open desktop window: {e}")
        sys.exit(1)


def _configure_desktop_db():
    """Set the database path to the Windows AppData directory for desktop mode."""
    if os.getenv("DATABASE_URL"):
        return  # User explicitly configured

    if sys.platform == "win32":
        appdata = os.getenv("LOCALAPPDATA")
        if appdata:
            db_dir = os.path.join(appdata, "AIWorldEngine")
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, "ai_world_engine.db")
            os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"


if __name__ == "__main__":
    main()
