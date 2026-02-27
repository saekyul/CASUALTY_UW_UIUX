"""
Data/Database Query API Routes
"""
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.text_to_sql import get_text_to_sql_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/data", tags=["data"])


class QueryRequest(BaseModel):
    """Natural language query request"""

    query: str
    model: str = None  # Optional: claude or gemini


class QueryResponse(BaseModel):
    """Query response"""

    status: str
    sql_query: str
    results: List[dict]
    error: str = None


@router.post("/query", response_model=QueryResponse)
async def execute_natural_language_query(
    request: QueryRequest,
    db: Session = Depends(get_db),
):
    """Execute natural language query"""
    try:
        if not request.query or not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        text_to_sql_service = get_text_to_sql_service()

        # Convert natural language to SQL and execute
        results, sql_query, success = await text_to_sql_service.convert_and_execute(
            request.query, db, model=request.model
        )

        if success:
            return QueryResponse(
                status="success",
                sql_query=sql_query,
                results=results,
            )
        else:
            return QueryResponse(
                status="error",
                sql_query=sql_query,
                results=[],
                error="Failed to execute query",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        raise HTTPException(status_code=500, detail="Failed to execute query")


@router.post("/convert-to-sql")
async def convert_to_sql(
    request: QueryRequest,
    db: Session = Depends(get_db),
):
    """Convert natural language to SQL (without executing)"""
    try:
        if not request.query or not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        text_to_sql_service = get_text_to_sql_service()

        # Convert natural language to SQL
        sql_query, model_used, is_valid = await text_to_sql_service.convert_to_sql(
            request.query, db, model=request.model
        )

        return {
            "status": "success" if is_valid else "invalid",
            "sql_query": sql_query,
            "model_used": model_used,
            "is_valid": is_valid,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error converting to SQL: {e}")
        raise HTTPException(status_code=500, detail="Failed to convert to SQL")


@router.get("/schema")
async def get_database_schema(
    db: Session = Depends(get_db),
):
    """Get database schema information"""
    try:
        text_to_sql_service = get_text_to_sql_service()
        schema_info = text_to_sql_service.get_schema_info(db)
        return {
            "schema": schema_info,
        }
    except Exception as e:
        logger.error(f"Error fetching schema: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch schema")
