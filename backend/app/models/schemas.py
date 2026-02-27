"""
Pydantic Schemas for API
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """User Base Schema"""

    username: str
    email: EmailStr


class UserCreate(UserBase):
    """User Create Schema"""

    password: str


class UserUpdate(BaseModel):
    """User Update Schema"""

    username: Optional[str] = None
    email: Optional[EmailStr] = None


class UserResponse(UserBase):
    """User Response Schema"""

    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class EmailBase(BaseModel):
    """Email Base Schema"""

    sender: str
    subject: str
    body: Optional[str] = None


class EmailCreate(EmailBase):
    """Email Create Schema"""

    outlook_id: Optional[str] = None
    received_at: Optional[datetime] = None


class EmailResponse(EmailBase):
    """Email Response Schema"""

    id: int
    user_id: int
    outlook_id: Optional[str]
    received_at: Optional[datetime]
    is_processed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SummaryResponse(BaseModel):
    """Summary Response Schema"""

    id: int
    email_id: int
    summary_text: str
    llm_model: str
    tokens_used: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class ActionItemResponse(BaseModel):
    """Action Item Response Schema"""

    id: int
    email_id: int
    action_text: str
    priority: str
    deadline: Optional[datetime]
    is_completed: bool
    llm_model: str
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class AutoResponseResponse(BaseModel):
    """Auto Response Response Schema"""

    id: int
    email_id: int
    suggested_response: str
    final_response: Optional[str]
    is_sent: bool
    llm_model: str
    created_at: datetime
    sent_at: Optional[datetime]

    class Config:
        from_attributes = True


class EmailDetailResponse(EmailResponse):
    """Email Detail Response with Summary and Actions"""

    summary: Optional[SummaryResponse] = None
    action_items: list[ActionItemResponse] = []
    auto_response: Optional[AutoResponseResponse] = None

    class Config:
        from_attributes = True


class StatusResponse(BaseModel):
    """System Status Response"""

    status: str
    database_connected: bool
    claude_api_available: bool
    gemini_api_available: bool
    outlook_configured: bool
    timestamp: datetime
