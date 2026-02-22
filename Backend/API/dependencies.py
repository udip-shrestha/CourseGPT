
import os
import logging
from typing import Dict
from functools import lru_cache
from dotenv import load_dotenv
from chromadb import Client, PersistentClient, HttpClient
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel
from langchain_ollama import ChatOllama
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_text_splitters import RecursiveCharacterTextSplitter, TextSplitter

from API.Repository.sql_repository import SQLRepository
from API.Repository.postgres_connection_manager import PostgresConnectionManager
from API.Service.document_service import DocumentService
from API.Service.auth_service import AuthService
from API.Service.rag_service import RAGService
from API.Service.courses_service import CourseService
from API.Service.instructors_service import InstructorService
from API.Service.students_service import StudentService
from API.Service.queries_service import QueryService
from API.Service.feedback_service import FeedbackService
from API.Service.analytics_service import AnalyticsService
from API.Repository.i_vector_repository import IVectorRepository
from API.Repository.chroma_vector_repository import ChromaVectorRepository
from API.Util.loaders import LOADER_CLASS_REGISTRY, ILoader, LoaderFactory
from API.Util.rag_strategy import STRATEGY_CLASS_REGISTRY, IRAGStrategy, RAGStrategyFactory
from API.Util.auth import decrypt_access_token
from API.Util.web_socket_manager import WebSocketManager


load_dotenv()


logger = logging.getLogger(__name__)


# ============================================================
# 🔌 DATABASE CLIENT SETUP
# ============================================================


@lru_cache()
def get_connection_manager() -> PostgresConnectionManager:
    """Create and return a PostgreSQL connection manager."""
    db_host = os.environ["DB_HOST"]
    db_port = os.environ["DB_PORT"]
    db_name = os.environ["DB_NAME"]
    db_user = os.environ["DB_USER"]
    db_password = os.environ["DB_PASSWORD"]

    db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    return PostgresConnectionManager(db_url=db_url)


@lru_cache()
def get_chroma_client() -> Client:
    """Create and return a persistent Chroma client."""
    client_type = os.environ["CHROMA_CLIENT"].lower()

    if client_type == "http":
        return HttpClient(host=os.environ["CHROMA_HOST"], port=int(os.environ["CHROMA_PORT"]))

    elif client_type == "persistent":
        return PersistentClient(path=["CHROMA_DATA_PATH"])

    else:
        raise ValueError(f"Invalid CHROMA_CLIENT type: {client_type}. Expected 'persistent' or 'http'.")


# ============================================================
# 🏗️ REPOSITORY SETUP
# ============================================================


def get_sql_repository(
    cm: PostgresConnectionManager = Depends(get_connection_manager),
) -> SQLRepository:
    """Provide an SQL repository using the connection manager."""
    return SQLRepository(cm)


def get_vector_repository(
    client: Client = Depends(get_chroma_client),
) -> IVectorRepository:
    """Provide a Chroma-based vector repository instance."""
    return ChromaVectorRepository(client)


# ============================================================
# 🔐 AUTHENTICATION SETUP
# ============================================================


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def authorize(
    token: str = Depends(oauth2_scheme),
    sql_repo: SQLRepository = Depends(get_sql_repository),
) -> dict:
    """Decode JWT (fake JSON token) and return instructor record from DB."""
    if not token or token.strip() == "":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization token", headers={"WWW-Authenticate": "Bearer"})

    try:
        payload = decrypt_access_token(token)
        token_instructor_id = payload["id"]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Unauthorized: {str(e)}", headers={"WWW-Authenticate": "Bearer"})

    instructor = sql_repo.read_instructor(token_instructor_id)
    if not instructor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instructor not found")

    return instructor


def authorize_instructor(
    instructor_id: str,
    auth: dict = Depends(authorize),
) -> dict:
    """Allow instructor self-access or ADMIN access."""
    if instructor_id and str(instructor_id) != str(auth["id"]) and auth["role"] != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to access this instructor’s resources")
    return auth


def authorize_admin(
    auth: dict = Depends(authorize),
) -> dict:
    """Allow only ADMIN users."""
    if auth["role"] != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return auth


def validate_course(
    course_id: str,
    sql_repo: SQLRepository = Depends(get_sql_repository),
) -> dict:
    """Validate that the course exists."""
    course = sql_repo.read_course(course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    return course


def authorize_course(
    auth: dict = Depends(authorize),
    course: dict = Depends(validate_course),
) -> dict:
    """Authorize access to a course based on instructor ownership or ADMIN role."""
    if auth["role"] != "ADMIN" and course["instructor_id"] != auth["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this course")

    return course


# ============================================================
# 🔌 WEBSOCKET MANAGER SETUP
# ============================================================


@lru_cache()
def get_web_socket_manager() -> WebSocketManager:
    """
    Provide a singleton WebSocketManager instance.

    - Manages WebSocket connections grouped by topic (URL path)
    - Subscribes/unsubscribes clients automatically
    - Allows broadcast of real-time updates to subscribed clients
    """
    return WebSocketManager()


# ============================================================
# 🧠 LLM  SETUP
# ============================================================


@lru_cache
def get_splitter() -> TextSplitter:
    """Return a Singleton Splitter instance for document chunking."""
    return RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=128,
        length_function=len,
        separators=[
            "\n\n",    # paragraph
            "\n",      # line
            ". ",      # sentence
            "; ",      # semi-structured
            ", ",      # NEW: improves CSV/XLSX rows
            " ",       # word level
            ""         # fallback
        ],
    )


