from typing import List

from langchain_core.documents import Document
from chromadb import EmbeddingFunction

from API.Util.loaders import Loader
from API.Util.splitters import Splitter
from API.Repository.i_vector_repository import IVectorRepository
from API.Util.decorators import clean_service


class RAGService:
    """
    Full Retrieval-Augmented Generation (RAG) pipeline orchestrator.

    Methods:
      • create_index() → Loads, splits, and stores document chunks in the vector store.
      • delete_index() → Removes all vectors linked to a specific document or course.
      • query()        → Retrieves relevant chunks, builds a prompt, and generates a response.
    """

    def __init__(
        self,
        loader: Loader,
        splitter: Splitter,
        vector_repo: IVectorRepository,
    ):
        self.loader = loader
        self.splitter = splitter
        self.vector_repo = vector_repo

    # ======================================================
    # INDEXING (Loader → Splitter → Vector Store)
    # ======================================================
    @clean_service
    def create_index(self, course_id: str, doc_id: str, splitter_type: str, file_type: str, file_bytes: bytes) -> List[Document]:
        """
        Ingest a file and build a vector index for retrieval.

        Steps:
          1. Load → 2. Split → 3. Store (embedding handled automatically by Chroma)
        """
        # 1. Load
        docs = self.loader.load(file_type, file_bytes)
        if not docs:
            raise ValueError("No text extracted from file.")

        # 2. Split
        chunks = self.splitter.split(splitter_type, docs)
        
        for chunk in chunks:
            chunk.metadata["doc_id"] = doc_id

        # 3. Store
        self.vector_repo.create_index(course_id, chunks)

        return chunks

    @clean_service
    def delete_index(self, course_id: str, document_id: str) -> None:
        """Delete all vectors associated with a specific document."""
        self.vector_repo.delete_index(course_id, document_id)

    # ======================================================
    # RETRIEVAL (Retriever → Prompt → LLM)
    # ======================================================
    @clean_service
    def query(self, course_id: str, query_text: str) -> str:
        """Full RAG pipeline: retrieve → build prompt → generate response."""
        pass
