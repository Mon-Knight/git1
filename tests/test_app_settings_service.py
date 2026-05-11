"""
Tests for v1.7.11.3: App Settings Service.
"""
import pytest
from app.database import SessionLocal, Base, engine
from app.services.app_settings_service import AppSettingsService


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    # Clean any pre-existing settings from other tests
    from app.models import AppSetting
    session.query(AppSetting).delete()
    session.commit()
    yield session
    session.close()


class TestAppSettingsService:
    def test_default_values(self, db):
        assert AppSettingsService.get(db, "ui_sidebar_default_expanded") == "true"
        assert AppSettingsService.get(db, "ui_compact_mode") == "false"
        assert AppSettingsService.get(db, "desktop_default_width") == "1280"
        assert AppSettingsService.get(db, "desktop_default_height") == "820"

    def test_missing_key_returns_default(self, db):
        assert AppSettingsService.get(db, "nonexistent_key", "fallback") == "fallback"

    def test_set_and_get(self, db):
        AppSettingsService.set(db, "ui_compact_mode", "true")
        assert AppSettingsService.get(db, "ui_compact_mode") == "true"

    def test_update_existing(self, db):
        AppSettingsService.set(db, "ui_sidebar_default_expanded", "false")
        assert AppSettingsService.get(db, "ui_sidebar_default_expanded") == "false"
        AppSettingsService.set(db, "ui_sidebar_default_expanded", "true")
        assert AppSettingsService.get(db, "ui_sidebar_default_expanded") == "true"

    def test_window_size_valid(self, db):
        AppSettingsService.set(db, "desktop_default_width", "1400")
        AppSettingsService.set(db, "desktop_default_height", "900")
        assert AppSettingsService.get(db, "desktop_default_width") == "1400"
        assert AppSettingsService.get(db, "desktop_default_height") == "900"

    def test_window_size_too_small_rejected(self, db):
        with pytest.raises(ValueError):
            AppSettingsService.set(db, "desktop_default_width", "500")

    def test_window_size_too_large_rejected(self, db):
        with pytest.raises(ValueError):
            AppSettingsService.set(db, "desktop_default_height", "3000")

    def test_get_all_returns_dict(self, db):
        result = AppSettingsService.get_all(db)
        assert isinstance(result, dict)
        assert "ui_sidebar_default_expanded" in result
        assert "desktop_default_width" in result

    def test_is_desktop_mode_returns_bool(self):
        result = AppSettingsService.is_desktop_mode()
        assert isinstance(result, bool)

    def test_get_window_size_returns_tuple(self):
        size = AppSettingsService.get_window_size()
        assert isinstance(size, tuple)
        assert len(size) == 2
        assert 1024 <= size[0] <= 2560
        assert 700 <= size[1] <= 1600
