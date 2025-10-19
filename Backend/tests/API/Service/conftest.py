import pytest 
from API.Repository.i_sql_repository import ISQLRepository 
from API.Service.document_service import DocumentService 
from unittest.mock import MagicMock 


@pytest.fixture 
def mock_sql_repo(): 
    """ Provides a mock SQLRepository instance for each test. """ 
    return MagicMock(spec=ISQLRepository) 
    
    
@pytest.fixture 
def document_service(mock_sql_repo: ISQLRepository) -> DocumentService: 
    """ Provides a DocumentService using the fake repository. Other service fixtures can depend on sql_repo too. """ 
    return DocumentService(mock_sql_repo)