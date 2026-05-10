"""
AI World Engine - Test Export / Import / Backup Services
"""

import os, json, tempfile, pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base


_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
_Session = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


@pytest.fixture()
def db():
    Base.metadata.create_all(bind=_engine)
    session = _Session()
    yield session
    session.rollback()
    session.close()
    Base.metadata.drop_all(bind=_engine)


# ── Export Service Tests ──

def test_export_world_to_dict(db):
    from app.models import World
    from app.services.export_service import export_world_to_dict
    w = World(name="Test Export World")
    db.add(w); db.commit()
    payload = export_world_to_dict(db, w.id)
    assert payload["export_type"] == "single_world"
    assert payload["data"]["world"]["name"] == "Test Export World"
    assert "characters" in payload["data"]


def test_export_nonexistent_world(db):
    from app.services.export_service import export_world_to_dict
    with pytest.raises(ValueError):
        export_world_to_dict(db, 999)


def test_export_includes_characters(db):
    from app.models import World, Character
    from app.services.export_service import export_world_to_dict
    w = World(name="W"); db.add(w); db.commit()
    c = Character(name="Hero", world_id=w.id)
    db.add(c); db.commit()
    payload = export_world_to_dict(db, w.id)
    assert payload["metadata"]["counts"]["characters"] == 1


def test_export_includes_novel_evolution(db):
    from app.models import World, SimulationRecord
    from app.services.export_service import export_world_to_dict
    w = World(name="W"); db.add(w); db.commit()
    r = SimulationRecord(world_id=w.id, question="test", simulation_type="novel_evolution")
    db.add(r); db.commit()
    payload = export_world_to_dict(db, w.id)
    assert payload["metadata"]["contains_novel_evolution"] is True


def test_export_no_app_settings(db):
    from app.models import World, AppSetting
    from app.services.export_service import export_world_to_dict
    w = World(name="W"); db.add(w); db.commit()
    s = AppSetting(key="test", value="secret")
    db.add(s); db.commit()
    payload = export_world_to_dict(db, w.id)
    json_str = json.dumps(payload)
    assert "app_settings" not in json_str
    assert "secret" not in json_str


def test_sanitize_filename():
    from app.services.export_service import sanitize_filename
    assert sanitize_filename("test:world<>") == "test_world__"


def test_export_json_serializable(db):
    from app.models import World
    from app.services.export_service import export_world_to_dict
    w = World(name="W"); db.add(w); db.commit()
    payload = export_world_to_dict(db, w.id)
    s = json.dumps(payload, ensure_ascii=False, indent=2)
    assert len(s) > 50


# ── Import Service Tests ──

def test_import_creates_new_world(db):
    from app.models import World
    from app.services.import_service import import_world_from_payload
    payload = {"export_type": "single_world", "export_version": "1.0", "data": {"world": {"name": "Imported"}}}
    result = import_world_from_payload(db, payload)
    assert " - 导入副本" in result["new_world_name"]


def test_import_rejects_invalid_type(db):
    from app.services.import_service import import_world_from_payload
    payload = {"export_type": "invalid", "export_version": "1.0", "data": {"world": {"name": "X"}}}
    with pytest.raises(ValueError):
        import_world_from_payload(db, payload)


def test_import_rejects_bad_version(db):
    from app.services.import_service import import_world_from_payload
    payload = {"export_type": "single_world", "export_version": "99.0", "data": {"world": {"name": "X"}}}
    with pytest.raises(ValueError):
        import_world_from_payload(db, payload)


def test_import_rejects_missing_world(db):
    from app.services.import_service import import_world_from_payload
    payload = {"export_type": "single_world", "export_version": "1.0", "data": {}}
    with pytest.raises(ValueError):
        import_world_from_payload(db, payload)


def test_import_preserves_sim_type(db):
    from app.models import SimulationRecord
    from app.services.import_service import import_world_from_payload
    payload = {
        "export_type": "single_world", "export_version": "1.0",
        "data": {
            "world": {"name": "Test"},
            "simulation_records": [{"question": "q", "simulation_type": "novel_evolution", "world_id": 1}],
        }
    }
    result = import_world_from_payload(db, payload)
    assert result["contains_novel_evolution"] is True


def test_import_rollback_on_error(db):
    from app.services.import_service import import_world_from_payload
    initial = db.query(__import__("app.models", fromlist=["World"]).World).count()
    try:
        import_world_from_payload(db, {"export_type": "invalid"})
    except ValueError:
        pass
    db.rollback()
    final = db.query(__import__("app.models", fromlist=["World"]).World).count()
    assert final == initial


# ── Backup Service Tests ──

def test_backup_creates_file(db):
    from app.services.backup_service import create_backup, _get_backup_dir
    meta = create_backup(db=db)
    assert os.path.isfile(os.path.join(_get_backup_dir(), meta["backup_filename"]))


def test_backup_metadata_no_api_key(db):
    from app.services.backup_service import create_backup
    meta = create_backup(db=db)
    meta_str = json.dumps(meta)
    assert "sk-" not in meta_str
    assert "api_key" not in meta_str.lower()


def test_list_backups(db):
    from app.services.backup_service import create_backup, list_backups
    create_backup(db=db)
    backups = list_backups()
    assert len(backups) >= 1


def test_restore_rejects_nonexistent():
    from app.services.backup_service import restore_backup
    with pytest.raises(ValueError):
        restore_backup("nonexistent.db")


def test_restore_rejects_non_db():
    from app.services.backup_service import restore_backup
    with pytest.raises(ValueError):
        restore_backup("file.txt")


def test_sanitize_filename_unicode():
    from app.services.export_service import sanitize_filename
    name = sanitize_filename("测试:世界")
    assert ":" not in name
