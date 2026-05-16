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
    """Auto-add missing columns to existing tables by comparing model metadata
    against actual database schema. Safe — no-op if columns already exist."""
    import sqlite3
    from app.config import settings as app_settings

    if "sqlite" not in app_settings.DATABASE_URL:
        return

    db_path = app_settings.DATABASE_URL.replace("sqlite:///", "")
    if db_path.startswith("./"):
        db_path = str(Path(__file__).parent.parent / db_path)

    # Use SQLAlchemy metadata to find all expected columns per table
    from app.models import (  # noqa: F401
        World, Character, Faction, Location, WorldRule,
        HistoricalEvent, SimulationRecord, Branch, AppSetting,
        StyleProfile, StyleSourceAnalysis, PlotAnchor, ContextPackage,
        SettingSuggestion,
        NovelVolumeOutline, NovelChapterOutline, NovelDraft,
        NovelDraftQualityReport, NovelDraftRevision, NovelFinalDraft,
    )
    from sqlalchemy import inspect as sa_inspect

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        for table in Base.metadata.sorted_tables:
            table_name = table.name
            expected_cols = {c.name: str(c.type) for c in table.columns}

            cursor.execute(f"PRAGMA table_info({table_name})")
            actual_cols = {row[1] for row in cursor.fetchall()}
            if not actual_cols:
                continue  # Table doesn't exist yet, create_all will handle

            for col_name, col_type in expected_cols.items():
                if col_name not in actual_cols:
                    # Map SQLAlchemy types to SQLite types
                    sql_type = _sa_type_to_sqlite(col_type)
                    cursor.execute(
                        f"ALTER TABLE {table_name} ADD COLUMN {col_name} {sql_type}"
                    )
                    print(f"  migrated: {table_name}.{col_name} added")

        conn.commit()
        conn.close()
    except sqlite3.OperationalError:
        pass


def _sa_type_to_sqlite(sa_type: str) -> str:
    """Convert SQLAlchemy type string to SQLite type."""
    upper = sa_type.upper()
    if "INTEGER" in upper or "BIGINT" in upper:
        return "INTEGER"
    if "BOOLEAN" in upper:
        return "BOOLEAN DEFAULT 0"
    if "FLOAT" in upper or "REAL" in upper or "DECIMAL" in upper:
        return "REAL"
    if "DATETIME" in upper or "TIMESTAMP" in upper or "DATE" in upper:
        return "TIMESTAMP"
    if "TEXT" in upper or "VARCHAR" in upper or "STRING" in upper or "CHAR" in upper:
        return "TEXT DEFAULT ''"
    return "TEXT DEFAULT ''"


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
        NovelContinuityReport,
        NovelVolumeExport,
    )
    Base.metadata.create_all(bind=engine)
    _migrate_schema()
