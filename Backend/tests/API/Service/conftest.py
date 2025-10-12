# tests/conftest.py
import pytest
from API.Repository.fake_sql_repository import ISQLRepository, FakeSQLRepository
from API.Service.document_service import DocumentService


@pytest.fixture
def sql_repo() -> ISQLRepository:
    """
    Provides a fresh FakeSQLRepository instance for each test.
    Simulates an in-memory SQL database.
    """
    return FakeSQLRepository()


@pytest.fixture
def document_service(sql_repo: ISQLRepository) -> DocumentService:
    """
    Provides a DocumentService using the fake repository.
    Other service fixtures can depend on sql_repo too.
    """
    return DocumentService(sql_repo)
