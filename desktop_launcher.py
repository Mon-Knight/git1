#!/usr/bin/env python
"""
AI World Engine - Desktop Launcher
Launches the FastAPI backend in a background thread and opens a
pywebview desktop window.

v1.3.4: Fixed backend server startup, added full exception logging,
server.log capture with uvicorn log_config, headless mode, error dialog.
"""

import os
import sys
import socket
import threading
import time
import logging
import io
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


# ── Server logging ──────────────────────────────────────────────────────────

SERVER_LOG_PATH = None  # Set during startup, read by server thread

def _setup_server_file_logger(log_dir: str) -> logging.Logger:
    """Create a dedicated server file logger that uvicorn can use."""
    global SERVER_LOG_PATH
    SERVER_LOG_PATH = os.path.join(log_dir, "server.log")
    srv = logging.getLogger("server")
    srv.setLevel(logging.DEBUG)
    for h in list(srv.handlers):
        srv.removeHandler(h)
    fh = logging.FileHandler(SERVER_LOG_PATH, encoding="utf-8", mode="a")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"))
    srv.addHandler(fh)
    return srv


# ── Stdio safety & uvicorn log config ──────────────────────────────────────

def ensure_stdio_available():
    """
    Ensure sys.stdout and sys.stderr are not None.
    In PyInstaller --windowed EXEs, they can be None, and any library that
    calls .isatty() on them (e.g. uvicorn's DefaultFormatter) will crash
    with AttributeError: 'NoneType' object has no attribute 'isatty'.
    """
    import os as _os
    import sys as _sys
    if _sys.stdout is None:
        _sys.stdout = open(_os.devnull, "w", encoding="utf-8")
    if _sys.stderr is None:
        _sys.stderr = open(_os.devnull, "w", encoding="utf-8")


