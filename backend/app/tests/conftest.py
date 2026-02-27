"""
Test Configuration and Fixtures
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.database import Base
from app.models.database import User, Email, Summary, ActionItem, AutoResponse

# Create test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def pytest_configure():
    """Create test database tables"""
    Base.metadata.create_all(bind=engine)


def pytest_unconfigure():
    """Drop test database tables"""
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db() -> Session:
    """Create a test database session"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def test_user(db: Session) -> User:
    """Create a test user"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password_123",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_email(db: Session, test_user: User) -> Email:
    """Create a test email"""
    email = Email(
        user_id=test_user.id,
        outlook_id="outlook_123",
        sender="sender@example.com",
        subject="Test Email",
        body="This is a test email body. Please summarize this and extract action items.",
        received_at="2024-01-01T12:00:00Z",
    )
    db.add(email)
    db.commit()
    db.refresh(email)
    return email
