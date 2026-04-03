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
        collection = self.client.get_collection(name=course_id)

        documents = []
        metadatas = []
        ids = []

        for i, doc in enumerate(docs):
            metadata = doc.metadata.copy()

            # Build id using doc_id
            doc_id = metadata.get("doc_id", "doc")
            chunk_id = f"{doc_id}_{i}"

            documents.append(doc.page_content)
            metadatas.append(metadata)   
            ids.append(chunk_id)

        collection.add(ids=ids, documents=documents, metadatas=metadatas)

    def _query_neighbors(self, collection, hits: List[Tuple[str, Document]]) -> List[Tuple[str, Document]]:
        seen_ids = {chunk_id for chunk_id, _ in hits}

        def get_neighbor_ids(chunk_id: str) -> List[str]:
            parts = chunk_id.rsplit("_", 1)
            if len(parts) != 2 or not parts[1].isdigit():
                return []
            doc_id, idx = parts[0], int(parts[1])
            return [f"{doc_id}_{neighbor_idx}" for neighbor_idx in (idx - 1, idx + 1)]

        neighbor_ids = [
            neighbor_id
            for chunk_id, _ in hits
            for neighbor_id in get_neighbor_ids(chunk_id)
            if neighbor_id not in seen_ids and not seen_ids.add(neighbor_id)
        ]

        if not neighbor_ids:
            return []
        
        neighbor_results = collection.get(ids=neighbor_ids, include=["documents", "metadatas"])
        return [
            (chunk_id, Document(page_content=doc_text, metadata=meta or {}))
            for chunk_id, doc_text, meta in zip(neighbor_results["ids"], neighbor_results["documents"], neighbor_results["metadatas"],)
        ]

    def query(self, course_id: str, question: str, top_k: Optional[int] = 8, distance_cutoff: Optional[float] = 1.5, file_name: list[str] | None = None) -> List[Tuple[str, Document]]:
        """
        Retrieve top-k similar chunks using a specific embedding function and collection.
        Returns a list of (Document, score) tuples — same format as LangChain's Chroma
        """
        collection = self.client.get_collection(name=course_id)
        where = {"$or": [{"source": s} for s in file_name]} if file_name else None
        results = collection.query(query_texts=[question], n_results=top_k, where=where)

        # Convert Chroma QueryResult → LangChain-style format
        hits = [
            (chunk_id, Document(page_content=doc, metadata=meta or {}))
            for chunk_id, doc, meta, dist in zip(results["ids"][0], results["documents"][0], results["metadatas"][0], results["distances"][0])
            if dist < distance_cutoff
        ]


        hits.extend(self._query_neighbors(collection,  hits))
        hits.sort(key=lambda item: (
            item[0].rsplit("_", 1)[0],                                         # doc_id
            int(item[0].rsplit("_", 1)[1]) if item[0].rsplit("_", 1)[1].isdigit() else 0  # chunk index
        ))

        return hits

    def delete_index(self, course_id: str, document_id: str) -> None:
        """
        Deletes vectors belonging to a document.
        Safe even if collection does not exist.
        """

        from chromadb.errors import NotFoundError

        try:
            collection = self.client.get_collection(name=course_id)
            collection.delete(where={"doc_id": document_id})
        except NotFoundError:
            # Collection does not exist → nothing to delete
            pass