def build_uvicorn_log_config(server_log_path: str) -> dict:
    """
    Build a safe uvicorn logging config that writes to a file only.
    Uses plain logging.Formatter — NOT uvicorn.logging.DefaultFormatter
    or AccessFormatter, which call isatty() and crash in PyInstaller EXEs.
    """
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%H:%M:%S",
            },
            "access": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%H:%M:%S",
            },
        },
        "handlers": {
            "server_file": {
                "class": "logging.FileHandler",
                "filename": server_log_path,
                "mode": "a",
                "encoding": "utf-8",
                "formatter": "default",
            }
        },
        "loggers": {
            "uvicorn": {
                "handlers": ["server_file"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["server_file"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["server_file"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }


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
        logger.error(f"[ERROR] Templates: MISSING ({tpl})")
    else:
        logger.info(f"[OK] Templates: {tpl}")

    # 2. Static check
    static = resource_path("app/static")
    static_ok = os.path.isdir(static)
    if not static_ok:
        issues.append(f"Static directory missing: {static}")
        logger.error(f"[ERROR] Static: MISSING ({static})")
    else:
        logger.info(f"[OK] Static: {static}")

    # 3. AI settings template
    ai_tpl = resource_path("app/templates/settings/ai.html")
    ai_template_ok = os.path.isfile(ai_tpl)
    if not ai_template_ok:
        issues.append(f"AI settings template missing: {ai_tpl}")
        logger.error(f"[ERROR] AI settings template: MISSING ({ai_tpl})")
    else:
        logger.info(f"[OK] AI settings template: {ai_tpl}")

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
            logger.error(f"[ERROR] AI module: {mod_name} - {e}")
    if ai_modules_ok:
        logger.info("[OK] AI modules: all importable")

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
                    logger.error(f"[ERROR] DB directory: cannot create {db_dir} - {e}")
            if db_dir_ok:
                try:
                    test_file = os.path.join(db_dir, ".write_test")
                    with open(test_file, "w") as f:
                        f.write("test")
                    os.remove(test_file)
                    db_dir_writable = True
                    logger.info(f"[OK] DB directory: {db_dir} (writable)")
                except Exception as e:
                    issues.append(f"DB directory not writable: {e}")
                    logger.error(f"[ERROR] DB directory: not writable - {e}")
        else:
            issues.append("LOCALAPPDATA not set; DB directory unknown")
            logger.warning("[WARN] LOCALAPPDATA not set")

    # 6. Port
    try:
        port = find_free_port()
        logger.info(f"[OK] Port available: {port}")
        port_ok = True
    except RuntimeError as e:
        port = None
        port_ok = False
        issues.append(f"No free port found: {e}")
        logger.error(f"[ERROR] Port: {e}")

    # Log AI config (without key)
    logger.info(f"AI base_url: {settings.AI_BASE_URL}")
    logger.info(f"AI model: {settings.AI_MODEL}")
    logger.info(f"AI mode: {'Mock' if settings.is_mock_ai else 'Live (via .env)'}")
    logger.info(f"Database URL: {settings.DATABASE_URL}")
    if issues:
        logger.warning(f"Self-check found {len(issues)} issue(s)")
    else:
        logger.info("[OK] Self-check passed - no issues")

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


def wait_for_server(url: str, timeout: int = 30, logger=None) -> bool:
    """Wait until the server responds, logging each failure for diagnosis."""
    import urllib.request
    deadline = time.time() + timeout
    attempt = 0
    last_error = None
    while time.time() < deadline:
        try:
            attempt += 1
            urllib.request.urlopen(url, timeout=1)
            if logger:
                logger.info(f"Health check OK on attempt {attempt}")
            return True
        except Exception as e:
            last_error = e
            if logger:
                logger.debug(f"Health check attempt {attempt}/{int(timeout*2)} failed: {type(e).__name__}: {e}")
            time.sleep(0.5)
    if logger:
        logger.error(f"Server failed to start within {timeout}s. Last error: {type(last_error).__name__}: {last_error}")
    return False


def start_server(host: str, port: int, log_dir: str, logger: logging.Logger):
    """
    Start uvicorn in the current thread. Fully wrapped for EXE reliability.

    - Imports app.main:app directly (never uses string import in PyInstaller)
    - Configures uvicorn logging to write to server.log file
    - Captures all exceptions with full traceback to server.log and error.log
    """
    try:
        logger.info(f"Backend: importing app.main...")
        from app.main import app  # noqa: F811 - direct import, not string
        logger.info("Backend: FastAPI app imported successfully")
    except BaseException as e:
        logger.exception("Backend: FAILED to import app.main")
        if SERVER_LOG_PATH:
            try:
                with open(SERVER_LOG_PATH, "a", encoding="utf-8") as f:
                    import traceback
                    f.write(f"\n=== APP IMPORT FAILED ===\n")
                    traceback.print_exc(file=f)
            except Exception:
                pass
        raise

    logger.info(f"Backend: starting uvicorn on {host}:{port}...")
    import uvicorn

    # Safety: ensure stdio is available (PyInstaller --windowed may have None)
    ensure_stdio_available()

    # Build safe uvicorn log config (no DefaultFormatter, no use_colors, no isatty())
    log_config = build_uvicorn_log_config(SERVER_LOG_PATH) if SERVER_LOG_PATH else None

    try:
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_config=log_config,
            log_level="info",
            access_log=True,
            loop="asyncio",
            http="h11",
        )
    except BaseException as e:
        logger.exception(f"Backend: uvicorn crashed with {type(e).__name__}")
        if SERVER_LOG_PATH:
            try:
                with open(SERVER_LOG_PATH, "a", encoding="utf-8") as f:
                    import traceback
                    f.write(f"\n=== UVICORN CRASH ===\n")
                    traceback.print_exc(file=f)
            except Exception:
                pass
        raise


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
    import app.routes.novel  # noqa: F401
    import app.routes.data  # noqa: F401


# ── Main ────────────────────────────────────────────────────────────────────

def _show_error_dialog(message: str, log_dir: str):
    """Show an error dialog using tkinter (always available on Windows)."""
    try:
        import tkinter.messagebox as mb
        from tkinter import Tk
        root = Tk()
        root.withdraw()
        mb.showerror(
            "AI World Engine — 启动失败",
            f"{message}\n\n"
            f"错误日志路径：\n{log_dir}\\server.log\n{log_dir}\\error.log\n\n"
            f"请查看上述文件获取详细错误信息，或联系开发者。"
        )
        root.destroy()
    except Exception:
        pass  # If even tkinter fails, we still have log files


def main():
    """Main entry point for the desktop launcher."""
    # 0a. Safety: ensure stdio is available (PyInstaller --windowed may set them to None)
    ensure_stdio_available()

    # 0b. Check for headless mode (for automated verification)
    headless = os.getenv("AIWORLDENGINE_HEADLESS", "0") in ("1", "true", "True", "yes")

    # 1. Setup logging
    log_dir = get_log_dir()
    logger = _setup_desktop_logging(log_dir)
    _setup_server_file_logger(log_dir)

    logger.info(f"=== AI World Engine Desktop Launcher ===")
    logger.info(f"Log directory: {log_dir}")
    if headless:
        logger.info("HEADLESS mode — no desktop window")

    # 2. Configure database path for desktop mode
    _configure_desktop_db(logger)
    logger.info(f"Database URL: {os.environ.get('DATABASE_URL', '(default)')}")

    # Set desktop mode flag for the backend to detect
    os.environ["AIWE_DESKTOP_MODE"] = "1"

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
        _show_error_dialog(f"无法获取可用端口: {e}", log_dir)
        sys.exit(1)

    host = "127.0.0.1"
    url = f"http://{host}:{port}"
    logger.info(f"Server will listen on {url}")

    # 5. Start FastAPI in background thread (uses start_server for full logging)
    server_thread = threading.Thread(
        target=start_server,
        args=(host, port, log_dir, logger),
        daemon=True,
    )
    server_thread.start()

    # 6. Wait for server to be ready (with detailed failure logging)
    logger.info("Waiting for server to start...")
    print(f"Starting AI World Engine server on {url} ...")
    if not wait_for_server(f"{url}/health", logger=logger):
        logger.error("Server failed to start within timeout.")
        _show_error_dialog("后端服务未能启动。请查看日志文件获取详细错误信息。", log_dir)
        if headless:
            time.sleep(3)
        sys.exit(1)

    # 7. Health check (with more detail)
    try:
        import urllib.request
        import json as _json
        resp = urllib.request.urlopen(f"{url}/health", timeout=5)
        data = _json.loads(resp.read().decode())
        logger.info(f"Health check: version={data.get('version')}, status={data.get('status')}")
    except Exception as e:
        logger.warning(f"Health check detail fetch failed: {e}")

    logger.info(f"Server ready on {url}")
    print(f"Server ready. Opening desktop window...")

    # 8. Open desktop window (or stay in headless mode)
    if headless:
        logger.info("HEADLESS mode: server is running, no window will open.")
        logger.info(f"Server URL: {url}")
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            logger.info("Shutting down (keyboard interrupt).")
        return

    try:
        import webview

        class DesktopExportApi:
            """API exposed to the webview for desktop file operations."""

            def choose_save_path(self, default_filename: str = "export.json",
                                 file_types: list = None):
                """Open a native save-file dialog. Returns dict with path or cancelled."""
                try:
                    if file_types is None:
                        file_types = ["JSON 文件 (*.json)", "所有文件 (*.*)"]

                    result = window.create_file_dialog(
                        webview.SAVE_DIALOG,
                        save_filename=default_filename,
                        file_types=file_types,
                    )
                    if result:
                        return {"ok": True, "path": result}
                    else:
                        return {"ok": False, "cancelled": True}
                except Exception as e:
                    return {"ok": False, "error": str(e)}

        api = DesktopExportApi()

        # Read configured window size from app settings
        win_width, win_height = 1280, 820
        try:
            from app.services.app_settings_service import AppSettingsService
            win_width, win_height = AppSettingsService.get_window_size()
            logger.info(f"Window size from settings: {win_width}x{win_height}")
        except Exception:
            logger.info(f"Using default window size: 1280x820")

        window = webview.create_window(
            title="AI World Engine",
            url=url,
            width=win_width,
            height=win_height,
            min_size=(1024, 700),
            resizable=True,
            js_api=api,
        )
        webview.start()
    except Exception as e:
        logger.error(f"Desktop window failed: {e}", exc_info=True)
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
            _show_error_dialog(f"无法打开桌面窗口或浏览器: {e2}", log_dir)
            sys.exit(1)


def _configure_desktop_db(logger: logging.Logger = None):
    """Set the database path to the Windows AppData directory for desktop mode."""
    if os.getenv("DATABASE_URL"):
        if logger:
            logger.info("Using explicit DATABASE_URL from environment")
        return

    if sys.platform == "win32":
        appdata = os.getenv("LOCALAPPDATA")
        if appdata:
            db_dir = os.path.join(appdata, "AIWorldEngine")
            os.makedirs(db_dir, exist_ok=True)
            # Use forward slashes for SQLite URL on Windows
            db_path = Path(db_dir) / "ai_world_engine.db"
            os.environ["DATABASE_URL"] = f"sqlite:///{db_path.as_posix()}"
            if logger:
                logger.info(f"Desktop database path: {db_path}")
                logger.info(f"Desktop DATABASE_URL: sqlite:///{db_path.as_posix()}")
        else:
            if logger:
                logger.warning("LOCALAPPDATA not set; using default database path")
    else:
        if logger:
            logger.info("Non-Windows platform; using default database path")


if __name__ == "__main__":
    main()
