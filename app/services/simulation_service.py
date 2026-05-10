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

        Uses ModelRouter to select the appropriate AI client.
        If live AI fails, does NOT create an empty record — raises an exception.
        """
        from app.services.world_context_service import WorldContextService
        from app.services.ai.model_router import ModelRouter
        from app.services.ai.prompt_builder import PromptBuilder
        from app.services.settings_service import SettingsService

        if context is None:
            context = WorldContextService.build_world_context(db, world_id)

        context_snapshot = WorldContextService.build_context_snapshot(context)

        # Get the AI client for simulation task
        client = ModelRouter.get_client(db, "simulation")
        messages = PromptBuilder.build_simulation_prompt(context, question)
        config = SettingsService.get_effective_config(db)
        options = {
            "temperature": config.get("ai_temperature", 0.7),
            "max_tokens": config.get("ai_max_tokens", 2000),
            "timeout": config.get("ai_timeout", 60),
        }
        result = client.generate(messages, options)

        if not result.get("success"):
            error = result.get("error", {})
            raise RuntimeError(error.get("message", "AI 调用失败，请检查 AI 设置配置。"))

        ai_response = result["content"]
        ai_model = result.get("model", "mock")
        is_mock = result.get("provider") == "mock"

        # Create record
        record = SimulationService.create_simulation_record(
            db=db,
            world_id=world_id,
            question=question,
            simulation_type=simulation_type,
            context_snapshot=context_snapshot,
            ai_response=ai_response,
            ai_model=ai_model,
            is_mock=is_mock,
        )

        return record
