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
        sql = """
            SELECT id, name, title, university, email, created_at
            FROM instructors
            WHERE email = %s;
        """
        return self.cm.select_one(sql, (email,))

    def read_all_instructors(self) -> List[dict]:
        sql = """
            SELECT id, name, title, university, email, created_at
            FROM instructors
            ORDER BY created_at DESC;
        """
        return self.cm.select_all(sql)

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