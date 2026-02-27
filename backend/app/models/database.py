"""
SQLAlchemy ORM Models
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    """User Model"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    emails = relationship("Email", back_populates="user")
    work_logs = relationship("WorkLog", back_populates="user")


class Email(Base):
    """Email Model (from Outlook)"""

    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    outlook_id = Column(String(255), unique=True, index=True)
    sender = Column(String(255), nullable=False)
    subject = Column(String(500), nullable=False)
    body = Column(Text, nullable=True)
    received_at = Column(DateTime(timezone=True), nullable=True)
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="emails")
    summary = relationship("Summary", uselist=False, back_populates="email")
    action_items = relationship("ActionItem", back_populates="email")
    auto_response = relationship("AutoResponse", uselist=False, back_populates="email")


class WorkLog(Base):
    """Work Log Model (from PostgreSQL legacy system)"""

    __tablename__ = "work_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="pending")
    priority = Column(String(20), default="medium")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="work_logs")


class Summary(Base):
    """Summary Model (LLM-generated summaries)"""

    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Integer, ForeignKey("emails.id"), unique=True, nullable=False)
    summary_text = Column(Text, nullable=False)
    llm_model = Column(String(50), nullable=False)
    tokens_used = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    email = relationship("Email", back_populates="summary")


class ActionItem(Base):
    """Action Item Model (extracted from emails)"""

    __tablename__ = "action_items"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Integer, ForeignKey("emails.id"), nullable=False)
    action_text = Column(Text, nullable=False)
    priority = Column(String(20), default="medium")
    deadline = Column(DateTime(timezone=True), nullable=True)
    is_completed = Column(Boolean, default=False)
    llm_model = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    email = relationship("Email", back_populates="action_items")


class AutoResponse(Base):
    """Auto Response Model"""

    __tablename__ = "auto_responses"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Integer, ForeignKey("emails.id"), unique=True, nullable=False)
    suggested_response = Column(Text, nullable=False)
    final_response = Column(Text, nullable=True)
    is_sent = Column(Boolean, default=False)
    llm_model = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sent_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    email = relationship("Email", back_populates="auto_response")
