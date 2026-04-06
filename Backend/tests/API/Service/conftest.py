import pytest
from unittest.mock import MagicMock
from langchain_core.language_models import BaseLanguageModel
from langchain_text_splitters import TextSplitter

from API.Repository.i_sql_repository import ISQLRepository 
from API.Service.document_service import DocumentService 
from API.Service.rag_service import RAGService 
from API.Service.courses_service import CourseService
from API.Service.auth_service import AuthService
from API.Service.instructors_service import InstructorService
from API.Service.students_service import StudentService
from API.Service.queries_service import QueryService
from API.Service.gmail_service import GmailService
from API.Repository.i_vector_repository import IVectorRepository
from API.Util.rag_strategy import RAGStrategyFactory
from API.Util.loaders import LoaderFactory


@pytest.fixture
def mock_sql_repo() -> ISQLRepository:
    """Provides a mocked SQL repository instance."""
    return MagicMock(spec=ISQLRepository)


@pytest.fixture
def mock_vector_repo() -> IVectorRepository:
    """Provides a mocked vector repository instance."""
    return MagicMock(spec=IVectorRepository)


@pytest.fixture
def mock_loader_factory() -> LoaderFactory:
    """Provides an empty mocked Loader instance."""
    return MagicMock(spec=LoaderFactory)


@pytest.fixture
def mock_splitter() -> TextSplitter:
    """Provides an empty mocked Splitter instance."""
    return MagicMock(spec=TextSplitter)


@pytest.fixture
def mock_rag_strategy_factory() -> RAGStrategyFactory:
    """Provides a plain mocked RAG strategy instance."""
    return MagicMock(spec=RAGStrategyFactory)


@pytest.fixture
def mock_llm() -> BaseLanguageModel:
    """Provides an empty mocked LLM instance."""
    return MagicMock(spec=BaseLanguageModel)

@pytest.fixture
def mock_rag_service() -> RAGService:
    """Provides a plain mocked RAGService instance."""
    return MagicMock(spec=RAGService)

@pytest.fixture
def mock_gmail_service() -> GmailService:
    """Provides a GmailService instance."""
    return MagicMock(spec=GmailService)

@pytest.fixture
def rag_service(
    mock_loader_factory: LoaderFactory,
    mock_splitter: TextSplitter,
    mock_rag_strategy_factory: RAGStrategyFactory,
    mock_vector_repo: IVectorRepository,
    mock_sql_repo: ISQLRepository,
    mock_llm: BaseLanguageModel,
) -> RAGService:
    """Provides a RAGService wired with plain mock dependencies."""
    return RAGService(
        vector_repo=mock_vector_repo,
        sql_repo=mock_sql_repo,
        loader_factory=mock_loader_factory,
        rag_strategy_factory=mock_rag_strategy_factory,
        splitter=mock_splitter,
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
    return AuthService(sql_repo=mock_sql_repo, gmail_service=mock_gmail_service)


@pytest.fixture
def instructor_service(mock_sql_repo: ISQLRepository) -> InstructorService:
    """Provides an InstructorService wired with a mock SQL repository."""
    return InstructorService(sql_repo=mock_sql_repo)


@pytest.fixture
def student_service(mock_sql_repo: ISQLRepository) -> StudentService:
    """Provides a StudentService wired with a mock SQL repository."""
    return StudentService(sql_repo=mock_sql_repo)


@pytest.fixture
def query_service(mock_sql_repo, mock_rag_service):
    """Provides a plain mocked QueryService instance."""
    return QueryService(sql_repo=mock_sql_repo, rag_service=mock_rag_service)
