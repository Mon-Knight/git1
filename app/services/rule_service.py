"""
AI World Engine - World Rule Service
Business logic for world rule CRUD operations.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.models import WorldRule


class RuleService:
    """Service for world rule management operations."""

    @staticmethod
    def create_rule(
        db: Session,
        world_id: int,
        name: str,
        rule_type: str = "",
        content: str = "",
        constraints: str = "",
        scope: str = "",
    ) -> WorldRule:
        """Create a new rule in a world."""
        rule = WorldRule(
            world_id=world_id,
            name=name,
            rule_type=rule_type,
            content=content,
            constraints=constraints,
            scope=scope,
        )
        db.add(rule)
        db.commit()
        db.refresh(rule)
        return rule

    @staticmethod
    def list_rules(db: Session, world_id: int) -> List[WorldRule]:
        """List all rules in a world."""
        return (
            db.query(WorldRule)
            .filter(WorldRule.world_id == world_id)
            .order_by(WorldRule.created_at.desc())
            .all()
        )

    @staticmethod
    def get_rule(db: Session, rule_id: int) -> Optional[WorldRule]:
        """Get a rule by ID."""
        return db.query(WorldRule).filter(WorldRule.id == rule_id).first()

    @staticmethod
    def update_rule(
        db: Session,
        rule_id: int,
        name: str,
        rule_type: str = "",
        content: str = "",
        constraints: str = "",
        scope: str = "",
    ) -> Optional[WorldRule]:
        """Update a rule. Returns None if not found."""
        rule = db.query(WorldRule).filter(WorldRule.id == rule_id).first()
        if not rule:
            return None

        rule.name = name
        rule.rule_type = rule_type
        rule.content = content
        rule.constraints = constraints
        rule.scope = scope

        db.commit()
        db.refresh(rule)
        return rule

    @staticmethod
    def delete_rule(db: Session, rule_id: int) -> bool:
        """Delete a rule. Returns True if deleted, False if not found."""
        rule = db.query(WorldRule).filter(WorldRule.id == rule_id).first()
        if not rule:
            return False
        db.delete(rule)
        db.commit()
        return True
