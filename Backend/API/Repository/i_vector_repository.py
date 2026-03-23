from typing import List, Tuple, Protocol, Optional
from chromadb import EmbeddingFunction
from langchain_core.documents import Document


class IVectorRepository(Protocol):
    """
    Interface for vector storage operations.
    Implementations manage course-specific vector indexes (collections),
    embedding storage, retrieval, and deletion.
    """

    # ==============================
    # COLLECTION MANAGEMENT
    # ==============================
    def create_collection(
        self,
        course_id: str,
        embedding_function: Optional[EmbeddingFunction],
        metric: str,
    ) -> None:
        """
        Create a new vector collection for a course.

        Args:
            course_id: Collection identifier.
            embedding: Embedding function to use for this collection.
            metric: Similarity metric (e.g., 'cosine', 'l2', 'ip').
        """
        ...

    def delete_collection(
        self,
        course_id: str,
    ) -> None:
        """
        Delete an entire collection.

        Args:
            course_id: Identifier of the collection to delete.
        """
        ...

    # ==============================
    # INDEXING
    # ==============================
    def create_index(
        self,
        course_id: str,
        docs: List[Document],
    ) -> None:
        """
        Add documents to an existing collection.
        The embedding function is already bound to the collection.

        Args:
            course_id: Target collection.
            docs: List of Documents to index.
        """
        ...

    def delete_index(
        self,
        course_id: str,
        document_id: str,
    ) -> None:
        """
        Remove all vector entries belonging to a specific document.

        Args:
            course_id: Collection identifier.
            document_id: The logical document ID (stored in metadata).
        """
        ...

    # ==============================
    # QUERYING
    # ==============================
    def query(
        self,
        course_id: str,
        question: str,
        top_k: Optional[int],
        distance_cutoff: Optional[float],
    ) -> List[Tuple[str, Document]]:
        """
        Retrieve top-k matching Documents with their similarity distance.

        Args:
            course_id: Collection identifier.
            query_text: Text to search for.
            top_k: Number of results to return.

        Returns:
            List of (Document, distance) sorted ascending (smaller = closer).
        """
        ...
