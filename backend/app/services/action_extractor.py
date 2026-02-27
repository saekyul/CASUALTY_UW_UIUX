"""
Action Extractor Service - Extract action items from emails and data
"""
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.database import ActionItem
from app.services.llm_service import get_llm_service

logger = logging.getLogger(__name__)


class ActionExtractorService:
    """Service for extracting action items"""

    def __init__(self):
        self.llm_service = get_llm_service()

    async def extract_from_email(
        self,
        email_id: int,
        email_body: str,
        db: Session,
        model: str = None,
    ) -> list[ActionItem]:
        """
        Extract action items from email

        Args:
            email_id: ID of email
            email_body: Email body text
            db: Database session
            model: LLM model to use

        Returns:
            List of ActionItem objects
        """
        try:
            # Extract actions using LLM
            actions, model_used, tokens_used = await self.llm_service.extract_actions(
                email_body, model=model
            )

            # Save to database
            action_items = []
            for action in actions:
                try:
                    action_item = ActionItem(
                        email_id=email_id,
                        action_text=action.get("action", ""),
                        priority=action.get("priority", "medium").lower(),
                        deadline=None,  # Could be parsed from action deadline if provided
                        llm_model=model_used,
                    )
                    db.add(action_item)
                    action_items.append(action_item)
                except Exception as e:
                    logger.error(f"Error creating action item: {e}")
                    continue

            db.commit()
            logger.info(f"Extracted {len(action_items)} action items from email {email_id}")
            return action_items

        except Exception as e:
            db.rollback()
            logger.error(f"Error extracting actions from email: {e}")
            raise

    async def extract_batch(
        self,
        emails: list[tuple[int, str]],
        db: Session,
        model: str = None,
    ) -> list[ActionItem]:
        """
        Extract action items from multiple emails

        Args:
            emails: List of (email_id, email_body) tuples
            db: Database session
            model: LLM model to use

        Returns:
            List of ActionItem objects
        """
        all_actions = []

        for email_id, email_body in emails:
            try:
                actions = await self.extract_from_email(
                    email_id, email_body, db, model=model
                )
                all_actions.extend(actions)
            except Exception as e:
                logger.error(f"Failed to extract actions from email {email_id}: {e}")
                continue

        return all_actions

    def get_actions_for_email(self, email_id: int, db: Session) -> list[ActionItem]:
        """Get all action items for email"""
        return db.query(ActionItem).filter(ActionItem.email_id == email_id).all()

    def get_pending_actions(
        self,
        email_id: int = None,
        db: Session = None,
    ) -> list[ActionItem]:
        """
        Get pending action items

        Args:
            email_id: Optional email ID to filter by
            db: Database session

        Returns:
            List of pending ActionItem objects
        """
        query = db.query(ActionItem).filter(ActionItem.is_completed == False)

        if email_id:
            query = query.filter(ActionItem.email_id == email_id)

        return query.all()

    def mark_action_complete(
        self,
        action_id: int,
        db: Session,
    ) -> ActionItem:
        """
        Mark action item as complete

        Args:
            action_id: ID of action item
            db: Database session

        Returns:
            Updated ActionItem object
        """
        try:
            action = db.query(ActionItem).filter(ActionItem.id == action_id).first()
            if action:
                action.is_completed = True
                action.completed_at = datetime.utcnow()
                db.commit()
                db.refresh(action)
                logger.info(f"Action {action_id} marked as complete")
                return action
            return None
        except Exception as e:
            db.rollback()
            logger.error(f"Error marking action as complete: {e}")
            raise

    def delete_action(self, action_id: int, db: Session) -> bool:
        """Delete action item"""
        try:
            action = db.query(ActionItem).filter(ActionItem.id == action_id).first()
            if action:
                db.delete(action)
                db.commit()
                logger.info(f"Action {action_id} deleted")
                return True
            return False
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting action: {e}")
            raise

    def get_high_priority_actions(self, db: Session) -> list[ActionItem]:
        """Get high priority pending actions"""
        return (
            db.query(ActionItem)
            .filter(
                ActionItem.priority == "high",
                ActionItem.is_completed == False,
            )
            .order_by(ActionItem.deadline.asc())
            .all()
        )


# Singleton instance
_action_extractor_service = None


def get_action_extractor_service() -> ActionExtractorService:
    """Get or create action extractor service instance"""
    global _action_extractor_service
    if _action_extractor_service is None:
        _action_extractor_service = ActionExtractorService()
    return _action_extractor_service
