"""
AI World Engine - Test Export File Service
Tests for ExportFileService: filenames, payloads, security, validation.
"""

import os
import json
import tempfile
from app.services.export_file_service import ExportFileService


class TestBuildExportFilename:
    def test_basic_world_export(self):
        name = ExportFileService.build_export_filename("world", "测试世界")
        assert name.startswith("AIWorldEngine_world_")
        assert name.endswith(".json")

    def test_no_world_name(self):
        name = ExportFileService.build_export_filename("backup")
        assert name.startswith("AIWorldEngine_backup_")
        assert ".json" in name

    def test_sanitize_illegal_chars(self):
        name = ExportFileService.build_export_filename("world", 'test<>:"/\\|?*world')
        assert '<' not in name
        assert '>' not in name
        assert ':' not in name

    def test_truncate_long_name(self):
        long_name = "A" * 100
        name = ExportFileService.build_export_filename("world", long_name)
        assert len(name) < 120

    def test_default_ext_json(self):
        name = ExportFileService.build_export_filename("test")
        assert name.endswith(".json")


class TestWriteExportFile:
    def test_write_valid_json(self):
        path = os.path.join(tempfile.gettempdir(), "aiwe_test_export.json")
        try:
            result = ExportFileService.write_export_file(path, {"test": "data"})
            assert result["ok"]
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            assert data["test"] == "data"
        finally:
            if os.path.exists(path):
                os.unlink(path)


class TestValidateDesktopPath:
    def test_empty_path_rejected(self):
        result = ExportFileService.validate_desktop_export_path("")
        assert not result["ok"]

    def test_valid_path_accepted(self):
        path = os.path.join(tempfile.gettempdir(), "test_export.json")
        result = ExportFileService.validate_desktop_export_path(path)
        assert result["ok"]


class TestSanitizePayload:
    def test_removes_api_key(self):
        payload = {"data": "hello", "api_key": "secret123"}
        cleaned = ExportFileService.sanitize_payload_for_export(payload)
        assert "api_key" not in cleaned
        assert cleaned["data"] == "hello"

    def test_removes_password(self):
        payload = {"user": "admin", "password": "12345"}
        cleaned = ExportFileService.sanitize_payload_for_export(payload)
        assert "password" not in cleaned

    def test_keeps_safe_fields(self):
        payload = {"name": "test", "version": "1.0"}
        cleaned = ExportFileService.sanitize_payload_for_export(payload)
        assert cleaned["name"] == "test"
