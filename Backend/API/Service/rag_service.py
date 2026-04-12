from typing import Dict, List, Optional
from fastapi import HTTPException, status
from langchain_core.documents import Document
from langchain_core.language_models import BaseChatModel
from langchain_text_splitters import TextSplitter
from API.Util.loaders import ImageLoader, LoaderFactory
from API.Util.rag_strategy import RAGStrategyFactory
from API.Repository.i_vector_repository import IVectorRepository
from API.Repository.i_sql_repository import ISQLRepository
from API.Util.decorators import clean_service

from uuid import uuid4
from datetime import datetime


class RAGService:
    """
    Full Retrieval-Augmented Generation (RAG) pipeline orchestrator.

    Methods:
      • create_index() → Loads, splits, and stores document chunks in the vector store.
      • delete_index() → Removes all vectors linked to a specific document or course.
      • query()        → RAG.
    """

    def __init__(
        self,
        vector_repo: IVectorRepository,
        sql_repo: ISQLRepository,
        loader_factory: LoaderFactory,
        rag_strategy_factory: RAGStrategyFactory,
        splitter: TextSplitter,
        llm: BaseChatModel
    ):
        self.vector_repo = vector_repo
        self.sql_repo = sql_repo
        self.loader_factory = loader_factory
        self.rag_strategy_factory = rag_strategy_factory
        self.splitter = splitter
        self.llm = llm

    # ======================================================
    # INDEXING (Loader → Splitter → Vector Store)
    # ======================================================
    @clean_service
    def create_index(self, course_id: str, doc_id: str, file_name: str, mime_type: str, file_bytes: bytes) -> List[Document]:
        """
        Ingest a file and build a vector index for retrieval.

        Steps:
          1. Load → 2. Split → 3. Store (embedding handled automatically by Chroma)
        """
        # 1. Load
        loader = self.loader_factory.get(mime_type)
        docs = loader.load(file_name, file_bytes)
        if not docs:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="No text extracted from file. Please upload a valid document.")

        # 2. Split
        chunks = self.splitter.split_documents(docs)
        for chunk in chunks:
            chunk.metadata.update({
                "chunk_id": str(uuid4()),        # Unique per chunk
                "doc_id": str(doc_id),           # Already there but normalize
                "course_id": str(course_id),     # Helpful for filtering
                "title": file_name,              # REQUIRED FOR SOURCES
                "source_type": mime_type,        # Optional but recommended
                "date": datetime.utcnow().isoformat()
            })

        # 3. Delete old vectors for this document (if any)
        self.vector_repo.delete_index(course_id, str(doc_id))

        # 4. Store new vectors
        self.vector_repo.create_index(course_id, chunks)

        return chunks

    # ======================================================
    # DELETION (Vector Cleanup)
    # ======================================================
    @clean_service
    def delete_index(self, course_id: str, doc_id: str) -> None:
        """
        Deletes all vector entries associated with a given document within a course.
        """
        self.vector_repo.delete_index(course_id, doc_id)

    @clean_service
    def extract_image_context(self, file_name: str, mime_type: str, file_bytes: bytes) -> str:
        """Extract readable text from a transient chat image attachment."""
        supported_types = {"image/png", "image/jpeg", "image/jpg"}
        if mime_type not in supported_types:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="Unsupported image type. Please upload a PNG or JPEG image.",
            )

        docs = ImageLoader().load(file_name, file_bytes)
        extracted_text = "\n\n".join(doc.page_content.strip() for doc in docs if doc.page_content.strip())
        if not extracted_text:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="No readable text could be extracted from the uploaded image.",
            )

        return extracted_text

    # ======================================================
    # RETRIEVAL
    # ======================================================
    @clean_service
    def query(
        self,
        course_id: str,
        course: dict,
        question: str,
        validate: bool = False,
        student_id: Optional[str] = None,
        image_context: Optional[str] = None,
        image_name: Optional[str] = None,
    ) -> Dict[str, str]:
        rag_strategy_id = course["rag_strategy_id"]

        rag_strategy = self.rag_strategy_factory.get(str(rag_strategy_id))
        result = rag_strategy.run(
            self.vector_repo,
            self.sql_repo,
            self.llm,
            course_id,
            course,
            question,
            validate,
            student_id,
            image_context=image_context,
            image_name=image_name,
        )

        if not result:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No relevant information found for this course.")

        return result
