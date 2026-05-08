"""
AI World Engine - Branch Service
Business logic for branch management.
"""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.models import Branch


class BranchService:
    """Service for branch operations."""

    @staticmethod
    def list_branches(db: Session, world_id: int) -> List[Branch]:
        """List all branches in a world."""
        return (
            db.query(Branch)
            .options(joinedload(Branch.simulation))
            .filter(Branch.world_id == world_id)
            .order_by(Branch.created_at.desc())
            .all()
        )

    @staticmethod
    def get_branch(db: Session, branch_id: int) -> Optional[Branch]:
        """Get a branch by ID with simulation loaded."""
        return (
            db.query(Branch)
            .options(joinedload(Branch.simulation))
            .filter(Branch.id == branch_id)
            .first()
        )
