"""
Text-to-SQL Service - Convert natural language to SQL queries
"""
import logging
import re
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.services.llm_service import get_llm_service

logger = logging.getLogger(__name__)


class TextToSQLService:
    """Service for converting natural language to SQL queries"""

    def __init__(self):
        self.llm_service = get_llm_service()

    def get_schema_info(self, db: Session) -> str:
        """
        Get database schema information

        Args:
            db: Database session

        Returns:
            Schema information as string
        """
        try:
            # Get all tables and their columns
            inspector_query = """
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
            """

            tables_result = db.execute(text(inspector_query)).fetchall()
            schema_info = "데이터베이스 스키마:\n\n"

            for (table_name,) in tables_result:
                columns_query = f"""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = '{table_name}' AND table_schema = 'public'
                """

                columns_result = db.execute(text(columns_query)).fetchall()

                schema_info += f"테이블: {table_name}\n"
                for column_name, data_type in columns_result:
                    schema_info += f"  - {column_name}: {data_type}\n"
                schema_info += "\n"

            return schema_info

        except Exception as e:
            logger.error(f"Error getting schema info: {e}")
            return "데이터베이스 스키마를 가져올 수 없습니다."

    async def convert_to_sql(
        self,
        natural_language_query: str,
        db: Session,
        model: str = None,
    ) -> tuple[str, str, bool]:
        """
        Convert natural language query to SQL

        Args:
            natural_language_query: Natural language query
            db: Database session
            model: LLM model to use

        Returns:
            Tuple of (sql_query, model_used, is_valid)
        """
        try:
            # Get schema information
            schema_info = self.get_schema_info(db)

            # Generate SQL using LLM
            sql_query, model_used, tokens_used = await self.llm_service.text_to_sql(
                natural_language_query, schema_info, model=model
            )

            # Validate SQL query
            is_valid = self._validate_sql(sql_query)

            logger.info(f"Generated SQL using {model_used}. Valid: {is_valid}")
            return sql_query, model_used, is_valid

        except Exception as e:
            logger.error(f"Error converting to SQL: {e}")
            return "", "", False

    def _validate_sql(self, sql_query: str) -> bool:
        """
        Basic SQL validation

        Args:
            sql_query: SQL query to validate

        Returns:
            True if query appears valid, False otherwise
        """
        # Remove whitespace and convert to uppercase
        cleaned_query = sql_query.strip().upper()

        # Check for dangerous operations
        dangerous_keywords = [
            "DROP",
            "DELETE",
            "TRUNCATE",
            "ALTER TABLE",
            "CREATE",
            "INSERT",
            "UPDATE",
        ]

        for keyword in dangerous_keywords:
            if keyword in cleaned_query:
                logger.warning(f"Potentially dangerous SQL operation detected: {keyword}")
                return False

        # Check for valid SELECT statement
        if not cleaned_query.startswith("SELECT"):
            logger.warning("SQL query does not start with SELECT")
            return False

        # Check for valid FROM clause
        if "FROM" not in cleaned_query:
            logger.warning("SQL query does not contain FROM clause")
            return False

        return True

    async def execute_query(
        self,
        sql_query: str,
        db: Session,
        limit: int = 1000,
    ) -> tuple[list[dict], bool]:
        """
        Execute SQL query safely

        Args:
            sql_query: SQL query to execute
            db: Database session
            limit: Maximum number of rows to return

        Returns:
            Tuple of (results, success)
        """
        try:
            # Validate query
            if not self._validate_sql(sql_query):
                logger.error("Invalid SQL query")
                return [], False

            # Add LIMIT if not present
            if "LIMIT" not in sql_query.upper():
                sql_query = f"{sql_query} LIMIT {limit}"

            # Execute query
            result = db.execute(text(sql_query))
            rows = result.fetchall()

            # Convert to dictionaries
            results = []
            if result.keys():
                for row in rows:
                    results.append(dict(zip(result.keys(), row)))

            logger.info(f"Query executed successfully. Rows returned: {len(results)}")
            return results, True

        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return [], False

    async def convert_and_execute(
        self,
        natural_language_query: str,
        db: Session,
        model: str = None,
    ) -> tuple[list[dict], str, bool]:
        """
        Convert natural language to SQL and execute

        Args:
            natural_language_query: Natural language query
            db: Database session
            model: LLM model to use

        Returns:
            Tuple of (results, sql_query, success)
        """
        try:
            # Convert to SQL
            sql_query, model_used, is_valid = await self.convert_to_sql(
                natural_language_query, db, model=model
            )

            if not is_valid:
                logger.error("Generated SQL query is invalid")
                return [], sql_query, False

            # Execute query
            results, success = await self.execute_query(sql_query, db)

            return results, sql_query, success

        except Exception as e:
            logger.error(f"Error in convert_and_execute: {e}")
            return [], "", False


# Singleton instance
_text_to_sql_service = None


def get_text_to_sql_service() -> TextToSQLService:
    """Get or create text-to-SQL service instance"""
    global _text_to_sql_service
    if _text_to_sql_service is None:
        _text_to_sql_service = TextToSQLService()
    return _text_to_sql_service
