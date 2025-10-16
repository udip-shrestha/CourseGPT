import os, platform
from dotenv import load_dotenv
from fastapi import Depends
from API.Repository.sql_repository import SQLRepository
from API.Repository.postgres_connection_manager import PostgresConnectionManager
from API.Service.document_service import DocumentService

load_dotenv()

def get_connection_manager() -> PostgresConnectionManager:
    """Create and return a PostgreSQL connection manager."""
    db_host, db_port, db_name, db_password = os.environ["DB_HOST"], os.environ["DB_PORT"], os.environ["DB_NAME"], os.environ["DB_PASSWORD"]
    db_user =os.environ["DB_USER"] if platform.system() == "Windows" else os.getlogin()

    if platform.system() == "Darwin":
        db_url = f"postgresql://{db_user}@{db_host}:{db_port}/{db_name}"
    else:
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