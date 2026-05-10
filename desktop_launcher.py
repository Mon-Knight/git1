#!/usr/bin/env python
"""
AI World Engine - Desktop Launcher
Launches the FastAPI backend in a background thread and opens a
pywebview desktop window.

v1.3.1: Added desktop logging, startup self-check, and configuration reporting.
"""

import os
import sys
import socket
import threading
import time
import logging
from pathlib import Path

# Suppress pywebview's default logging unless debugging
logging.getLogger("pywebview").setLevel(logging.WARNING)


# ── Log directory and logging setup ──────────────────────────────────────────

def get_log_dir() -> str:
    """Return the desktop log directory, creating it if necessary."""
    if sys.platform == "win32":
        appdata = os.getenv("LOCALAPPDATA", "")
        if appdata:
            log_dir = os.path.join(appdata, "AIWorldEngine", "logs")
        else:
            log_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "AIWorldEngine", "logs")
    else:
        log_dir = os.path.join(os.path.expanduser("~"), ".AIWorldEngine", "logs")
    os.makedirs(log_dir, exist_ok=True)
    return log_dir


def _setup_desktop_logging(log_dir: str) -> logging.Logger:
    """Configure desktop logger that writes to desktop.log and error.log."""
    logger = logging.getLogger("desktop")
    logger.setLevel(logging.DEBUG)

    # Console handler (always active)
    if not logger.handlers:
        console = logging.StreamHandler(sys.stdout)
        console.setLevel(logging.INFO)
        console.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
        logger.addHandler(console)

        # desktop.log — all messages
        try:
            desktop_fh = logging.FileHandler(
                os.path.join(log_dir, "desktop.log"), encoding="utf-8"
            )
            desktop_fh.setLevel(logging.DEBUG)
            desktop_fh.setFormatter(
                logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
            )
            logger.addHandler(desktop_fh)
        except Exception:
            logger.warning(f"Cannot write to {log_dir}/desktop.log")

        # error.log — warnings and above
        try:
            error_fh = logging.FileHandler(
                os.path.join(log_dir, "error.log"), encoding="utf-8"
            )
            error_fh.setLevel(logging.WARNING)
            error_fh.setFormatter(
                logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
            )
            logger.addHandler(error_fh)
        except Exception:
            logger.warning(f"Cannot write to {log_dir}/error.log")

    return logger


# ── Server log handler ──────────────────────────────────────────────────────

def _setup_server_logging(log_dir: str) -> None:
    """Configure a file handler for uvicorn/server messages → server.log."""
    try:
        server_logger = logging.getLogger("server")
        server_logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(
            os.path.join(log_dir, "server.log"), encoding="utf-8"
        )
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )
        server_logger.addHandler(fh)
    except Exception:
        pass


# ── Self-check ──────────────────────────────────────────────────────────────

def run_self_check(logger: logging.Logger) -> dict:
    """
    Run startup self-checks and return a results dict.

    Returns:
        {
            "version": str,
            "is_pyinstaller": bool,
            "template_ok": bool,
            "static_ok": bool,
            "ai_template_ok": bool,
            "ai_modules_ok": bool,
            "db_dir_ok": bool,
            "db_dir_writable": bool,
            "port_ok": bool,
            "issues": list[str]
        }
    """
    from app.config import settings, resource_path

    issues = []
    version = settings.VERSION
    is_pyinstaller = hasattr(sys, "_MEIPASS")

    logger.info(f"=== AI World Engine v{version} Self-Check ===")
    logger.info(f"Version: {version}")
    logger.info(f"Mode: {'PyInstaller EXE' if is_pyinstaller else 'Source (python)'}")

    # 1. Template check
    tpl = resource_path("app/templates")
    template_ok = os.path.isdir(tpl)
    if not template_ok:
        issues.append(f"Templates directory missing: {tpl}")
        logger.error(f"❌ Templates: MISSING ({tpl})")
    else:
        logger.info(f"✅ Templates: {tpl}")

    # 2. Static check
    static = resource_path("app/static")
    static_ok = os.path.isdir(static)
    if not static_ok:
        issues.append(f"Static directory missing: {static}")
        logger.error(f"❌ Static: MISSING ({static})")
    else:
        logger.info(f"✅ Static: {static}")

    # 3. AI settings template
    ai_tpl = resource_path("app/templates/settings/ai.html")
    ai_template_ok = os.path.isfile(ai_tpl)
    if not ai_template_ok:
        issues.append(f"AI settings template missing: {ai_tpl}")
        logger.error(f"❌ AI settings template: MISSING ({ai_tpl})")
    else:
        logger.info(f"✅ AI settings template: {ai_tpl}")

    # 4. AI modules importable
    ai_modules_ok = True
    ai_modules = [
        "app.services.ai.mock_client",
        "app.services.ai.openai_compatible_client",
        "app.services.ai.model_router",
        "app.services.ai.prompt_builder",
        "app.services.ai.response_parser",
        "app.services.settings_service",
    ]
    for mod_name in ai_modules:
        try:
            __import__(mod_name)
        except ImportError as e:
            ai_modules_ok = False
            issues.append(f"Cannot import {mod_name}: {e}")
            logger.error(f"❌ AI module: {mod_name} — {e}")
    if ai_modules_ok:
        logger.info("✅ AI modules: all importable")

    # 5. Database directory
    db_dir_ok = False
    db_dir_writable = False
    if sys.platform == "win32":
        appdata = os.getenv("LOCALAPPDATA", "")
        if appdata:
            db_dir = os.path.join(appdata, "AIWorldEngine")
            db_dir_ok = os.path.isdir(db_dir)
            if not db_dir_ok:
                try:
                    os.makedirs(db_dir, exist_ok=True)
                    db_dir_ok = True
                except Exception as e:
                    issues.append(f"Cannot create DB directory {db_dir}: {e}")
                    logger.error(f"❌ DB directory: cannot create {db_dir} — {e}")
        else:
            issues.append("LOCALAPPDATA not set; DB directory unknown")
            logger.warning("⚠️ LOCALAPPDATA not set")

    # 6. Port
    try:
        port = find_free_port()
        logger.info(f"✅ Port available: {port}")
        port_ok = True
    except RuntimeError as e:
        port = None
        port_ok = False
        issues.append(f"No free port found: {e}")
        logger.error(f"❌ Port: {e}")

    # Log AI config (without key)
    logger.info(f"AI base_url: {settings.AI_BASE_URL}")
    logger.info(f"AI model: {settings.AI_MODEL}")
    logger.info(f"AI mode: {'Mock' if settings.is_mock_ai else 'Live (via .env)'}")
    logger.info(f"Database URL: {settings.DATABASE_URL}")
    if issues:
        logger.warning(f"Self-check found {len(issues)} issue(s)")
    else:
        logger.info("✅ Self-check passed — no issues")

    return {
        "version": version,
        "is_pyinstaller": is_pyinstaller,
        "template_ok": template_ok,
        "static_ok": static_ok,
        "ai_template_ok": ai_template_ok,
        "ai_modules_ok": ai_modules_ok,
        "db_dir_ok": db_dir_ok,
        "db_dir_writable": db_dir_writable,
        "port_ok": port_ok,
        "issues": issues,
    }


