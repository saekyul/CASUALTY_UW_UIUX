"""
Tasks/Actions and Auto-Responses API Routes
"""
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schemas import ActionItemResponse, AutoResponseResponse
from app.models.database import ActionItem, AutoResponse, Email
from app.services.action_extractor import get_action_extractor_service
from app.services.email_responder import get_email_responder_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["tasks", "responses"])


class ActionUpdateRequest(BaseModel):
    """Update action item request"""

    is_completed: bool = None
    priority: str = None


class ResponseApprovalRequest(BaseModel):
    """Approve and send response request"""

    response_text: str


# Action/Task Endpoints


@router.get("/actions", response_model=List[ActionItemResponse])
async def get_pending_actions(
    completed: bool = Query(False, description="Filter by completion status"),
    priority: str = Query(None, description="Filter by priority (high/medium/low)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get action items"""
    try:
        query = db.query(ActionItem)

        if not completed:
            query = query.filter(ActionItem.is_completed == False)

        if priority:
            query = query.filter(ActionItem.priority == priority.lower())

        actions = query.offset(skip).limit(limit).all()
        return actions

    except Exception as e:
        logger.error(f"Error fetching actions: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch actions")


@router.get("/actions/high-priority", response_model=List[ActionItemResponse])
async def get_high_priority_actions(
    db: Session = Depends(get_db),
):
    """Get high priority pending actions"""
    try:
        action_service = get_action_extractor_service()
        actions = action_service.get_high_priority_actions(db)
        return actions
    except Exception as e:
        logger.error(f"Error fetching high priority actions: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch actions")


@router.get("/actions/{action_id}", response_model=ActionItemResponse)
async def get_action(
    action_id: int,
    db: Session = Depends(get_db),
):
    """Get specific action item"""
    try:
        action = db.query(ActionItem).filter(ActionItem.id == action_id).first()
        if not action:
            raise HTTPException(status_code=404, detail="Action not found")
        return action
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching action: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch action")


@router.patch("/actions/{action_id}", response_model=ActionItemResponse)
async def update_action(
    action_id: int,
    request: ActionUpdateRequest,
    db: Session = Depends(get_db),
):
    """Update action item"""
    try:
        action = db.query(ActionItem).filter(ActionItem.id == action_id).first()
        if not action:
            raise HTTPException(status_code=404, detail="Action not found")

        action_service = get_action_extractor_service()

        if request.is_completed is not None:
            if request.is_completed:
                action = action_service.mark_action_complete(action_id, db)
            else:
                action.is_completed = False
                action.completed_at = None
                db.commit()
                db.refresh(action)

        if request.priority is not None:
            action.priority = request.priority.lower()
            db.commit()
            db.refresh(action)

        return action

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating action: {e}")
        raise HTTPException(status_code=500, detail="Failed to update action")


@router.delete("/actions/{action_id}")
async def delete_action(
    action_id: int,
    db: Session = Depends(get_db),
):
    """Delete action item"""
    try:
        action_service = get_action_extractor_service()
        success = action_service.delete_action(action_id, db)

        if success:
            return {"status": "deleted", "action_id": action_id}
        else:
            raise HTTPException(status_code=404, detail="Action not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting action: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete action")


# Response/Auto-Reply Endpoints


@router.get("/responses", response_model=List[AutoResponseResponse])
async def get_response_suggestions(
    sent: bool = Query(False, description="Filter by sent status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get auto-response suggestions"""
    try:
        query = db.query(AutoResponse)

        if not sent:
            query = query.filter(AutoResponse.is_sent == False)
        else:
            query = query.filter(AutoResponse.is_sent == True)

        responses = query.offset(skip).limit(limit).all()
        return responses

    except Exception as e:
        logger.error(f"Error fetching responses: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch responses")


@router.get("/responses/{response_id}", response_model=AutoResponseResponse)
async def get_response(
    response_id: int,
    db: Session = Depends(get_db),
):
    """Get specific response suggestion"""
    try:
        response = db.query(AutoResponse).filter(AutoResponse.id == response_id).first()
        if not response:
            raise HTTPException(status_code=404, detail="Response not found")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching response: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch response")


@router.post("/responses/{response_id}/approve")
async def approve_response(
    response_id: int,
    request: ResponseApprovalRequest,
    db: Session = Depends(get_db),
):
    """Approve and send auto-response"""
    try:
        response = db.query(AutoResponse).filter(AutoResponse.id == response_id).first()
        if not response:
            raise HTTPException(status_code=404, detail="Response not found")

        if response.is_sent:
            raise HTTPException(status_code=400, detail="Response already sent")

        responder_service = get_email_responder_service()
        success = await responder_service.approve_and_send_response(
            response.email_id, request.response_text, db
        )

        if success:
            db.refresh(response)
            return {
                "status": "sent",
                "response": response,
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send response")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving response: {e}")
        raise HTTPException(status_code=500, detail="Failed to approve response")


@router.delete("/responses/{response_id}")
async def reject_response(
    response_id: int,
    db: Session = Depends(get_db),
):
    """Reject/delete auto-response suggestion"""
    try:
        response = db.query(AutoResponse).filter(AutoResponse.id == response_id).first()
        if not response:
            raise HTTPException(status_code=404, detail="Response not found")

        responder_service = get_email_responder_service()
        success = responder_service.reject_response_suggestion(response.email_id, db)

        if success:
            return {"status": "rejected", "response_id": response_id}
        else:
            raise HTTPException(status_code=400, detail="Cannot reject sent response")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rejecting response: {e}")
        raise HTTPException(status_code=500, detail="Failed to reject response")
