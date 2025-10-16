from fastapi import HTTPException, status
from typing import List, Optional
from langchain_core.documents import Document

from API.Repository.i_sql_repository import ISQLRepository
from API.Util.decorators import clean_service


class DocumentService:
    """
    Handles document storage and retrieval across:
      1️⃣ SQL (for binary/original files)
      2️⃣ Vector store (for semantic search)
    """

    def __init__(
        self,
        sql_repo: ISQLRepository
    ):
        self.sql_repo = sql_repo

    @clean_service
    def create_document(self, course_id: str, file_name: str, file_bytes: bytes, mime_type: str):
        """
        1️⃣ Determine file type and save original file in SQL.
        2️⃣ Extract and split file text into chunks.
        3️⃣ Store chunks in vector DB for semantic search.
        """
        # --- Step 1: Resolve file type ---
        file_type = self.sql_repo.read_file_type_by_mime(mime_type)
        if not file_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported MIME type: {mime_type}"
            )

        file_type_id = file_type["id"]

        # --- Step 2: Save file in SQL ---
        doc_id = self.sql_repo.create_document(course_id, file_name, file_bytes, file_type_id)

        return {"doc_id": doc_id}

    @clean_service
    def read_document(self, course_id: str, doc_id: str) -> dict:
        """Fetch one document by ID."""
        doc = self.sql_repo.read_document(doc_id)
        
        if not doc or doc["course_id"] != course_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with id={doc_id} not found."
            )

        return doc

    @clean_service
    def read_all_documents(
        self,
        course_id: str,
        file_type: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
        order_by: str = "uploaded_at",
        order_dir: str = "desc"
    ) -> List[dict]:
        """Fetch all uploaded documents with pagination and filters."""

        file_type_id = None
        # If a MIME type is provided, translate it to its numeric ID
        if file_type:
            ft_record = self.sql_repo.read_file_type_by_mime(file_type)
            if ft_record:
                file_type_id = ft_record.get("id")
            else:
                # If MIME type not found → return a clear HTTP 404 error
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"File type '{file_type}' not found in file_types table."
                )

        return self.sql_repo.read_all_documents(
            course_id=course_id,
            file_type_id=file_type_id,
            limit=limit,
            offset=offset,
            order_by=order_by,
            order_dir=order_dir,
        )

    @clean_service
    def search_documents(self, course_id: str, query: str, top_k: int = 3) -> List[Document]:
        """TODO: Perform semantic vector search within one course."""
        pass

    @clean_service
    def delete_document(self, course_id: str, doc_id: str):
        """
        Remove a document from both SQL and vector stores.
        Keeps systems consistent.
        """
        self.sql_repo.delete_document(doc_id)

        return {"status": "deleted", "course_id": course_id, "doc_id": doc_id}