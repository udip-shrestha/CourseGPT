from functools import lru_cache
import os, platform, json
from chromadb import Client, PersistentClient
from fastapi.security import OAuth2PasswordBearer
from langchain_core.language_models import BaseLanguageModel
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from langchain_huggingface import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from huggingface_hub import InferenceClient
from langchain.llms.base import LLM
from typing import Optional, List, Any
from pydantic import BaseModel
from jwt import ExpiredSignatureError, PyJWTError

from langchain_community.llms import Ollama
from API.Repository.sql_repository import SQLRepository
from API.Repository.postgres_connection_manager import PostgresConnectionManager
from API.Service.document_service import DocumentService
from API.Service.auth_service import AuthService
from API.Service.rag_service import RAGService
from API.Service.courses_service import CourseService
from API.Service.instructors_service import InstructorService
from API.Service.students_service import StudentService
from API.Repository.i_vector_repository import IVectorRepository
from API.Repository.chroma_vector_repository import ChromaVectorRepository
from API.Util.loaders import Loader
from API.Util.splitters import Splitter
from API.Util.prompt_builders import PromptBuilder
from API.Util.auth import decrypt_access_token

from langchain_community.llms import Ollama


load_dotenv()


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
    chroma_dir = os.environ["CHROMA_DATA_PATH"]
    return PersistentClient(path=chroma_dir)


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
        raise HTTPException(status_code=401, detail="Missing authorization token", headers={"WWW-Authenticate": "Bearer"})

    payload = decrypt_access_token(token)
    token_instructor_id = payload.get("id")
    if not token_instructor_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload", headers={"WWW-Authenticate": "Bearer"})

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


def authorize_course(
    course_id: str,
    auth: dict = Depends(authorize),
    sql_repo: SQLRepository = Depends(get_sql_repository),
) -> dict:
    """Authorize access to a course based on instructor ownership or ADMIN role."""
    course = sql_repo.read_course(course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    if auth["role"] != "ADMIN" and course["instructor_id"] != auth["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this course")

    return course


# ============================================================
# 🧠 LLM  SETUP
# ============================================================


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
