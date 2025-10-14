"""
Dependency providers for FastAPI routes.

Defines how services, repositories, and DB connections are created
and injected into route handlers using FastAPI's Depends().
"""

from fastapi import Depends
from API.Repository.sql_repository import SQLRepository
from API.Repository.postgres_connection_manager import PostgresConnectionManager
from API.Service.document_service import DocumentService
from API.Service.courses_service import CourseService
from API.Service.instructors_service import InstructorService


def get_connection_manager() -> PostgresConnectionManager:
    """Create and return a PostgreSQL connection manager."""
    return PostgresConnectionManager(
        db_url="postgresql://postgres:postgres@localhost:5432/course_gpt"
    )


def get_sql_repository(
    cm: PostgresConnectionManager = Depends(get_connection_manager),
) -> SQLRepository:
    """Provide an SQL repository using the connection manager."""
    return SQLRepository(cm)


def get_document_service(
    sql_repo: SQLRepository = Depends(get_sql_repository),
) -> DocumentService:
    """Provide a DocumentService using the SQL repository."""
    return DocumentService(sql_repo)

def get_course_service(
    sql_repo: SQLRepository = Depends(get_sql_repository),
) -> CourseService:
    """Provide a CourseService using the SQL repository."""
    return CourseService(sql_repo)

def get_instructor_service(
    sql_repo: SQLRepository = Depends(get_sql_repository),
) -> InstructorService:
    """Provide an InstructorService using the SQL repository."""
    return InstructorService(sql_repo)