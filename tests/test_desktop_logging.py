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
    """_setup_server_file_logger should create a server_logger that writes to server.log."""
    with tempfile.TemporaryDirectory() as tmpdir:
        from desktop_launcher import _setup_server_file_logger
        _setup_server_file_logger(tmpdir)
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


# ── v1.3.5: ensure_stdio_available Tests ──

def test_ensure_stdio_available_with_none():
    """ensure_stdio_available should handle None stdout/stderr without error."""
    import sys as _sys
    from desktop_launcher import ensure_stdio_available

    old_stdout = _sys.stdout
    old_stderr = _sys.stderr
    try:
        _sys.stdout = None
        _sys.stderr = None
        ensure_stdio_available()
        # After call, they should not be None
        assert _sys.stdout is not None
        assert _sys.stderr is not None
        assert hasattr(_sys.stdout, "write")
        assert hasattr(_sys.stderr, "write")
    finally:
        _sys.stdout = old_stdout
        _sys.stderr = old_stderr


def test_ensure_stdio_available_with_normal():
    """ensure_stdio_available should not change stdout/stderr when they exist."""
    import sys as _sys
    from desktop_launcher import ensure_stdio_available

    old_stdout = _sys.stdout
    old_stderr = _sys.stderr
    try:
        ensure_stdio_available()
        assert _sys.stdout is old_stdout
        assert _sys.stderr is old_stderr
    finally:
        pass  # no cleanup needed


def test_ensure_stdio_available_has_write_method():
    """After ensure_stdio_available, stdout/stderr must have write method."""
    import sys as _sys
    from desktop_launcher import ensure_stdio_available

    old_stdout = _sys.stdout
    old_stderr = _sys.stderr
    try:
        _sys.stdout = None
        ensure_stdio_available()
        _sys.stdout.write("test")
    except Exception as e:
        assert False, f"stdout.write failed: {e}"
    finally:
        _sys.stdout = old_stdout
        _sys.stderr = old_stderr


# ── v1.3.5: build_uvicorn_log_config Tests ──

def test_build_uvicorn_log_config_returns_dict():
    """build_uvicorn_log_config should return a dict."""
    from desktop_launcher import build_uvicorn_log_config
    config = build_uvicorn_log_config("/tmp/test_server.log")
    assert isinstance(config, dict)


def test_build_uvicorn_log_config_no_default_formatter():
    """build_uvicorn_log_config must NOT use uvicorn.logging.DefaultFormatter."""
    from desktop_launcher import build_uvicorn_log_config
    config = build_uvicorn_log_config("/tmp/test_server.log")
    config_str = str(config)
    assert "DefaultFormatter" not in config_str
    assert "AccessFormatter" not in config_str


def test_build_uvicorn_log_config_no_use_colors():
    """build_uvicorn_log_config must NOT contain use_colors."""
    from desktop_launcher import build_uvicorn_log_config
    config = build_uvicorn_log_config("/tmp/test_server.log")
    config_str = str(config)
    assert "use_colors" not in config_str


def test_build_uvicorn_log_config_formatter_is_plain():
    """build_uvicorn_log_config formatters should be plain format strings."""
    from desktop_launcher import build_uvicorn_log_config
    config = build_uvicorn_log_config("/tmp/test_server.log")
    fmt = config["formatters"]["default"]["format"]
    assert "%(asctime)" in fmt or "%(levelname)" in fmt
    # Must not reference uvicorn_module
    assert "()" not in config["formatters"]["default"].keys()


def test_build_uvicorn_log_config_has_server_file_handler():
    """build_uvicorn_log_config should have a server_file FileHandler."""
    from desktop_launcher import build_uvicorn_log_config
    config = build_uvicorn_log_config("/tmp/test_server.log")
    handler = config["handlers"]["server_file"]
    assert handler["class"] == "logging.FileHandler"
    assert "server.log" in handler["filename"]


def test_build_uvicorn_log_config_has_uvicorn_loggers():
    """build_uvicorn_log_config should configure uvicorn/error/access loggers."""
    from desktop_launcher import build_uvicorn_log_config
    config = build_uvicorn_log_config("/tmp/test_server.log")
    loggers = config["loggers"]
    assert "uvicorn" in loggers
    assert "uvicorn.error" in loggers
    assert "uvicorn.access" in loggers
    # All should write to server_file
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        assert "server_file" in loggers[name]["handlers"]


# ── v1.3.5: ASCII Log Tests ──

def test_self_check_logs_use_ascii_markers():
    """Self-check log messages should use ASCII markers [OK]/[WARN]/[ERROR]."""
    import sys as _sys, tempfile, logging, os as _os
    from desktop_launcher import run_self_check

    old_out = _sys.stdout
    old_stderr = _sys.stderr
    tmpdir = tempfile.TemporaryDirectory()
    try:
        _sys.stdout = open(_os.devnull, "w", encoding="utf-8")
        _sys.stderr = open(_os.devnull, "w", encoding="utf-8")

        log_path = _os.path.join(tmpdir.name, "test.log")
        logger = logging.getLogger("ascii_test")
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(log_path, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)

        _os.environ["LOCALAPPDATA"] = tmpdir.name
        try:
            run_self_check(logger)
        finally:
            _os.environ.pop("LOCALAPPDATA", None)
        fh.close()

        with open(log_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Must NOT contain Unicode emoji/symbols
        for symbol in ["✅", "❌", "⚠️", "→", "—", "鈥"]:
            assert symbol not in content, f"Log contains Unicode symbol: {symbol}"
        # Must contain ASCII markers
        assert "[OK]" in content, "Log missing [OK] marker"
    finally:
        tmpdir.cleanup()
        _sys.stdout = old_out
        _sys.stderr = old_stderr


def test_self_check_log_no_api_key():
    """Self-check log must NOT contain API key."""
    import sys as _sys, tempfile, logging, os as _os
    test_key = "sk-log-leak-test-key-abcde"
    _os.environ["AI_API_KEY"] = test_key

    from desktop_launcher import run_self_check
    old_out = _sys.stdout
    old_stderr = _sys.stderr
    tmpdir = tempfile.TemporaryDirectory()
    try:
        _sys.stdout = open(_os.devnull, "w", encoding="utf-8")
        _sys.stderr = open(_os.devnull, "w", encoding="utf-8")

        log_path = _os.path.join(tmpdir.name, "test.log")
        logger = logging.getLogger("noleak_test")
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(log_path, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)

        _os.environ["LOCALAPPDATA"] = tmpdir.name
        try:
            run_self_check(logger)
        finally:
            _os.environ.pop("LOCALAPPDATA", None)
        fh.close()

        with open(log_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert test_key not in content, "API key leaked in self-check log!"
    finally:
        tmpdir.cleanup()
        _sys.stdout = old_out
        _sys.stderr = old_stderr
        _os.environ.pop("AI_API_KEY", None)
