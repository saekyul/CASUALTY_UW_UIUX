"""
Summarizer Service - Text summarization using LLM
"""
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.database import Summary, Email
from app.services.llm_service import get_llm_service

logger = logging.getLogger(__name__)


class SummarizerService:
    """Service for text summarization"""

    def __init__(self):
        self.llm_service = get_llm_service()

    async def summarize_email(
        self,
        email_id: int,
        email_body: str,
        db: Session,
        model: str = None,
        language: str = "korean",
    ) -> Summary:
        """
        Summarize email and store in database

        Args:
            email_id: ID of email to summarize
            email_body: Email body text
            db: Database session
            model: LLM model to use
            language: Language for summary

        Returns:
            Summary object
        """
        try:
            # Check if summary already exists
            existing_summary = (
                db.query(Summary).filter(Summary.email_id == email_id).first()
            )
            if existing_summary:
                logger.info(f"Summary already exists for email {email_id}")
                return existing_summary

            # Generate summary
            summary_text, model_used, tokens_used = await self.llm_service.summarize_text(
                email_body, model=model, language=language
            )

            # Store in database
            summary = Summary(
                email_id=email_id,
                summary_text=summary_text,
                llm_model=model_used,
                tokens_used=tokens_used,
            )

            db.add(summary)
            db.commit()
            db.refresh(summary)

            logger.info(f"Summary created for email {email_id} using {model_used}")
            return summary

        except IntegrityError as e:
            db.rollback()
            logger.error(f"Database integrity error: {e}")
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error summarizing email: {e}")
            raise

    async def summarize_batch(
        self,
        emails: list[tuple[int, str]],
        db: Session,
        model: str = None,
        language: str = "korean",
    ) -> list[Summary]:
        """
        Summarize multiple emails

        Args:
            emails: List of (email_id, email_body) tuples
            db: Database session
            model: LLM model to use
            language: Language for summary

        Returns:
            List of Summary objects
        """
        summaries = []

        for email_id, email_body in emails:
            try:
                summary = await self.summarize_email(
                    email_id, email_body, db, model=model, language=language
                )
                summaries.append(summary)
            except Exception as e:
                logger.error(f"Failed to summarize email {email_id}: {e}")
                continue

        return summaries

    def get_summary(self, email_id: int, db: Session) -> Summary:
        """Get summary for email"""
        return db.query(Summary).filter(Summary.email_id == email_id).first()

    def delete_summary(self, email_id: int, db: Session) -> bool:
        """Delete summary for email"""
        try:
            summary = db.query(Summary).filter(Summary.email_id == email_id).first()
            if summary:
                db.delete(summary)
                db.commit()
                logger.info(f"Summary deleted for email {email_id}")
                return True
            return False
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting summary: {e}")
            raise


# Singleton instance
_summarizer_service = None


def get_summarizer_service() -> SummarizerService:
    """Get or create summarizer service instance"""
    global _summarizer_service
    if _summarizer_service is None:
        _summarizer_service = SummarizerService()
    return _summarizer_service
