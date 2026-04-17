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

    def count_documents(self) -> int:
        """Return total number of documents."""
        ...

    def count_documents_grouped_by_course(self) -> Dict[str, int]:
        """Return document counts grouped by course_id."""
        ...

    # ======================================================
    # INSTRUCTORS
    # ======================================================
    def create_instructor(
        self,
        name: str,
        title: str,
        university: str,
        email: str,
        encrypted_password: str,
        role_name: str = "INSTRUCTOR"
    ) -> str:
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
        role: Optional[int] = None,
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

    def update_instructor_password(self, instructor_id: str, encrypted_password: str) -> None:
        """Update an instructor password."""
        ...

    def update_instructor_admin(self, instructor_id: str, is_admin: bool) -> None:
        """Toggle an instructor admin role."""
        ...

    # ======================================================
    # PASSWORD RESET CODES
    # ======================================================
    def create_password_reset_code(self, instructor_id: str, code: str) -> None:
        """Create or replace a password reset code."""
        ...

    def read_password_reset_code(self, instructor_id: str) -> Optional[dict]:
        """Read a valid password reset code for an instructor."""
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
        instructor_email: Optional[str] = None,
        institution: Optional[str] = None,
        name: Optional[str] = None,
        semester_id: Optional[int] = None,
        rag_strategy_id: Optional[int] = None,
        status: Optional[str] = None,
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

    def read_course_by_canvas_id(self, canvas_course_id: str) -> Optional[dict]:
        """Find a course by its linked Canvas course identifier."""
        ...

    def update_course(self, course_id: str, updates: dict) -> dict:
        """Update course fields."""
        ...

    def count_courses(self) -> int:
        """Return total number of courses."""
        ...

    def count_courses_grouped_by_instructor(self) -> Dict[str, int]:
        """Return course counts grouped by instructor_id."""
        ...

    def update_course_status(self, course_id: str, enabled: bool) -> None:
        """Update a course status to ENABLED or DISABLED."""
        ...

    # ======================================================
    # STUDENTS
    # ======================================================
    def create_student(
        self,
        name: str,
        discord_id: Optional[str],
        course_id: str,
        canvas_user_id: Optional[str] = None,
    ) -> str:
        """Create a student and register them for a course."""
        ...

    def read_student(self, student_id: str) -> Optional[dict]:
        """Read a student record by ID."""
        ...

    def read_student_by_canvas(self, canvas_user_id: str) -> Optional[dict]:
        """Retrieve a student record by their Canvas user id."""
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

    # ======================================================
    # FEEDBACK
    # ======================================================
    def create_feedback(self, course_id: str, feedback_text: str, received_at: Optional[str] = None) -> str:
        """Insert a feedback record and return its id."""
        ...

    def read_all_feedback(
        self,
        limit: int = 50,
        offset: int = 0,
        order_by: str = "received_at",
        order_dir: str = "desc"
    ) -> dict:
        """Return all feedback in the system with pagination."""
        ...

    def read_all_feedback_for_course(
        self,
        course_id: str,
        limit: int = 50,
        offset: int = 0,
        order_by: str = "received_at",
        order_dir: str = "desc"
    ) -> dict:
        """Return all feedback for a specific course with pagination."""
        ...

    def create_answer_feedback(
        self,
        course_id: str,
        student_id: str,
        query_id: str,
        vote: str,
    ) -> str:
        """Insert an answer feedback vote and return its id."""
        ...

    def read_course_satisfaction(self, course_id: str) -> dict:
        """Return satisfaction metrics for a course based on answer_feedback."""
        ...

    # ======================================================
    # DISCORD ADMINS
    # ======================================================
    def create_discord_admin(self, discord_id: str) -> str:
        """Insert a new Discord admin and return its id."""
        ...

    def read_discord_admin(self, discord_id: str) -> Optional[Dict[str, Any]]:
        """Return a Discord admin by discord_id."""
        ...

    def read_all_discord_admins(self, limit: int = 50, offset: int = 0) -> dict:
        """Return all Discord admins with pagination."""
        ...

    def delete_discord_admin(self, discord_id: str) -> None:
        """Delete a Discord admin by discord_id."""
        ...

    # ======================================================
    # ANALYTICS
    # ======================================================
        
    def read_course_query_stats(
        self, course_id: str, days: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        ...

    def read_top_questions(
        self, course_id: str, limit: int, days: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        ...

    def read_top_keywords(
        self, course_id: str, limit: int, days: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        ...

    def read_engagement_stats(
        self, course_id: str
    ) -> Dict[str, Any]:
        ...

    def read_course_usage_trend(
        self, course_id: str, days: int
    ) -> List[Dict[str, Any]]:
        ...

    def read_instructor_query_distribution(
        self, instructor_id: str, days: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        ...

    def read_system_overview(self) -> Dict[str, Any]:
        ...

    def read_system_query_trend(
        self, days: int
    ) -> List[Dict[str, Any]]:
        ...

    def read_documents_per_course(self) -> List[Dict[str, Any]]:
        ...

    def read_documents_per_instructor(self) -> List[Dict[str, Any]]:
        ...

    def read_courses_per_instructor(self) -> List[Dict[str, Any]]:
        ...

    def read_queries_per_course(
        self, days: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        ...
