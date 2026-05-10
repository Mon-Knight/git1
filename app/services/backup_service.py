"""
AI World Engine - Backup Service
Database backup, restore, and listing.
Works in both source mode and PyInstaller desktop mode.
"""

import os
import shutil
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List
from sqlalchemy.orm import Session


def _get_database_path() -> Path:
    """Return the absolute path to the active SQLite database file."""
    from app.config import settings
    db_url = settings.DATABASE_URL
    # Extract path from sqlite:///...
    db_path_str = db_url[len("sqlite:///"):]
    # Special case: relative path './'
    if db_path_str.startswith("./"):
        db_path = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent / db_path_str[2:]
    else:
        db_path = Path(db_path_str.replace("\\", "/"))
    return db_path.resolve()


def _get_backup_dir() -> Path:
    """Return the backup directory, creating it if needed.
    Desktop mode: %LOCALAPPDATA%/AIWorldEngine/backups/
    Source mode: project_root/backups/
    """
    import sys
    if sys.platform == "win32":
        appdata = os.getenv("LOCALAPPDATA")
        if appdata:
            backup_dir = Path(appdata) / "AIWorldEngine" / "backups"
            os.makedirs(backup_dir, exist_ok=True)
            return backup_dir
    # Fallback: project root backups/
    project_root = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent
    backup_dir = project_root / "backups"
    os.makedirs(backup_dir, exist_ok=True)
    return backup_dir


def create_backup(db: Session = None, reason: str = "manual") -> Dict[str, Any]:
    """Create a backup of the current database. Returns metadata dict."""
    src = _get_database_path()
    dst_dir = _get_backup_dir()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    from app.config import settings

    db_name = f"AIWorldEngine-db-backup-v{settings.VERSION}-{timestamp}.db"
    dst_path = dst_dir / db_name

    # Copy database file
    shutil.copy2(src, dst_path)

    # Generate metadata
    metadata = {
        "backup_version": "1.0",
        "app_version": settings.VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "database_file": str(src),
        "database_size": src.stat().st_size,
        "backup_file": str(dst_path),
        "reason": reason,
        "backup_filename": db_name,
    }
    if db:
        from app.models import World, SimulationRecord, Branch
        metadata["world_count"] = db.query(World).count()
        metadata["simulation_record_count"] = db.query(SimulationRecord).count()
        metadata["branch_count"] = db.query(Branch).count()

    # Write metadata JSON
    meta_name = dst_path.stem + ".json"
    meta_path = dst_dir / meta_name
    import json
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    # Verify the backup
    with open(dst_path, "rb") as f:
        metadata["sha256"] = hashlib.sha256(f.read()).hexdigest()

    return metadata


def list_backups() -> List[Dict[str, Any]]:
    """List all backups with their metadata."""
    backup_dir = _get_backup_dir()
    if not backup_dir.exists():
        return []

    backups = []
    for f in sorted(backup_dir.glob("*.db"), reverse=True):
        meta_path = backup_dir / (f.stem + ".json")
        meta = {}
        if meta_path.exists():
            try:
                import json
                with open(meta_path, "r", encoding="utf-8") as mf:
                    meta = json.load(mf)
            except Exception:
                pass
        backups.append({
            "filename": f.name,
            "path": str(f),
            "size": f.stat().st_size,
            "created_at": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
            "metadata": meta,
        })
    return backups


def create_pre_restore_backup() -> Dict[str, Any]:
    """Create a safety backup before restoring."""
    return create_backup(reason="pre_restore")


def restore_backup(backup_filename: str) -> Dict[str, Any]:
    """Restore the database from a backup file.
    Creates a pre-restore backup first.
    Raises ValueError if backup is invalid.
    """
    backup_dir = _get_backup_dir()
    backup_path = backup_dir / backup_filename

    if not backup_path.exists():
        raise ValueError(f"备份文件不存在：{backup_filename}")

    if not backup_filename.endswith(".db"):
        raise ValueError(f"不是有效的数据库备份文件：{backup_filename}")

    if backup_path.stat().st_size == 0:
        raise ValueError(f"备份文件为空：{backup_filename}")

    # 1. Create pre-restore safety backup
    pre_backup = create_pre_restore_backup()

    # 2. Copy backup over current database
    src_db = _get_database_path()
    try:
        shutil.copy2(backup_path, src_db)
    except Exception as e:
        # Try to restore from pre-backup
        pre_backup_path = backup_dir / pre_backup["backup_filename"]
        if pre_backup_path.exists():
            try:
                shutil.copy2(pre_backup_path, src_db)
            except Exception:
                pass
        raise ValueError(f"数据库恢复失败：{e}。已尝试回退到恢复前备份。")

    return {
        "restored_from": backup_filename,
        "pre_restore_backup": pre_backup["backup_filename"],
        "database_path": str(src_db),
    }
