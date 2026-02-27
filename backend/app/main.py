"""
FastAPI Main Application
"""
import logging
from datetime import datetime

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.config import settings
from app.database import engine, get_db
from app.models.database import Base
from app.models.schemas import StatusResponse

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="LLM Data Integration PoC API",
    docs_url="/docs",
    openapi_url="/openapi.json",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "timestamp": datetime.now()}


# Status endpoint
@app.get("/api/status", response_model=StatusResponse)
async def get_status(db: Session = Depends(get_db)) -> StatusResponse:
    """
    Get system status and integration check
    """
    # Check database connection
    db_connected = True
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        db_connected = False

    # Check Claude API availability
    claude_available = settings.CLAUDE_API_KEY is not None

    # Check Gemini API availability
    gemini_available = settings.GEMINI_API_KEY is not None

    # Check Outlook configuration
    outlook_configured = all(
        [
            settings.OUTLOOK_CLIENT_ID,
            settings.OUTLOOK_CLIENT_SECRET,
            settings.OUTLOOK_TENANT_ID,
        ]
    )

    return StatusResponse(
        status="healthy" if all([db_connected, claude_available or gemini_available]) else "degraded",
        database_connected=db_connected,
        claude_api_available=claude_available,
        gemini_api_available=gemini_available,
        outlook_configured=outlook_configured,
        timestamp=datetime.now(),
    )


# Include API routes
from app.api.routes import emails, data, tasks

app.include_router(emails.router)
app.include_router(data.router)
app.include_router(tasks.router)


@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info(f"Starting {settings.APP_NAME}")
    logger.info(f"Environment: {settings.ENV}")
    logger.info(f"Debug: {settings.DEBUG}")
    logger.info(f"Preferred LLM: {settings.PREFERRED_LLM}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Shutting down application")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
