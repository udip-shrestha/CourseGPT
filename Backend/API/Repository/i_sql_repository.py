from typing import Protocol, List, Dict, Any, Optional

class ISQLRepository(Protocol):
    """Interface defining all SQL repository operations."""

    # ======================================================
    # FILE TYPES
    # ======================================================
    def read_file_type_by_mime(self, mime_type: str) -> Optional[Dict[str, Any]]:
        """Return the file type record (id, mime_type, extension) matching a MIME type."""
        ...

    def read_file_type_by_extension(self, extension: str) -> Optional[Dict[str, Any]]:
        """Return the file type record (id, mime_type, extension) matching a file extension."""
        ...

    # ======================================================
    # DOCUMENTS
    # ======================================================
    def create_document(self, course_id: str, file_name: str, file_bytes: bytes, file_type_id: str) -> str:
        """Save a single uploaded file (binary) in SQL DB and return its document ID."""
        ...

    def read_document(self, doc_id: str) -> Optional[dict]:
        """Retrieve a file record by document ID."""
        ...

    def delete_document(self, doc_id: str) -> None:
        """Delete a file record by its ID."""
        ...

    def read_all_documents(
        self,
        course_id: str,
        file_type_id: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
        order_by: str = "uploaded_at",
        order_dir: str = "desc"
    ) -> List[dict]:
        """Retrieve files with pagination, optional filters, and sorting."""
        ...


