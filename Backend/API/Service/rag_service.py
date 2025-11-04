from typing import Dict, List
from fastapi import HTTPException, status
from langchain_core.documents import Document
from langchain_core.language_models import BaseLanguageModel
from API.Util.loaders import Loader
from API.Util.splitters import Splitter
from API.Util.prompt_builders import PromptBuilder
from API.Repository.i_vector_repository import IVectorRepository
from API.Util.decorators import clean_service
from API.Util.formatters import clean_and_format_response


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
        prompt_builder: PromptBuilder,
        llm: BaseLanguageModel
    ):
        self.loader = loader
        self.splitter = splitter
        self.vector_repo = vector_repo
        self.prompt_builder = prompt_builder
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
    # RETRIEVAL (Retriever → Prompt → LLM)
    # ======================================================
    @clean_service
    def query(self, course_id: str, question: str) -> Dict[str, str]:
        """
        1️⃣ Retrieve relevant text chunks from vector DB.
        2️⃣ Construct a context-aware prompt using retrieved chunks.
        3️⃣ Generate an answer via the LLM.
        """
        # --- Step 1: Retrieve relevant chunks ---
        retrieved = self.vector_repo.query(course_id, question)
        # 🔍 DEBUG LOGGING: Check retrieval
        print(f"[RAG DEBUG] Retrieved {len(retrieved)} chunks for course {course_id}")
        for i, (doc, score) in enumerate(retrieved):
            print(f"[RAG DEBUG] #{i+1} Source: {getattr(doc.metadata, 'get', lambda k, d=None: doc.metadata[k] if k in doc.metadata else d)('source', 'unknown')}")
            print(f"[RAG DEBUG] Similarity Score: {score}")
            print(f"[RAG DEBUG] Preview: {doc.page_content[:200]}...\n")

        if not retrieved:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No relevant information found for this course.")

        # --- Step 2: Build context from retrieved chunks ---
        context = "\n\n".join([doc.page_content for doc, _ in retrieved])
        message = self.prompt_builder.build("DefaultLangChainRAGPrompt", context, question)

        # --- Step 3: Generate response from LLM ---
        result = self.llm.invoke(message)
        answer, sources = clean_and_format_response(result, [doc for doc, _ in retrieved])

        return {"answer": answer, "sources": sources}
