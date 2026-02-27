"""
Email Responder Service - Generate and manage auto-responses
"""
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.database import AutoResponse, Email
from app.services.llm_service import get_llm_service
from app.services.outlook_service import get_outlook_service

logger = logging.getLogger(__name__)


class EmailResponderService:
    """Service for generating and sending email responses"""

    def __init__(self):
        self.llm_service = get_llm_service()
        self.outlook_service = get_outlook_service()

    async def generate_response_suggestion(
        self,
        email_id: int,
        email_subject: str,
        email_body: str,
        db: Session,
        model: str = None,
    ) -> AutoResponse:
        """
        Generate response suggestion for email

        Args:
            email_id: ID of email to respond to
            email_subject: Email subject
            email_body: Email body
            db: Database session
            model: LLM model to use

        Returns:
            AutoResponse object with suggested response
        """
        try:
            # Check if response suggestion already exists
            existing_response = (
                db.query(AutoResponse)
                .filter(AutoResponse.email_id == email_id)
                .first()
            )
            if existing_response:
                logger.info(f"Response suggestion already exists for email {email_id}")
                return existing_response

            # Generate response using LLM
            suggested_response, model_used, tokens_used = await self.llm_service.generate_response(
                email_subject, email_body, model=model
            )

            # Store in database
            auto_response = AutoResponse(
                email_id=email_id,
                suggested_response=suggested_response,
                llm_model=model_used,
            )

            db.add(auto_response)
            db.commit()
            db.refresh(auto_response)

            logger.info(f"Response suggestion generated for email {email_id} using {model_used}")
            return auto_response

        except IntegrityError as e:
            db.rollback()
            logger.error(f"Database integrity error: {e}")
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error generating response suggestion: {e}")
            raise

    async def approve_and_send_response(
        self,
        email_id: int,
        response_text: str,
        db: Session,
    ) -> bool:
        """
        Approve and send response to email

        Args:
            email_id: ID of email to respond to
            response_text: Response text to send
            db: Database session

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get email from database
            email = db.query(Email).filter(Email.id == email_id).first()
            if not email or not email.outlook_id:
                logger.error(f"Email {email_id} not found or has no outlook_id")
                return False

            # Send response via Outlook
            success = await self.outlook_service.send_reply(
                email.outlook_id, response_text
            )

            if success:
                # Update auto_response record
                auto_response = (
                    db.query(AutoResponse)
                    .filter(AutoResponse.email_id == email_id)
                    .first()
                )

                if auto_response:
                    auto_response.final_response = response_text
                    auto_response.is_sent = True
                    from datetime import datetime
                    auto_response.sent_at = datetime.utcnow()
                    db.commit()
                    logger.info(f"Response sent for email {email_id}")
                else:
                    # Create new auto_response record
                    from datetime import datetime
                    auto_response = AutoResponse(
                        email_id=email_id,
                        suggested_response=response_text,
                        final_response=response_text,
                        is_sent=True,
                        llm_model="manual",
                        sent_at=datetime.utcnow(),
                    )
                    db.add(auto_response)
                    db.commit()
                    logger.info(f"Manual response sent for email {email_id}")

                return True
            else:
                logger.error(f"Failed to send response for email {email_id}")
                return False

        except Exception as e:
            db.rollback()
            logger.error(f"Error sending response: {e}")
            return False

    def get_response_suggestion(self, email_id: int, db: Session) -> AutoResponse:
        """Get response suggestion for email"""
        return (
            db.query(AutoResponse)
            .filter(AutoResponse.email_id == email_id)
            .first()
        )

    def get_unsent_suggestions(self, db: Session) -> list[AutoResponse]:
        """Get all unsent response suggestions"""
        return (
            db.query(AutoResponse)
            .filter(AutoResponse.is_sent == False)
            .all()
        )

    def reject_response_suggestion(self, email_id: int, db: Session) -> bool:
        """Reject/delete response suggestion"""
        try:
            auto_response = (
                db.query(AutoResponse)
                .filter(AutoResponse.email_id == email_id)
                .first()
            )
            if auto_response and not auto_response.is_sent:
                db.delete(auto_response)
                db.commit()
                logger.info(f"Response suggestion rejected for email {email_id}")
                return True
            return False
        except Exception as e:
            db.rollback()
            logger.error(f"Error rejecting response suggestion: {e}")
            raise

    async def generate_batch_suggestions(
        self,
        emails: list[tuple[int, str, str]],
        db: Session,
        model: str = None,
    ) -> list[AutoResponse]:
        """
        Generate response suggestions for multiple emails

        Args:
            emails: List of (email_id, subject, body) tuples
            db: Database session
            model: LLM model to use

        Returns:
            List of AutoResponse objects
        """
        responses = []

        for email_id, subject, body in emails:
            try:
                response = await self.generate_response_suggestion(
                    email_id, subject, body, db, model=model
                )
                responses.append(response)
            except Exception as e:
                logger.error(f"Failed to generate response for email {email_id}: {e}")
                continue

        return responses


# Singleton instance
_email_responder_service = None


def get_email_responder_service() -> EmailResponderService:
    """Get or create email responder service instance"""
    global _email_responder_service
    if _email_responder_service is None:
        _email_responder_service = EmailResponderService()
    return _email_responder_service
