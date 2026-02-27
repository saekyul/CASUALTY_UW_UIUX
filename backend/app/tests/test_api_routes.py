"""
Tests for API Routes
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database import get_db
from app.tests.conftest import TestingSessionLocal, test_user, test_email


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "ok"


def test_get_status():
    """Test status endpoint"""
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database_connected" in data
    assert "claude_api_available" in data
    assert "gemini_api_available" in data
    assert "outlook_configured" in data


def test_get_emails_empty(db: Session):
    """Test get emails endpoint with empty database"""
    response = client.get("/api/emails")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_get_emails_with_data(db: Session, test_email):
    """Test get emails endpoint with data"""
    response = client.get("/api/emails")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["sender"] == "sender@example.com"


def test_get_email_detail(db: Session, test_email):
    """Test get email detail endpoint"""
    response = client.get(f"/api/emails/{test_email.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_email.id
    assert data["sender"] == "sender@example.com"


def test_get_email_detail_not_found():
    """Test get email detail endpoint with non-existent ID"""
    response = client.get("/api/emails/999")
    assert response.status_code == 404


def test_get_actions_for_email(db: Session, test_email):
    """Test get actions endpoint"""
    response = client.get(f"/api/emails/{test_email.id}/actions")
    assert response.status_code == 200
    data = response.json()
    assert "email_id" in data
    assert "actions" in data


def test_get_pending_actions(db: Session):
    """Test get pending actions endpoint"""
    response = client.get("/api/actions")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_responses(db: Session):
    """Test get responses endpoint"""
    response = client.get("/api/responses")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_database_schema(db: Session):
    """Test database schema endpoint"""
    response = client.get("/api/data/schema")
    assert response.status_code == 200
    data = response.json()
    assert "schema" in data
