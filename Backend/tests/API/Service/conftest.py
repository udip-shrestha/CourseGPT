import pytest 
from unittest.mock import create_autospec
from API.Repository.i_sql_repository import ISQLRepository 
from API.Service.document_service import DocumentService 
from API.Service.rag_service import RAGService 
from unittest.mock import MagicMock 


@pytest.fixture 
def mock_sql_repo(): 
    """ Provides a mock SQLRepository instance for each test. """ 
    return MagicMock(spec=ISQLRepository) 
    

import pytest
from unittest.mock import MagicMock
from API.Service.rag_service import RAGService

@pytest.fixture
def mock_rag_service() -> RAGService:
    """Mock RAGService for dependency injection."""
    return MagicMock(spec=RAGService)


@pytest.fixture 
def document_service(mock_sql_repo: ISQLRepository, mock_rag_service: RAGService) -> DocumentService: 
    """ Provides a DocumentService using the fake repository. Other service fixtures can depend on sql_repo too. """ 
    return DocumentService(mock_sql_repo, mock_rag_service)

@pytest.fixture 
def mock_sql_repo(): 
    """Provides a mock SQLRepository instance for each test."""
    mock_repo = MagicMock()  
    return mock_repo
