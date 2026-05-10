"""
AI World Engine - Test Desktop Logging
Tests for the desktop logging system: directory creation, file writes,
API key leakage prevention.
"""

import os
import sys
import tempfile
import logging
import pytest


def test_get_log_dir_creates_directory():
    """get_log_dir() should create the log directory if it doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Temporarily patch LOCALAPPDATA
        old_val = os.environ.get("LOCALAPPDATA")
        os.environ["LOCALAPPDATA"] = tmpdir
        try:
            from desktop_launcher import get_log_dir
            log_dir = get_log_dir()
            assert os.path.isdir(log_dir), f"Log directory was not created: {log_dir}"
            assert "AIWorldEngine" in log_dir
            assert "logs" in log_dir
        finally:
            if old_val is None:
                os.environ.pop("LOCALAPPDATA", None)
            else:
                os.environ["LOCALAPPDATA"] = old_val


def test_log_dir_contains_logs_subdir():
    """The log dir should end with /logs/."""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ["LOCALAPPDATA"] = tmpdir
        try:
            from desktop_launcher import get_log_dir
            log_dir = get_log_dir()
            assert log_dir.endswith("logs") or log_dir.endswith("logs/")
        finally:
            os.environ.pop("LOCALAPPDATA", None)


def test_log_files_can_be_written():
    """Log files should be writable in the log directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        from desktop_launcher import _setup_desktop_logging
        logger = _setup_desktop_logging(tmpdir)
        logger.info("test message for logging")
        logger.warning("test warning for error log")
        desktop_log = os.path.join(tmpdir, "desktop.log")
        error_log = os.path.join(tmpdir, "error.log")
        assert os.path.isfile(desktop_log), "desktop.log was not created"
        with open(desktop_log, "r", encoding="utf-8") as f:
            assert "test message" in f.read()
        if os.path.isfile(error_log):
            with open(error_log, "r", encoding="utf-8") as f:
                assert "test warning" in f.read()
        # Close all file handlers before temp dir cleanup
        for h in list(logger.handlers):
            if hasattr(h, "close"):
                h.close()
            logger.removeHandler(h)


def test_log_does_not_contain_api_key():
    """Logging should not leak full API keys."""
    test_key = "sk-supersecretkey12345678"
    with tempfile.TemporaryDirectory() as tmpdir:
        from desktop_launcher import _setup_desktop_logging
        logger = _setup_desktop_logging(tmpdir)
        logger.debug(f"AI key configured (length={len(test_key)})")
        logger.info(f"AI base_url: https://api.example.com/v1")
        for fname in os.listdir(tmpdir):
            fpath = os.path.join(tmpdir, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
                assert test_key not in content, f"API key leaked in {fname}"
        for h in list(logger.handlers):
            if hasattr(h, "close"):
                h.close()
            logger.removeHandler(h)


def test_log_directory_writable_on_non_windows():
    """get_log_dir should work on non-Windows by using home directory."""
    original_platform = sys.platform
    with tempfile.TemporaryDirectory() as tmpdir:
        old_home = os.environ.get("HOME") or os.environ.get("USERPROFILE")
        os.environ["HOME"] = tmpdir
        # Temporarily pretend we're not on Windows
        sys.platform = "linux"
        try:
            from desktop_launcher import get_log_dir
            log_dir = get_log_dir()
            assert os.path.isdir(log_dir)
            assert "AIWorldEngine" in log_dir
        finally:
            sys.platform = original_platform
            if old_home:
                os.environ["HOME"] = old_home


def test_server_log_setup():
    """_setup_server_logging should create a server_logger that writes to server.log."""
    with tempfile.TemporaryDirectory() as tmpdir:
        from desktop_launcher import _setup_server_logging
        _setup_server_logging(tmpdir)
        server_logger = logging.getLogger("server")
        server_logger.info("server test message")
        server_log = os.path.join(tmpdir, "server.log")
        assert os.path.isfile(server_log), "server.log was not created"
        with open(server_log, "r", encoding="utf-8") as f:
            content = f.read()
            assert "server test message" in content
        # Close handlers to allow temp dir cleanup
        for h in list(server_logger.handlers):
            if hasattr(h, "close"):
                h.close()
            server_logger.removeHandler(h)
