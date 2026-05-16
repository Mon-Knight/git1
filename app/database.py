"""
AI World Engine - Database Setup
SQLAlchemy engine and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from pathlib import Path

from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.APP_DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


def get_db():
    """Dependency that provides a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _migrate_schema():
    """Add missing columns to existing tables (safe, no-op if columns exist)."""
    import sqlite3
    from app.config import settings as app_settings

    if "sqlite" not in app_settings.DATABASE_URL:
        return

    # Extract database path from URL
    db_path = app_settings.DATABASE_URL.replace("sqlite:///", "")
    if db_path.startswith("./"):
        db_path = str(Path(__file__).parent.parent / db_path)

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # ── setting_suggestions ──
        cursor.execute("PRAGMA table_info(setting_suggestions)")
        cols = {row[1] for row in cursor.fetchall()}
        if cols:
            for col_name, col_def in [
                ("adopted_target_id", "INTEGER"),
                ("adopted_target_type", "VARCHAR(20)"),
                ("adopted_at", "TIMESTAMP"),
            ]:
                if col_name not in cols:
                    cursor.execute(f"ALTER TABLE setting_suggestions ADD COLUMN {col_name} {col_def}")
                    print(f"  migrated: setting_suggestions.{col_name} added")

        conn.commit()
        conn.close()
    except sqlite3.OperationalError:
        pass  # Table doesn't exist yet, Base.metadata.create_all will handle it


def init_db():
    """Create all tables and migrate missing columns in the database."""
    from app.models import (  # noqa: F401 - import to register models
        World,
        Character,
        Faction,
        Location,
        WorldRule,
        HistoricalEvent,
        SimulationRecord,
        Branch,
        AppSetting,
        StyleProfile,
        StyleSourceAnalysis,
        PlotAnchor,
        ContextPackage,
        SettingSuggestion,
        NovelVolumeOutline,
        NovelChapterOutline,
        NovelDraft,
        NovelDraftQualityReport,
        NovelDraftRevision,
        NovelFinalDraft,
    )
    Base.metadata.create_all(bind=engine)
    _migrate_schema()