@lru_cache()
def get_loader_factory(
    sql_repo: SQLRepository = Depends(get_sql_repository)
) -> LoaderFactory:
    """Builds a LoaderFactory from DB: mime_type → instantiated loader class."""
    file_types = sql_repo.read_all_file_types()  # expected: List[{ "mime_type": str, "class_name": str }]

    # --- Detect invalid loader classes from DB ---
    invalid = { row["class_name"] for row in file_types if row["class_name"] not in LOADER_CLASS_REGISTRY}
    if invalid:
        raise ValueError(f"Invalid loader classes in file_types table: {invalid}. Valid: {list(LOADER_CLASS_REGISTRY.keys())}")

    loader_registry_from_db: Dict[str, ILoader] = { row["mime_type"]: LOADER_CLASS_REGISTRY[row["class_name"]]() for row in file_types if row["class_name"] in LOADER_CLASS_REGISTRY }
    return LoaderFactory(loader_registry_from_db)


@lru_cache()
def get_rag_strategy_factory(
    sql_repo: SQLRepository = Depends(get_sql_repository)
) -> RAGStrategyFactory:
    """Build RagStrategyFactory from DB: rag_strategy_id → instantiated strategy class."""
    rag_strategies = sql_repo.read_all_rag_strategies()   # returns { id, type_name, class_name, description }

    # Detect invalid classes from DB
    invalid = { row["class_name"] for row in rag_strategies if row["class_name"] not in STRATEGY_CLASS_REGISTRY }
    if invalid:
        raise ValueError(f"Invalid strategy classes in rag_types table: {invalid}. Valid: {list(STRATEGY_CLASS_REGISTRY.keys())}")

    rag_strategy_registry_from_db: Dict[str, IRAGStrategy] = { str(row["id"]): STRATEGY_CLASS_REGISTRY[row["class_name"]]() for row in rag_strategies if row["class_name"] in STRATEGY_CLASS_REGISTRY }
    return RAGStrategyFactory(rag_strategy_registry_from_db)


@lru_cache()
def get_llm() -> BaseChatModel:
    llm_provider = os.environ["LLM_PROVIDER"].lower()
    logger.info(f"[LLM] LLM_PROVIDER detected as {llm_provider}.")

    if llm_provider == "huggingface":
        model_id, token = os.environ["LLM_MODEL"], os.environ["HUGGINGFACEHUB_API_TOKEN"]
        logger.info(f"[LLM INIT] Initializing HuggingFace Chat Model ID: {model_id}")
        
        endpoint = HuggingFaceEndpoint(
            repo_id=model_id,
            task="text-generation",
            max_new_tokens=512,
            do_sample=False,
            repetition_penalty=1.03,
            temperature=0.0,
            provider="auto"
        )

        return ChatHuggingFace(llm=endpoint)

    if llm_provider == "ollama":
        model_name, base_url = os.environ["LLM_MODEL"], os.environ["LLM_BASE_URL"]
        logger.info(f"[LLM INIT] Initializing Ollama model '{model_name}' at {base_url}")
        return ChatOllama(model=model_name, base_url=base_url, temperature=0)

    if llm_provider == "vllm":
        model_name = os.environ["LLM_MODEL"]
        base_url = os.environ["LLM_BASE_URL"]
        logger.info(f"[LLM INIT] Initializing vLLM model '{model_name}' at {base_url}")

        return ChatOpenAI(model=model_name, base_url=base_url, api_key="EMPTY", temperature=0, max_tokens=512)

    raise ValueError(f"Unknown LLM_PROVIDER: {llm_provider}")


# ============================================================
# 🧩 SERVICE SETUP
# ============================================================


def get_auth_service(
    sql_repo: SQLRepository = Depends(get_sql_repository),
) -> AuthService:
    """Provide an AuthService using the SQL repository."""
    return AuthService(sql_repo)


def get_course_service(
    sql_repo: SQLRepository = Depends(get_sql_repository),
    vector_repo: IVectorRepository = Depends(get_vector_repository),
) -> CourseService:
    """Provide a CourseService using the SQL repository."""
    return CourseService(sql_repo, vector_repo)


def get_instructor_service(
    sql_repo: SQLRepository = Depends(get_sql_repository),
) -> InstructorService:
    """Provide an InstructorService using the SQL repository."""
    return InstructorService(sql_repo)


def get_student_service(
    sql_repo: SQLRepository = Depends(get_sql_repository),
) -> StudentService:
    """Provide an StudentService using the SQL repository."""
    return StudentService(sql_repo)


def get_rag_service(
    vector_repo: IVectorRepository = Depends(get_vector_repository),
    sql_repo: IVectorRepository = Depends(get_sql_repository),
    loader_factory: LoaderFactory = Depends(get_loader_factory),
    rag_strategy_factory: RAGStrategyFactory = Depends(get_rag_strategy_factory),
    splitter: TextSplitter = Depends(get_splitter),
    llm: BaseChatModel = Depends(get_llm),
) -> RAGService:
    """Provide a fully configured RAGService instance."""
    return RAGService(vector_repo, sql_repo, loader_factory, rag_strategy_factory, splitter, llm)


def get_document_service(
    sql_repo: SQLRepository = Depends(get_sql_repository),
    rag_service: RAGService = Depends(get_rag_service),
) -> DocumentService:
    """Provide a DocumentService using the SQL repository and RAGService."""
    return DocumentService(sql_repo, rag_service)


def get_query_service(
    sql_repo: SQLRepository = Depends(get_sql_repository),
    rag_service: RAGService = Depends(get_rag_service),
) -> QueryService:
    """Provide a QueryService using the SQL repository and RAGService."""
    return QueryService(sql_repo, rag_service)

