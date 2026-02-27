"""
Email API Routes
"""
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schemas import EmailResponse, EmailDetailResponse, SummaryResponse
from app.models.database import Email, Summary
from app.services.outlook_service import get_outlook_service
from app.services.summarizer import get_summarizer_service
from app.services.action_extractor import get_action_extractor_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/emails", tags=["emails"])


@router.get("", response_model=List[EmailResponse])
async def get_emails(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get list of emails"""
    try:
        emails = db.query(Email).offset(skip).limit(limit).all()
        return emails
    except Exception as e:
        logger.error(f"Error fetching emails: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch emails")


@router.get("/{email_id}", response_model=EmailDetailResponse)
async def get_email_detail(
    email_id: int,
    db: Session = Depends(get_db),
):
    """Get detailed email information"""
    try:
        email = db.query(Email).filter(Email.id == email_id).first()
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
        return email
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching email detail: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch email detail")


@router.post("/{email_id}/summarize", response_model=SummaryResponse)
async def summarize_email(
    email_id: int,
    model: str = Query(None, description="LLM model to use (claude or gemini)"),
    db: Session = Depends(get_db),
):
    """Summarize email"""
    try:
        # Get email
        email = db.query(Email).filter(Email.id == email_id).first()
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")

        if not email.body:
            raise HTTPException(status_code=400, detail="Email body is empty")

        # Summarize email
        summarizer_service = get_summarizer_service()
        summary = await summarizer_service.summarize_email(
            email_id, email.body, db, model=model
        )

        return summary

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error summarizing email: {e}")
        raise HTTPException(status_code=500, detail="Failed to summarize email")


@router.post("/{email_id}/extract-actions")
async def extract_actions(
    email_id: int,
    model: str = Query(None, description="LLM model to use (claude or gemini)"),
    db: Session = Depends(get_db),
):
    """Extract action items from email"""
    try:
        # Get email
        email = db.query(Email).filter(Email.id == email_id).first()
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")

        if not email.body:
            raise HTTPException(status_code=400, detail="Email body is empty")

        # Extract actions
        action_service = get_action_extractor_service()
        actions = await action_service.extract_from_email(
            email_id, email.body, db, model=model
        )

        return {"email_id": email_id, "actions": actions}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting actions: {e}")
        raise HTTPException(status_code=500, detail="Failed to extract actions")


@router.get("/{email_id}/actions")
async def get_email_actions(
    email_id: int,
    db: Session = Depends(get_db),
):
    """Get extracted actions for email"""
    try:
        action_service = get_action_extractor_service()
        actions = action_service.get_actions_for_email(email_id, db)
        return {"email_id": email_id, "actions": actions}
    except Exception as e:
        logger.error(f"Error fetching actions: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch actions")


@router.post("/{email_id}/sync-outlook")
async def sync_outlook_email(
    email_id: int,
    db: Session = Depends(get_db),
):
    """Sync email from Outlook"""
    try:
        outlook_service = get_outlook_service()
        if not outlook_service.is_configured():
            raise HTTPException(status_code=503, detail="Outlook not configured")

        email = db.query(Email).filter(Email.id == email_id).first()
        if not email or not email.outlook_id:
            raise HTTPException(status_code=404, detail="Email not found or no Outlook ID")

        email_detail = await outlook_service.get_email_detail(email.outlook_id)
        if email_detail:
            email.subject = email_detail.get("subject", email.subject)
            email.body = email_detail.get("body", email.body)
            email.received_at = email_detail.get("received_at", email.received_at)
            db.commit()
            return {"status": "synced", "email": email}
        else:
            raise HTTPException(status_code=500, detail="Failed to sync from Outlook")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing email: {e}")
        raise HTTPException(status_code=500, detail="Failed to sync email")
