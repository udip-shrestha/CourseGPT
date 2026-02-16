from typing import List, Tuple, Optional
from chromadb import EmbeddingFunction
from chromadb.api import ClientAPI
from langchain_core.documents import Document
from API.Repository.i_vector_repository import IVectorRepository


class ChromaVectorRepository(IVectorRepository):
    """
    Remote Chroma-based implementation of IVectorRepository.
    Allows dynamic embedding functions and collections per course_id.
    """

    def __init__(self, client: ClientAPI):
        self.client = client


    # ======================================================
    # COLLECTION MANAGEMENT
    # ======================================================


    def create_collection(self, course_id: str, embedding_function: Optional[EmbeddingFunction] , metric: Optional[str]) -> None:
        """
        Explicitly create a new Chroma collection for a course.
        """
        metadata = {"hnsw:space": metric} if metric else None
        self.client.create_collection(name=course_id, embedding_function=embedding_function, metadata=metadata)

    def delete_collection(self, course_id: str) -> None:
        """
        Permanently delete an entire collection (e.g., when a course is deleted).
        """
        self.client.delete_collection(name=course_id)


    # ======================================================
    # INDEXING
    # ======================================================


    def create_index(self, course_id: str, docs: List[Document]) -> None:
        """
        Dynamically embed and store the provided documents in a specific Chroma collection.
        """
        collection = self.client.get_collection(name=course_id)
        
        documents = [doc.page_content for doc in docs]
        metadatas = [doc.metadata for doc in docs]
        ids = [f"{m['doc_id']}_{i}" for i, m in enumerate(metadatas)]

        collection.add(ids=ids, documents=documents, metadatas=metadatas)

    def query(self, course_id: str, question: str, top_k: Optional[int] = 8) -> List[Tuple[Document, float]]:
        """
        Retrieve top-k similar chunks using a specific embedding function and collection.
        Returns a list of (Document, score) tuples — same format as LangChain's Chroma
        """

        
        collection = self.client.get_collection(name=course_id)
        results = collection.query(query_texts=[question], n_results=top_k)

        # Convert Chroma QueryResult → LangChain-style format
        return [
            (Document(page_content=doc, metadata=meta or {}), dist)
            for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0])
        ]

    def delete_index(self, course_id: str, document_id: str) -> None:
        """
        Delete all vectors that belong to a document from a specific Chroma collection.
        """
        collection = self.client.get_collection(name=course_id)
        collection.delete(where={"doc_id": document_id})

