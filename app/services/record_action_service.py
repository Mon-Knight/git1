"""
AI World Engine - Record Action Service
Handles adoption as canon and saving as branch from simulation records.
"""

from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.models import SimulationRecord, HistoricalEvent, Branch


class RecordActionService:
    """Service for actions on simulation records (adopt/branch)."""

    @staticmethod
    def ensure_record_pending(record: Optional[SimulationRecord]) -> Tuple[bool, str]:
        """
        Check if a record exists and is in 'pending' status.
        Returns (is_valid, error_message).
        """
        if not record:
            return False, "推演记录不存在"
        if record.status != "pending":
            return False, f"推演记录状态为 {record.status}，不允许操作"
        return True, ""

    @staticmethod
    def ensure_record_belongs_to_world(record: SimulationRecord, world_id: int) -> Tuple[bool, str]:
        """
        Check if a record belongs to the specified world.
        Returns (is_valid, error_message).
        """
        if record.world_id != world_id:
            return False, "推演记录不属于当前世界"
        return True, ""

    @staticmethod
    def adopt_record_as_canon(
        db: Session,
        record_id: int,
        world_id: int,
    ) -> Tuple[Optional[HistoricalEvent], Optional[str]]:
        """
        Adopt a simulation record as a canon historical event.

        Returns (event, error_message). error_message is None on success.
        """
        record = db.query(SimulationRecord).filter(SimulationRecord.id == record_id).first()

        # Validate
        valid, err = RecordActionService.ensure_record_pending(record)
        if not valid:
            return None, err

        valid, err = RecordActionService.ensure_record_belongs_to_world(record, world_id)
        if not valid:
            return None, err

        # Create historical event from simulation record
        title = record.question[:50] if record.question else "AI推演采纳"
        event = HistoricalEvent(
            world_id=world_id,
            title=f"AI推演采纳：{title}",
            event_time="",
            content=record.ai_response or "",
            consequences="由 AI 推演记录采纳生成",
            is_canon=True,
            source_type="simulation",
            source_id=record.id,
        )
        db.add(event)

        # Update record status
        record.status = "adopted"

        db.commit()
        db.refresh(event)

        return event, None

    @staticmethod
    def save_record_as_branch(
        db: Session,
        record_id: int,
        world_id: int,
        branch_name: str = "",
    ) -> Tuple[Optional[Branch], Optional[str]]:
        """
        Save a simulation record as a branch.

        Returns (branch, error_message). error_message is None on success.
        """
        record = db.query(SimulationRecord).filter(SimulationRecord.id == record_id).first()

        # Validate
        valid, err = RecordActionService.ensure_record_pending(record)
        if not valid:
            return None, err

        valid, err = RecordActionService.ensure_record_belongs_to_world(record, world_id)
        if not valid:
            return None, err

        # Generate branch name if not provided
        if not branch_name:
            question_preview = record.question[:30] if record.question else "未命名"
            branch_name = f"分支：{question_preview}"

        # Create branch
        import json
        events_data = json.dumps({
            "question": record.question,
            "simulation_type": record.simulation_type,
            "ai_response": record.ai_response,
        }, ensure_ascii=False)

        branch = Branch(
            world_id=world_id,
            simulation_id=record.id,
            branch_name=branch_name,
            description=f"来源：推演记录 #{record.id}",
            events_json=events_data,
        )
        db.add(branch)

        # Update record status
        record.status = "branched"

        db.commit()
        db.refresh(branch)

        return branch, None
