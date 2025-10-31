import base64
from typing import Optional, List, Dict, Any
from API.Repository.postgres_connection_manager import PostgresConnectionManager


class SQLRepository:
    """
    Central repository for all SQL-based database interactions.
    Each method corresponds to a specific domain (documents, courses, etc.).
    """

    def __init__(self, cm: PostgresConnectionManager):
        self.cm = cm

    # ======================================================
    # FILE TYPES
    # ======================================================
    def read_file_type_by_mime(self, mime_type: str) -> Optional[Dict[str, Any]]:
        sql = """
            SELECT *
            FROM file_types
            WHERE mime_type = %s;
        """
        return self.cm.select_one(sql, (mime_type,))

    def read_file_type_by_extension(self, extension: str) -> Optional[Dict[str, Any]]:
        sql = """
            SELECT *
            FROM file_types
            WHERE extension = %s;
        """
        return self.cm.select_one(sql, (extension,))

    def read_all_file_types(self) -> List[Dict[str, Any]]:
        sql = """
            SELECT * 
            FROM file_types;
        """
        return self.cm.select_all(sql)

    # ======================================================
    # DOCUMENTS
    # ======================================================
    def create_document(self, course_id: str, file_name: str, file_bytes: bytes, file_type_id: str) -> str:
        sql = """
            INSERT INTO documents (course_id, file_name, file_data, file_type_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """
        return self.cm.insert_one(sql, (course_id, file_name, file_bytes, file_type_id))

    def read_document(self, doc_id: str) -> Optional[dict]:
        sql = """
            SELECT 
                d.id,
                d.course_id,
                d.file_name,
                d.file_data,
                ft.mime_type,
                ft.extension,
                d.uploaded_at
            FROM documents d
            LEFT JOIN file_types ft ON d.file_type_id = ft.id
            WHERE d.id = %s;
        """

        row = self.cm.select_one(sql, (doc_id,))

        if not row:
            return None

        # Encode BYTEA → Base64 string
        if row.get("file_data") is not None:
            row["file_data"] = base64.b64encode(row["file_data"]).decode("utf-8")

        return row

    def delete_document(self, doc_id: str) -> None:
        sql = "DELETE FROM documents WHERE id = %s;"
        self.cm.execute(sql, (doc_id,))

    def read_all_documents(
        self,
        course_id: str,
        file_type_id: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
        order_by: str = "uploaded_at",
        order_dir: str = "desc",
    ) -> List[dict]:
        filters = ["course_id = %s"]
        params = [course_id]

        if file_type_id:
            filters.append("file_type_id = %s")
            params.append(file_type_id)

        where_clause = f"WHERE {' AND '.join(filters)}"
        sql = f"""
            SELECT id, course_id, file_name, uploaded_at
            FROM documents
            {where_clause}
            ORDER BY {order_by} {order_dir}
            LIMIT %s OFFSET %s;
        """
        
        params.extend([limit, offset])
        results = self.cm.select_all(sql, tuple(params))

        return results

    # ======================================================
    # INSTRUCTORS
    # ======================================================
    def create_instructor(self, name: str, title: str, university: str, email: str) -> str:
        sql = """
            INSERT INTO instructors (name, title, university, email)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """
        return self.cm.insert_one(sql, (name, title, university, email))

    def read_instructor(self, instructor_id: str) -> Optional[dict]:
        sql = """
            SELECT id, name, title, university, email, created_at
            FROM instructors
            WHERE id = %s;
        """
        return self.cm.select_one(sql, (instructor_id,))

    def read_instructor_by_email(self, email: str) -> Optional[dict]:
        """
        Safely fetch an instructor by email.
        Returns None if no matching record exists.
        """
        sql = """
            SELECT id, name, title, university, email, created_at
            FROM instructors
            WHERE email = %s;
        """
        try:
            row = self.cm.select_one(sql, (email,))
            if not row:
                return None
            return row
        except Exception as e:
            print(f"[SQLRepository] Error reading instructor by email: {e}")
            return None

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
        filters = []
        params = []

        if name:
            filters.append("name ILIKE %s")
            params.append(f"%{name}%")
        if title:
            filters.append("title ILIKE %s")
            params.append(f"%{title}%")
        if university:
            filters.append("university ILIKE %s")
            params.append(f"%{university}%")
        if email:
            filters.append("email ILIKE %s")
            params.append(f"%{email}%")

        where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
        sql = f"""
            SELECT id, name, title, university, email, created_at
            FROM instructors
            {where_clause}
            ORDER BY {order_by} {order_dir}
            LIMIT %s OFFSET %s;
        """
        params.extend([limit, offset])
        return self.cm.select_all(sql, tuple(params))

    def delete_instructor(self, instructor_id: str) -> None:
        sql = "DELETE FROM instructors WHERE id = %s;"
        self.cm.execute(sql, (instructor_id,))

    # ======================================================
    # COURSES
    # ======================================================
    def create_course(
        self,
        instructor_id: str,
        name: str,
        institution: str,
        semester_id: int,
        year: int
    ) -> str:
        sql = """
            INSERT INTO courses (instructor_id, name, institution, semester_id, year)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """
        return self.cm.insert_one(sql, (instructor_id, name, institution, semester_id, year))

    def read_course(self, course_id: str) -> Optional[dict]:
        sql = """
            SELECT 
                c.id, c.name, c.institution, c.semester_id, c.year, c.created_at,
                i.id AS instructor_id, i.name AS instructor_name, i.email AS instructor_email
            FROM courses c
            LEFT JOIN instructors i ON c.instructor_id = i.id
            WHERE c.id = %s;
        """
        return self.cm.select_one(sql, (course_id,))

    def read_all_courses(
        self,
        instructor_id: Optional[str] = None,
        institution: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
        order_by: str = "created_at",
        order_dir: str = "desc"
    ) -> List[dict]:
        filters = []
        params = []

        if instructor_id:
            filters.append("instructor_id = %s")
            params.append(instructor_id)
        if institution:
            filters.append("institution ILIKE %s")
            params.append(f"%{institution}%")

        where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
        sql = f"""
            SELECT id, instructor_id, name, institution, semester_id, year, created_at
            FROM courses
            {where_clause}
            ORDER BY {order_by} {order_dir}
            LIMIT %s OFFSET %s;
        """
        params.extend([limit, offset])
        return self.cm.select_all(sql, tuple(params))

    def delete_course(self, course_id: str) -> None:
        self.cm.execute("DELETE FROM courses WHERE id = %s;", (course_id,))

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
        query = """
            INSERT INTO students (name, discord_id, course_id)
            VALUES (%s, %s, %s)
            RETURNING student_id
        """
        self.cursor.execute(query, (name, discord_id, course_id))
        student_id = self.cursor.fetchone()[0]
        self.conn.commit()
        return student_id

    def read_student(self, student_id: str) -> Optional[dict]:
        query = "SELECT * FROM students WHERE student_id = %s"
        self.cursor.execute(query, (student_id,))
        return self.cursor.fetchone()

    def read_all_students(self, course_id: Optional[str] = None) -> List[dict]:
        if course_id:
            query = "SELECT * FROM students WHERE course_id = %s"
            self.cursor.execute(query, (course_id,))
        else:
            query = "SELECT * FROM students"
            self.cursor.execute(query)
        return self.cursor.fetchall()

    def delete_student(self, student_id: str) -> None:
        query = "DELETE FROM students WHERE student_id = %s"
        self.cursor.execute(query, (student_id,))
        self.conn.commit()
