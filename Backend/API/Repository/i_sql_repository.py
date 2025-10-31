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

    # ======================================================
    # COURSES
    # ======================================================
    def create_course(self, instructor_id: str, name: str, institution: str, semester_id: int, year: int) -> str:
        """Create a new course record."""
    ...

    def read_course(self, course_id: str) -> Optional[dict]:
        """Retrieve a course record by ID."""
        ...

    def read_all_courses(self, instructor_id: Optional[str] = None) -> List[dict]:
        """Retrieve all courses, optionally filtered by instructor."""
        ...

    def delete_course(self, course_id: str) -> None:
        """Delete a course record by ID."""
        ...

    # ======================================================
    # INSTRUCTORS
    # ======================================================
    def create_instructor(self, name: str, title: str, university: str, email: str) -> str:
        """Add a new instructor."""
        ...

    def read_instructor(self, instructor_id: str) -> Optional[dict]:
        """Retrieve an instructor by ID."""
        ...

    def read_instructor_by_email(self, email: str) -> Optional[dict]:
        """Retrieve an instructor by Email."""
        ...

    def read_all_instructors(
        self, 
        name: Optional[str] = None, 
        title: Optional[str] = None, 
        university: Optional[str] = None,
        email: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
        order_by: str = "created_at",
        order_dir: str = "desc"
    ) -> List[dict]:
        """Retrieve all instructors."""
        ...

    def delete_instructor(self, instructor_id: str) -> Optional[dict]:
        """Delete an instructor by ID."""
        ...

    # ======================================================
    # STUDENTS
    # ======================================================
    def create_student(self, name: str, discord_id: str, course_id: str) -> str:
        """Add a new student."""
        ...

    def read_student(self, student_id: str) -> Optional[dict]:
        """Retrieve an student by ID."""
        ...

    def read_all_students(self, course_id: Optional[str] = None) -> List[dict]:
        """Retrieve all students, optionally filtered by course_id."""
        ...

    def delete_student(self, student_id: str) -> Optional[dict]:
        """Delete an student by ID."""
        ...