from functools import lru_cache
import os, platform
from chromadb import Client, PersistentClient
from langchain_core.language_models import BaseLanguageModel
from dotenv import load_dotenv
from fastapi import Depends
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from langchain_huggingface import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from huggingface_hub import InferenceClient
from langchain.llms.base import LLM
from typing import Optional, List, Any
from pydantic import BaseModel

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

# Custom LangChain-compatible wrapper
class HuggingFaceScoutLLM(LLM):
    """Custom LangChain-compatible wrapper for Hugging Face Llama 4 Scout."""
    model_id: str = os.getenv("LLM_MODEL", "meta-llama/Llama-4-Scout-17B-16E-Instruct")
    token: Optional[str] = os.getenv("HUGGINGFACE_TOKEN")

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        client = InferenceClient(model=self.model_id, token=self.token)

        response = client.chat.completions.create(
            model=self.model_id,
            messages=[
                {"role": "system", "content": "You are a helpful and concise assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.5,
        )

        return response.choices[0].message.content

    @property
    def _llm_type(self) -> str:
        return "huggingface-scout"


@lru_cache()
def get_llm() -> LLM:
    """Use Hugging Face Inference API for Llama 4 Scout (no local download)."""
    llm_instance = HuggingFaceScoutLLM()
    print(f"[LLM INIT] Loaded model: {llm_instance.model_id}")
    return llm_instance

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
