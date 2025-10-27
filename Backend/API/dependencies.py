from functools import lru_cache
import os, platform
from chromadb import Client, PersistentClient
from langchain_core.language_models import BaseLanguageModel
from dotenv import load_dotenv
from fastapi import Depends
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from langchain_huggingface import HuggingFacePipeline

from langchain_community.llms import Ollama
from API.Repository.sql_repository import SQLRepository
from API.Repository.postgres_connection_manager import PostgresConnectionManager
from API.Service.document_service import DocumentService
from API.Service.rag_service import RAGService
from API.Service.courses_service import CourseService
from API.Service.instructors_service import InstructorService
from API.Repository.i_vector_repository import IVectorRepository
from API.Repository.chroma_vector_repository import ChromaVectorRepository
from API.Util.loaders import Loader
from API.Util.splitters import Splitter
from API.Util.prompt_builders import PromptBuilder

from langchain_community.llms import Ollama


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


def get_chroma_client() -> Client:
    """Create and return a persistent Chroma client."""
    chroma_dir = os.environ["CHROMA_DATA_PATH"]
    return PersistentClient(path=chroma_dir)


def get_vector_repository(
    client: Client = Depends(get_chroma_client),
) -> IVectorRepository:
    """Provide a Chroma-based vector repository instance."""
    return ChromaVectorRepository(client)


@lru_cache
def get_loader() -> Loader:
    """Return a Singleton Loader instance for document parsing."""
    return Loader()


@lru_cache
def get_splitter() -> Splitter:
    """Return a Singleton Splitter instance for document chunking."""
    return Splitter()

@lru_cache()
def get_prompt_builder() -> PromptBuilder:
    """Return a Singleton PromptBuilder instance."""
    return PromptBuilder()

@lru_cache()
def get_llm() -> BaseLanguageModel:
    """
    Load and return the Llama Scout 4 model via Ollama.
    Uses environment variables defined in .env:
      - LLM_MODEL
      - LLM_BASE_URL
    """
    model_name = os.getenv("LLM_MODEL", "llama-scout-4")
    base_url = os.getenv("LLM_BASE_URL", "http://localhost:11434")

    llm = Ollama(
        model=model_name,
        base_url=base_url,
    )

    return llm

    return HuggingFacePipeline(pipeline=hf_pipeline)

def get_document_service(
    sql_repo: SQLRepository = Depends(get_sql_repository),
) -> DocumentService:
    """Provide a DocumentService using the SQL repository."""
    return DocumentService(sql_repo)

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


def get_rag_service(
    loader: Loader = Depends(get_loader),
    splitter: Splitter = Depends(get_splitter),
    vector_repo: IVectorRepository = Depends(get_vector_repository),
    prompt_builder: PromptBuilder = Depends(get_prompt_builder),
    llm: BaseLanguageModel = Depends(get_llm),
) -> RAGService:
    """Provide a fully configured RAGService instance."""
    return RAGService(loader, splitter, vector_repo, prompt_builder, llm)


def get_document_service(
    sql_repo: SQLRepository = Depends(get_sql_repository),
    rag_service: RAGService = Depends(get_rag_service),
) -> DocumentService:
    """Provide a DocumentService using the SQL repository and RAGService."""
    return DocumentService(sql_repo, rag_service)
