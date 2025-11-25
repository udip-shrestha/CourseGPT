from typing import Protocol, List, Dict, Any, Optional

class ISQLRepository(Protocol):
    """Interface defining all SQL repository operations."""

    # ======================================================
    # FILE TYPES
    # ======================================================
    def read_file_type_by_mime(self, mime_type: str) -> Optional[Dict[str, Any]]:
        """Return the file type matching a MIME type."""
        ...

    def read_all_file_types(self) -> List[Dict[str, Any]]:
        """Return all file types."""
        ...

    # ======================================================
    # RAG STRATEGIES
    # ======================================================
    def read_rag_strategy_by_type(self, type_name: str) -> Optional[Dict[str, Any]]:
        """Return a rag strategy by its type name."""
        ...

    def read_all_rag_strategies(self) -> List[Dict[str, Any]]:
        """Return all rag strategies."""
        ...

    # ======================================================
    # DOCUMENTS
    # ======================================================
    def create_document(self, course_id: str, file_name: str, file_bytes: bytes, file_type_id: str) -> str:
        """Insert a new document and return its ID."""
        ...

    def read_document(self, course_id: str, doc_id: str) -> Optional[dict]:
        """Read a single document (file + metadata)."""
        ...

    def delete_document(self, course_id: str, doc_id: str) -> None:
        """Delete a document by ID."""
        ...

    def read_all_documents(
        self,
        course_id: str,
        file_type_id: Optional[str] = None,
        file_name: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
        order_by: str = "uploaded_at",
        order_dir: str = "desc"
    ) -> dict:
        """Return paginated, filtered documents."""
        ...
  
    def update_document_processing_status_completed(self, doc_id: str) -> None:
        """Mark a document's processing_status as COMPLETED."""
        ...

    def update_document_processing_status_failed(self, doc_id: str) -> None:
        """Mark a document's processing_status as FAILED."""
        ...

    # ======================================================
    # COURSES
    # ======================================================
    def create_course(
        self,
        instructor_id: str,
        name: str,
        institution: str,
        semester_id: int,
        year: int,
        rag_strategy_id: Optional[int] = None
    ) -> str:
        """Create a new course record."""
        ...

    def read_course(self, course_id: str) -> Optional[dict]:
        """Retrieve a course by ID."""
        ...

    def read_course_by_name(self, name: str, instructor_id: str) -> Optional[dict]:
        """Return a course owned by a specific instructor with a matching name."""
        ...

    def read_all_courses(
        self,
        instructor_id: Optional[str] = None,
        institution: Optional[str] = None,
        name: Optional[str] = None,
        semester_id: Optional[int] = None,
        rag_strategy_id: Optional[int] = None,
        limit: int = 10,
        offset: int = 0,
        order_by: str = "created_at",
        order_dir: str = "desc"
    ) -> dict:
        """Return all courses with filtering + pagination."""
        ...

    def delete_course(self, course_id: str) -> None:
        """Delete a course by ID."""
        ...

    def get_course_by_name(self, course_name: str) -> Optional[dict]:
        """Return a course by its exact name."""
        ...

    def update_course(self, course_id: str, updates: dict) -> dict:
        """Update course fields."""
        ...

    # ======================================================
    # INSTRUCTORS
    # ======================================================
    def create_instructor(self, name: str, title: str, university: str, email: str, encrypted_password: str) -> str:
        """Create a new instructor."""
        ...

    def read_instructor(self, instructor_id: str) -> Optional[dict]:
        """Read an instructor by ID."""
        ...

    def read_instructor_by_email(self, email: str) -> Optional[dict]:
        """Read an instructor by email."""
        ...

    def read_all_instructors(
        self,
        name: Optional[str] = None,
        title: Optional[str] = None,
        university: Optional[str] = None,
        email: Optional[str] = None,
        role: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
        order_by: str = "created_at",
        order_dir: str = "desc"
    ) -> dict:
        """Return all instructors with filtering + pagination."""
        ...

    def delete_instructor(self, instructor_id: str) -> None:
        """Delete an instructor by ID."""
        ...

    def update_instructor(self, instructor_id: str, updates: dict) -> dict:
        """Update instructor fields."""
        ...

    # ======================================================
    # STUDENTS
    # ======================================================
    def create_student(self, name: str, discord_id: str, course_id: str) -> str:
        """Create a student and register them for a course."""
        ...

    def read_student(self, student_id: str) -> Optional[dict]:
        """Read a student record by ID."""
        ...

    def read_all_students(self, course_id: Optional[str] = None) -> List[dict]:
        """Return all students, optionally filtered by course."""
        ...

    def delete_student(self, student_id: str) -> None:
        """Delete a student + remove links."""
        ...

    def read_student_by_discord(self, discord_id: str) -> Optional[dict]:
        """Return a student by Discord ID."""
        ...

    def read_courses_by_discord(self, discord_id: str) -> List[dict]:
        """Return all courses a Discord user is registered in."""
        ...

    def remove_student_from_course(self, student_id: str, course_id: str) -> bool:
        """Remove a student from a course."""
        ...

    # ======================================================
    # QUERIES
    # ======================================================
    def create_query(self, student_id: Optional[str], course_id: str, query_text: str, response_text: Optional[str]) -> str:
        """Create a query + response pair."""
        ...

    def read_query(self, course_id: str, query_id: str) -> Optional[dict]:
        """Return a single query."""
        ...

    def read_queries_for_student_course(
        self,
        student_id: str,
        course_id: str,
        limit: int = 10,
        offset: int = 0,
        order_by: str = "asked_at",
        order_dir: str = "desc"
    ) -> dict:
        """Return paginated queries for a specific student in a course."""
        ...

    def read_all_queries_for_course(
        self,
        course_id: str,
        limit: int = 10,
        offset: int = 0,
        order_by: str = "asked_at",
        order_dir: str = "desc"
    ) -> dict:
        """Return all queries for a course."""
        ...

    def delete_query(self, course_id: str, query_id: str) -> None:
        """Delete a query by ID."""
        ...
