from typing import Dict, List, Optional
from fastapi import HTTPException, status
from langchain_core.documents import Document
from langchain_core.language_models import BaseChatModel
from API.Util.loaders import Loader
from API.Util.splitters import Splitter
from API.Util.rag_strategy import RAGStrategyFactory
from API.Repository.i_vector_repository import IVectorRepository
from API.Repository.i_sql_repository import ISQLRepository
from API.Util.decorators import clean_service


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
        loader: Loader,
        splitter: Splitter,
        vector_repo: IVectorRepository,
        sql_repo: ISQLRepository,
        rag_strategy_factory: RAGStrategyFactory,
        llm: BaseChatModel
    ):
        self.loader = loader
        self.splitter = splitter
        self.vector_repo = vector_repo
        self.sql_repo = sql_repo
        self.rag_strategy_factory = rag_strategy_factory
        self.llm = llm

    # ======================================================
    # INDEXING (Loader → Splitter → Vector Store)
    # ======================================================
    @clean_service
    def create_index(self, course_id: str, doc_id: str, splitter_type: str, file_name: str, file_type: str, file_bytes: bytes) -> List[Document]:
        """
        Ingest a file and build a vector index for retrieval.

        Steps:
          1. Load → 2. Split → 3. Store (embedding handled automatically by Chroma)
        """
        # 1. Load
        docs = self.loader.load(file_name, file_type, file_bytes)
        if not docs:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="No text extracted from file. Please upload a valid document.")

        # 2. Split
        chunks = self.splitter.split(splitter_type, docs)
        
        for chunk in chunks:
            chunk.metadata["doc_id"] = doc_id

        # 3. Store
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

    # ======================================================
    # RETRIEVAL
    # ======================================================
    @clean_service
    def query(self, course_id: str, course: dict, student_id: Optional[int], question: str) -> Dict[str, str]:
        rag_strategy_id = course["rag_strategy_id"]

        rag_strategy = self.rag_strategy_factory.get(str(rag_strategy_id))
        result = rag_strategy.run(self.vector_repo, self.sql_repo, self.llm, course_id, course, student_id, question)

        if not result:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No relevant information found for this course.")

        return result
