import os, platform
from chromadb import Client, PersistentClient
from dotenv import load_dotenv
from fastapi import Depends
from API.Repository.sql_repository import SQLRepository
from API.Repository.postgres_connection_manager import PostgresConnectionManager
from API.Service.document_service import DocumentService
from API.Service.courses_service import CourseService
from API.Service.instructors_service import InstructorService
from API.Repository.chroma_vector_repository import ChromaVectorRepository


load_dotenv()


def get_connection_manager() -> PostgresConnectionManager:
    """Create and return a PostgreSQL connection manager."""
    db_host = os.environ["DB_HOST"]
    db_port = os.environ["DB_PORT"]
    db_name = os.environ["DB_NAME"]
    db_user = os.environ["DB_USER"]
    db_password = os.environ["DB_PASSWORD"]

    db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    return PostgresConnectionManager(db_url=db_url)


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


def get_chroma_client() -> Client:
    """Create and return a persistent Chroma client."""
    chroma_dir = os.environ["CHROMA_DATA_PATH"]
    return PersistentClient(path=chroma_dir)


def get_vector_repository(
    client: Client = Depends(get_chroma_client),
):
    """Provide a Chroma-based vector repository instance."""
    return ChromaVectorRepository(client)