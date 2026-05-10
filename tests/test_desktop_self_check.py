"""
AI World Engine - Test Desktop Self-Check
Tests for the desktop startup self-check.
"""

import os
import sys
import tempfile
import logging
import pytest


def _make_logger():
    """Create a minimal test logger."""
    logger = logging.getLogger("test_selfcheck")
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        logger.addHandler(logging.NullHandler())
    return logger


def test_self_check_structure():
    """run_self_check should return a dict with expected keys."""
    from desktop_launcher import run_self_check
    logger = _make_logger()
    # Ensure we're in source mode (not PyInstaller)
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ["LOCALAPPDATA"] = tmpdir
        try:
            result = run_self_check(logger)
            assert isinstance(result, dict)
            expected_keys = [
                "version", "is_pyinstaller", "template_ok",
                "static_ok", "ai_template_ok", "ai_modules_ok",
                "db_dir_ok", "db_dir_writable", "port_ok", "issues",
            ]
            for key in expected_keys:
                assert key in result, f"Missing key: {key}"
            # Force reimport of result to verify structure
            assert result["version"] is not None
            assert isinstance(result["issues"], list)
        finally:
            os.environ.pop("LOCALAPPDATA", None)


def test_self_check_template_ok():
    """Self-check should find templates when running from source."""
    from desktop_launcher import run_self_check
    logger = _make_logger()
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ["LOCALAPPDATA"] = tmpdir
        try:
            result = run_self_check(logger)
            assert result["template_ok"] is True, "Templates check failed in source mode"
        finally:
            os.environ.pop("LOCALAPPDATA", None)


def test_self_check_static_ok():
    """Self-check should find static files when running from source."""
    from desktop_launcher import run_self_check
    logger = _make_logger()
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ["LOCALAPPDATA"] = tmpdir
        try:
            result = run_self_check(logger)
            assert result["static_ok"] is True, "Static check failed in source mode"
        finally:
            os.environ.pop("LOCALAPPDATA", None)


def test_self_check_ai_template_ok():
    """Self-check should find settings/ai.html when running from source."""
    from desktop_launcher import run_self_check
    logger = _make_logger()
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ["LOCALAPPDATA"] = tmpdir
        try:
            result = run_self_check(logger)
            assert result["ai_template_ok"] is True, "AI settings template check failed"
        finally:
            os.environ.pop("LOCALAPPDATA", None)


def test_self_check_ai_modules_ok():
    """Self-check should successfully import AI modules in source mode."""
    from desktop_launcher import run_self_check
    logger = _make_logger()
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ["LOCALAPPDATA"] = tmpdir
        try:
            result = run_self_check(logger)
            assert result["ai_modules_ok"] is True, f"AI modules import failed: {result['issues']}"
        finally:
            os.environ.pop("LOCALAPPDATA", None)


def test_self_check_db_dir():
    """Self-check should verify database directory is writable on Windows."""
    from desktop_launcher import run_self_check
    logger = _make_logger()
    if sys.platform == "win32":
        with tempfile.TemporaryDirectory() as tmpdir:
            test_ai_dir = os.path.join(tmpdir, "AIWorldEngine")
            os.makedirs(test_ai_dir, exist_ok=True)
            os.environ["LOCALAPPDATA"] = tmpdir
            try:
                result = run_self_check(logger)
                assert result["db_dir_ok"] is True, f"db_dir_ok failed: {result['issues']}"
            finally:
                os.environ.pop("LOCALAPPDATA", None)
    else:
        pytest.skip("Skipping Windows-only test on non-Windows platform")


def test_self_check_port_ok():
    """Self-check should find an available port."""
    from desktop_launcher import run_self_check
    logger = _make_logger()
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ["LOCALAPPDATA"] = tmpdir
        try:
            result = run_self_check(logger)
            assert result["port_ok"] is True, "Port check failed"
        finally:
            os.environ.pop("LOCALAPPDATA", None)


def test_self_check_no_issues_in_source_mode():
    """In source mode with valid setup, self-check should have zero issues."""
    from desktop_launcher import run_self_check
    logger = _make_logger()
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ["LOCALAPPDATA"] = tmpdir
        try:
            result = run_self_check(logger)
            assert result["issues"] == [], f"Issues found: {result['issues']}"
        finally:
            os.environ.pop("LOCALAPPDATA", None)


def test_self_check_not_pyinstaller_in_source():
    """Source mode should detect is_pyinstaller=False."""
    from desktop_launcher import run_self_check
    logger = _make_logger()
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ["LOCALAPPDATA"] = tmpdir
        try:
            result = run_self_check(logger)
            assert result["is_pyinstaller"] is False
        finally:
            os.environ.pop("LOCALAPPDATA", None)


def test_self_check_reports_version():
    """Self-check should report the current version."""
    from desktop_launcher import run_self_check
    from app.config import settings
    logger = _make_logger()
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ["LOCALAPPDATA"] = tmpdir
        try:
            result = run_self_check(logger)
            assert result["version"] == settings.VERSION
        finally:
            os.environ.pop("LOCALAPPDATA", None)


def test_self_check_does_not_log_api_key():
    """Self-check log output should not contain API key."""
    test_key = "sk-selfcheck-leak-test-123456"
    os.environ["AI_API_KEY"] = test_key
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ["LOCALAPPDATA"] = tmpdir
        try:
            logger = logging.getLogger("test_leakcheck")
            logger.setLevel(logging.DEBUG)
            # Remove old handlers to avoid interference
            logger.handlers.clear()
            fh = logging.FileHandler(os.path.join(tmpdir, "test.log"), encoding="utf-8")
            fh.setLevel(logging.DEBUG)
            logger.addHandler(fh)

            from desktop_launcher import run_self_check
            run_self_check(logger)
            fh.close()

            with open(os.path.join(tmpdir, "test.log"), "r", encoding="utf-8") as f:
                content = f.read()
                assert test_key not in content, "Self-check leaked API key in log!"
        finally:
            os.environ.pop("LOCALAPPDATA", None)
            os.environ.pop("AI_API_KEY", None)


def test_self_check_app_settings_table_creatable():
    """Self-check should verify app_settings table can be accessed."""
    from desktop_launcher import run_self_check
    from app.database import init_db, SessionLocal, Base
    from sqlalchemy import create_engine
    logger = _make_logger()

    # Use in-memory DB to verify table structure
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)

    # Verify app_settings table exists
    from app.models import AppSetting
    from sqlalchemy.orm import sessionmaker
    TestSession = sessionmaker(bind=engine)
    db = TestSession()
    try:
        # Table should exist and be queryable
        count = db.query(AppSetting).count()
        assert count == 0  # Empty table, no error
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
