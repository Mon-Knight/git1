"""
AI World Engine - Simulation Service
Business logic for AI simulation and record management.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.models import SimulationRecord
from app.config import settings


class SimulationService:
    """Service for simulation operations."""

    @staticmethod
    def create_simulation_record(
        db: Session,
        world_id: int,
        question: str,
        simulation_type: str = "",
        context_snapshot: str = "",
        ai_response: str = "",
        ai_model: str = "",
        is_mock: bool = True,
    ) -> SimulationRecord:
        """Create a new simulation record with status 'pending'."""
        record = SimulationRecord(
            world_id=world_id,
            question=question,
            simulation_type=simulation_type,
            context_snapshot=context_snapshot,
            ai_response=ai_response,
            status="pending",
            ai_model=ai_model,
            is_mock=is_mock,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def list_simulation_records(db: Session, world_id: int) -> List[SimulationRecord]:
        """List all simulation records for a world."""
        return (
            db.query(SimulationRecord)
            .filter(SimulationRecord.world_id == world_id)
            .order_by(SimulationRecord.created_at.desc())
            .all()
        )

    @staticmethod
    def get_simulation_record(db: Session, record_id: int) -> Optional[SimulationRecord]:
        """Get a simulation record by ID."""
        return (
            db.query(SimulationRecord)
            .filter(SimulationRecord.id == record_id)
            .first()
        )

    @staticmethod
    def run_simulation(
        db: Session,
        world_id: int,
        question: str,
        simulation_type: str = "",
        context: dict = None,
    ) -> SimulationRecord:
        """
        Run an AI simulation and save the result.

        Args:
            db: Database session
            world_id: World ID
            question: User's simulation question
            simulation_type: Type of simulation
            context: World context dict from WorldContextService

        Returns:
            A SimulationRecord with status 'pending'
        """
        from app.services.world_context_service import WorldContextService
        from app.services.ai_service import ai_service

        if context is None:
            context = WorldContextService.build_world_context(db, world_id)

        context_snapshot = WorldContextService.build_context_snapshot(context)

        # Generate AI response
        ai_response = ai_service.generate_simulation(context, question)

        # Create record
        record = SimulationService.create_simulation_record(
            db=db,
            world_id=world_id,
            question=question,
            simulation_type=simulation_type,
            context_snapshot=context_snapshot,
            ai_response=ai_response,
            ai_model=settings.AI_MODEL if not settings.is_mock_ai else "mock",
            is_mock=settings.is_mock_ai,
        )

        return record