# ── Utility functions ──────────────────────────────────────────────────────

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
    """Force PyInstaller to bundle all app modules at analysis time."""
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
    import app.services.settings_service  # noqa: F401
    import app.services.ai  # noqa: F401
    import app.services.ai.base  # noqa: F401
    import app.services.ai.errors  # noqa: F401
    import app.services.ai.mock_client  # noqa: F401
    import app.services.ai.openai_compatible_client  # noqa: F401
    import app.services.ai.model_router  # noqa: F401
    import app.services.ai.prompt_builder  # noqa: F401
    import app.services.ai.response_parser  # noqa: F401
    import app.routes.settings  # noqa: F401


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    """Main entry point for the desktop launcher."""
    # 1. Setup logging
    log_dir = get_log_dir()
    logger = _setup_desktop_logging(log_dir)
    _setup_server_logging(log_dir)

    logger.info(f"=== AI World Engine Desktop Launcher ===")
    logger.info(f"Log directory: {log_dir}")

    # 2. Configure database path for desktop mode
    _configure_desktop_db(logger)
    logger.info(f"Database URL: {os.environ.get('DATABASE_URL', '(default)')}")

    # 3. Run self-check
    check_result = run_self_check(logger)
    if check_result["issues"]:
        for issue in check_result["issues"]:
            logger.warning(f"Self-check issue: {issue}")

    # 4. Find a free port
    try:
        port = find_free_port()
    except RuntimeError as e:
        logger.critical(f"No free port available: {e}")
        print(f"ERROR: {e}")
        sys.exit(1)

    host = "127.0.0.1"
    url = f"http://{host}:{port}"
    logger.info(f"Server will listen on {url}")

    # 5. Start FastAPI in background thread
    server_thread = threading.Thread(
        target=run_uvicorn,
        args=(host, port),
        daemon=True,
    )
    server_thread.start()

    # 6. Wait for server to be ready
    logger.info("Waiting for server to start...")
    print(f"Starting AI World Engine server on {url} ...")
    if not wait_for_server(f"{url}/health"):
        logger.error("Server failed to start within timeout.")
        print("ERROR: Server failed to start within timeout.")
        sys.exit(1)

    # 7. Health check
    try:
        import urllib.request
        import json as _json
        resp = urllib.request.urlopen(f"{url}/health", timeout=5)
        data = _json.loads(resp.read().decode())
        logger.info(f"Health check: {data}")
    except Exception as e:
        logger.warning(f"Health check failed: {e}")

    logger.info(f"Server ready on {url}")
    print(f"Server ready. Opening desktop window...")

    # 8. Open desktop window
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
        logger.error(f"Desktop window failed: {e}", exc_info=True)
        # Fallback: open in browser
        logger.info("Falling back to system browser...")
        try:
            import webbrowser
            webbrowser.open(url)
            logger.info(f"Opened {url} in system browser. Press Ctrl+C to stop.")
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            logger.info("Shutting down.")
        except Exception as e2:
            logger.critical(f"Cannot start server or open browser: {e2}", exc_info=True)
            sys.exit(1)


def _configure_desktop_db(logger: logging.Logger = None):
    """Set the database path to the Windows AppData directory for desktop mode."""
    if os.getenv("DATABASE_URL"):
        if logger:
            logger.info("Using explicit DATABASE_URL from environment")
        return  # User explicitly configured

    if sys.platform == "win32":
        appdata = os.getenv("LOCALAPPDATA")
        if appdata:
            db_dir = os.path.join(appdata, "AIWorldEngine")
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, "ai_world_engine.db")
            os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
            if logger:
                logger.info(f"Desktop database path: {db_path}")
        else:
            if logger:
                logger.warning("LOCALAPPDATA not set; using default database path")
    else:
        if logger:
            logger.info("Non-Windows platform; using default database path")


if __name__ == "__main__":
    main()
