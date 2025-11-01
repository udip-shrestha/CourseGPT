from langchain_core.language_models import BaseLanguageModel
import pytest
from API.Repository.i_sql_repository import ISQLRepository 
from API.Service.document_service import DocumentService 
from API.Service.rag_service import RAGService 
from API.Service.courses_service import CourseService
from API.Service.auth_service import AuthService
from API.Service.instructors_service import InstructorService
from API.Repository.i_vector_repository import IVectorRepository
from unittest.mock import MagicMock
from API.Util.loaders import Loader
from API.Util.splitters import Splitter
from API.Util.prompt_builders import PromptBuilder
from langchain_core.language_models import BaseLanguageModel


@pytest.fixture
def mock_sql_repo() -> ISQLRepository:
    """Provides a mocked SQL repository instance."""
    return MagicMock(spec=ISQLRepository)


@pytest.fixture
def mock_vector_repo() -> IVectorRepository:
    """Provides a mocked vector repository instance."""
    return MagicMock(spec=IVectorRepository)


@pytest.fixture
def mock_loader() -> Loader:
    """Provides an empty mocked Loader instance."""
    return MagicMock(spec=Loader)


@pytest.fixture
def mock_splitter() -> Splitter:
    """Provides an empty mocked Splitter instance."""
    return MagicMock(spec=Splitter)


@pytest.fixture
def mock_prompt_builder() -> PromptBuilder:
    """Provides an empty mocked PromptBuilder instance."""
    return MagicMock(spec=PromptBuilder)


@pytest.fixture
def mock_llm() -> BaseLanguageModel:
    """Provides an empty mocked LLM instance."""
    return MagicMock(spec=BaseLanguageModel)


@pytest.fixture
def mock_rag_service() -> RAGService:
    """Provides a plain mocked RAGService instance."""
    return MagicMock(spec=RAGService)

@pytest.fixture
def rag_service(
    mock_loader: MagicMock,
    mock_splitter: MagicMock,
    mock_vector_repo: IVectorRepository,
    mock_prompt_builder: MagicMock,
    mock_llm: MagicMock,
) -> RAGService:
    """Provides a RAGService wired with plain mock dependencies."""
    return RAGService(
        loader=mock_loader,
        splitter=mock_splitter,
        vector_repo=mock_vector_repo,
        prompt_builder=mock_prompt_builder,
        llm=mock_llm,
    )


@pytest.fixture 
def document_service(mock_sql_repo: ISQLRepository, mock_rag_service: RAGService) -> DocumentService: 
    """ Provides a DocumentService using the fake repository. Other service fixtures can depend on sql_repo too. """ 
    return DocumentService(mock_sql_repo, mock_rag_service)


@pytest.fixture
def course_service(mock_sql_repo: ISQLRepository, mock_vector_repo: IVectorRepository) -> CourseService:
    """Provides a CourseService instance with mock repositories."""
    return CourseService(sql_repo=mock_sql_repo, vector_repo=mock_vector_repo)


@pytest.fixture
def auth_service(mock_sql_repo: ISQLRepository) -> AuthService:
    """Provides an AuthService wired with a mock SQL repository."""
    return AuthService(sql_repo=mock_sql_repo)


@pytest.fixture
def instructor_service(mock_sql_repo: ISQLRepository) -> InstructorService:
    """Provides an InstructorService wired with a mock SQL repository."""
    return InstructorService(sql_repo=mock_sql_repo)
