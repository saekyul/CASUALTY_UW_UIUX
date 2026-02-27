"""
Tests for Database Models
"""
import pytest
from sqlalchemy.orm import Session

from app.models.database import User, Email, Summary, ActionItem, AutoResponse
from app.tests.conftest import test_user, test_email


def test_create_user(db: Session):
    """Test user creation"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.is_active is True


def test_create_email(db: Session, test_user: User):
    """Test email creation"""
    email = Email(
        user_id=test_user.id,
        outlook_id="outlook_123",
        sender="sender@example.com",
        subject="Test Email",
        body="Test body",
    )
    db.add(email)
    db.commit()
    db.refresh(email)

    assert email.id is not None
    assert email.sender == "sender@example.com"
    assert email.subject == "Test Email"
    assert email.is_processed is False


def test_create_summary(db: Session, test_email: Email):
    """Test summary creation"""
    summary = Summary(
        email_id=test_email.id,
        summary_text="This is a summary",
        llm_model="claude",
        tokens_used=100,
    )
    db.add(summary)
    db.commit()
    db.refresh(summary)

    assert summary.id is not None
    assert summary.summary_text == "This is a summary"
    assert summary.llm_model == "claude"


def test_create_action_item(db: Session, test_email: Email):
    """Test action item creation"""
    action = ActionItem(
        email_id=test_email.id,
        action_text="Do something important",
        priority="high",
        llm_model="claude",
    )
    db.add(action)
    db.commit()
    db.refresh(action)

    assert action.id is not None
    assert action.action_text == "Do something important"
    assert action.priority == "high"
    assert action.is_completed is False


def test_create_auto_response(db: Session, test_email: Email):
    """Test auto response creation"""
    response = AutoResponse(
        email_id=test_email.id,
        suggested_response="Thank you for your email",
        llm_model="claude",
    )
    db.add(response)
    db.commit()
    db.refresh(response)

    assert response.id is not None
    assert response.suggested_response == "Thank you for your email"
    assert response.is_sent is False


def test_email_relationships(db: Session, test_user: User):
    """Test email relationships"""
    email = Email(
        user_id=test_user.id,
        sender="test@example.com",
        subject="Test",
        body="Body",
    )
    db.add(email)
    db.commit()
    db.refresh(email)

    assert email.user is not None
    assert email.user.id == test_user.id

    # Add summary
    summary = Summary(
        email_id=email.id,
        summary_text="Summary",
        llm_model="claude",
    )
    db.add(summary)
    db.commit()
    db.refresh(email)

    assert email.summary is not None
    assert email.summary.summary_text == "Summary"

    # Add action items
    action = ActionItem(
        email_id=email.id,
        action_text="Action",
        llm_model="claude",
    )
    db.add(action)
    db.commit()
    db.refresh(email)

    assert len(email.action_items) == 1
