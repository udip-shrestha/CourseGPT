import base64
from typing import Optional, List, Dict, Any
from API.Repository.postgres_connection_manager import PostgresConnectionManager
from API.Repository.i_sql_repository import ISQLRepository


class SQLRepository(ISQLRepository):
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

    def read_document(self, course_id: str, doc_id: str) -> Optional[dict]:
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
            WHERE d.id = %s AND d.course_id = %s;
        """

        row = self.cm.select_one(sql, (doc_id, course_id))

        if not row:
            return None

        if row.get("file_data") is not None:
            row["file_data"] = base64.b64encode(row["file_data"]).decode("utf-8")

        return row

    def delete_document(self, course_id: str, doc_id: str) -> None:
        sql = "DELETE FROM documents WHERE id = %s AND course_id = %s;"
        self.cm.execute(sql, (doc_id, course_id))

    def read_all_documents(
        self,
        course_id: str,
        file_type_id: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
        order_by: str = "uploaded_at",
        order_dir: str = "desc",
    ) -> dict:
        allowed_order_by = {"uploaded_at", "file_name"}
        allowed_order_dir = {"asc", "desc"}

        if order_by not in allowed_order_by:
            order_by = "uploaded_at"
        if order_dir.lower() not in allowed_order_dir:
            order_dir = "desc"

        filters = ["course_id = %s"]
        params = [course_id]

        if file_type_id:
            filters.append("file_type_id = %s")
            params.append(file_type_id)

        where_clause = f"WHERE {' AND '.join(filters)}"

        # --- Count total matching records (before pagination)
        count_sql = f"SELECT COUNT(*) AS total FROM documents {where_clause};"
        total_row = self.cm.select_one(count_sql, tuple(params))
        total_count = total_row["total"] if total_row else 0

        # --- Fetch paginated results
        data_sql = f"""
            SELECT 
                d.id, 
                d.course_id, 
                d.file_name, 
                d.uploaded_at,
                ft.extension AS file_type
            FROM documents d
            LEFT JOIN file_types ft ON d.file_type_id = ft.id
                {where_clause}
            ORDER BY {order_by} {order_dir}
            LIMIT %s OFFSET %s;
        """
        data_params = params + [limit, offset]
        results = self.cm.select_all(data_sql, tuple(data_params))

        return {
            "total": total_count,
            "documents": results or []
        }


    # ======================================================
    # INSTRUCTORS
    # ======================================================
    def create_instructor(self, name: str, title: str, university: str, email: str, encrypted_password: str) -> str:
        sql = """
            INSERT INTO instructors (name, title, university, email, password, role_id)
            VALUES (
                %s, %s, %s, %s, %s,
                (SELECT id FROM instructor_roles WHERE role_name = 'INSTRUCTOR')
            )
            RETURNING id;
        """
        return self.cm.insert_one(sql, (name, title, university, email, encrypted_password))

    def read_instructor(self, instructor_id: str) -> Optional[dict]:
        sql = """
            SELECT i.id, i.name, i.title, i.university, i.email, r.role_name AS role, i.created_at, i.updated_at
            FROM instructors i
            LEFT JOIN instructor_roles r ON i.role_id = r.id
            WHERE i.id = %s;
        """
        return self.cm.select_one(sql, (instructor_id,))

    def read_instructor_by_email(self, email: str) -> Optional[dict]:
        sql = """
            SELECT i.id, i.name, i.title, i.university, i.email, i.password, r.role_name AS role, i.created_at, i.updated_at
            FROM instructors i
            LEFT JOIN instructor_roles r ON i.role_id = r.id
            WHERE i.email = %s;
        """
        return self.cm.select_one(sql, (email,))

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
    ) -> List[dict]:
        """Fetch instructors with optional filters, pagination, and total count."""

        allowed_order_by = {"created_at", "name"}
        allowed_order_dir = {"asc", "desc"}

        if order_by not in allowed_order_by:
            order_by = "created_at"
        if order_dir.lower() not in allowed_order_dir:
            order_dir = "desc"

        filters = []
        params = []

        if name:
            filters.append("i.name ILIKE %s")
            params.append(f"%{name}%")
        if title:
            filters.append("i.title ILIKE %s")
            params.append(f"%{title}%")
        if university:
            filters.append("i.university ILIKE %s")
            params.append(f"%{university}%")
        if email:
            filters.append("i.email ILIKE %s")
            params.append(f"%{email}%")
        if role:
            filters.append("r.role_name = %s")
            params.append(role)

        where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""

        # --- Count query ---
        count_sql = f"""
            SELECT COUNT(*) AS total
            FROM instructors i
            LEFT JOIN instructor_roles r ON i.role_id = r.id
            {where_clause};
        """
        total_row = self.cm.select_one(count_sql, tuple(params))
        total_count = total_row["total"] if total_row else 0

        # --- Data query ---
        data_sql = f"""
            SELECT i.id, i.name, i.title, i.university, i.email,
                r.role_name AS role, i.created_at, i.updated_at
            FROM instructors i
            LEFT JOIN instructor_roles r ON i.role_id = r.id
            {where_clause}
            ORDER BY i.{order_by} {order_dir}
            LIMIT %s OFFSET %s;
        """
        data_params = tuple(params + [limit, offset])
        results = self.cm.select_all(data_sql, data_params)

        return {"total": total_count, "instructors": results or []}

    def delete_instructor(self, instructor_id: str) -> None:
        """Delete an instructor by their UUID."""
        sql = """
            DELETE FROM instructors
            WHERE id = %s;
        """
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
    ) -> dict:
        """Fetch all courses with optional filters, pagination, and total count."""

        allowed_order_by = {"created_at", "name", "year"}
        allowed_order_dir = {"asc", "desc"}

        if order_by not in allowed_order_by:
            order_by = "created_at"
        if order_dir.lower() not in allowed_order_dir:
            order_dir = "desc"

        filters = []
        params = []

        if instructor_id:
            filters.append("instructor_id = %s")
            params.append(instructor_id)
        if institution:
            filters.append("institution ILIKE %s")
            params.append(f"%{institution}%")

        where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""

        # --- Count total matching records ---
        count_sql = f"SELECT COUNT(*) AS total FROM courses {where_clause};"
        total_row = self.cm.select_one(count_sql, tuple(params))
        total_count = total_row["total"] if total_row else 0

        # --- Fetch paginated results ---
        data_sql = f"""
            SELECT 
                c.id, c.instructor_id, c.name, c.institution, 
                c.semester_id, c.year, c.created_at, i.name AS instructor_name
            FROM courses c
            LEFT JOIN instructors i ON c.instructor_id = i.id
            {where_clause}
            ORDER BY c.{order_by} {order_dir}
            LIMIT %s OFFSET %s;
        """
        data_params = tuple(params + [limit, offset])
        results = self.cm.select_all(data_sql, data_params)

        return {
            "total": total_count,
            "courses": results or []
        }

    def delete_course(self, course_id: str) -> None:
        self.cm.execute("DELETE FROM courses WHERE id = %s;", (course_id,))

    def get_course_by_name(self, course_name: str) -> Optional[dict]:
        """
        Retrieve a single course record by its exact name.
        """
        sql = """
            SELECT 
                id, instructor_id, name, institution, semester_id, year, created_at
            FROM courses
            WHERE name = %s
            LIMIT 1;
        """
        return self.cm.select_one(sql, (course_name,))

    # ======================================================
    # STUDENTS
    # ======================================================
    def create_student(self, name: str, discord_id: str, course_id: str) -> str:
        #Create student (if not exists)
        sql_insert_student = """
            INSERT INTO students (name, discord_id)
            VALUES (%s, %s)
            RETURNING id;
        """
        student_id = self.cm.insert_one(sql_insert_student, (name, discord_id))

        #Link student to course
        sql_link = """
            INSERT INTO student_courses (student_id, course_id)
            VALUES (%s, %s);
        """
        self.cm.execute(sql_link, (student_id, course_id))

        return student_id

    def read_student(self, student_id: str) -> Optional[dict]:
        sql = """
            SELECT s.id, s.name, s.discord_id, s.created_at, sc.course_id
            FROM students s
            LEFT JOIN student_courses sc ON s.id = sc.student_id
            WHERE s.id = %s;
        """
        return self.cm.select_one(sql, (student_id,))

    def read_all_students(self, course_id: Optional[str] = None) -> List[dict]:
        if course_id:
            sql = """
                SELECT s.id, s.name, s.discord_id, s.created_at
                FROM students s
                JOIN student_courses sc ON s.id = sc.student_id
                WHERE sc.course_id = %s;
            """
            return self.cm.select_all(sql, (course_id,))
        else:
            sql = "SELECT * FROM students;"
            return self.cm.select_all(sql)

    def delete_student(self, student_id: str) -> None:
        # remove course links first
        self.cm.execute("DELETE FROM student_courses WHERE student_id = %s;", (student_id,))
        # remove student
        self.cm.execute("DELETE FROM students WHERE id = %s;", (student_id,))

    def read_courses_by_discord(self, discord_id: str) -> list[dict]:
        """
        Retrieve all courses a student (identified by their Discord ID) is registered in.
        """
        sql = """
            SELECT 
                c.id AS course_id,
                c.name AS course_name,
                c.institution,
                c.year,
                s.id AS student_id,
                s.name AS student_name,
                s.discord_id
            FROM students s
            JOIN student_courses sc ON s.id = sc.student_id
            JOIN courses c ON sc.course_id = c.id
            WHERE s.discord_id = %s
        """
        rows = self.cm.select_all(sql, (discord_id,))
        
        # convert UUIDs and integers to strings
        for r in rows:
            r["course_id"] = str(r["course_id"])
            r["student_id"] = str(r["student_id"])
            r["year"] = str(r["year"])
        
        return rows


    # ======================================================
    # QUERIES (Student Questions)
    # ======================================================
    def create_query_log(
        self,
        student_id: str,
        course_id: str,
        query_text: str,
        response_text: str
    ) -> str:
        """
        Logs a student's query and the generated system response.
        Returns the new query record ID.
        """
        sql = """
            INSERT INTO queries (student_id, course_id, query_text, response_text)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """
        return self.cm.insert_one(sql, (student_id, course_id, query_text, response_text))

    def read_queries_by_student(self, student_id: str, course_id: str) -> List[Dict[str, str]]:
        """
        Retrieves all queries made by a specific student for a specific course.
        Includes course name and timestamp.
        """
        sql = """
            SELECT 
                q.id AS query_id,
                q.query_text,
                q.response_text,
                q.asked_at,
                c.id AS course_id,
                c.name AS course_name
            FROM queries q
            LEFT JOIN courses c ON q.course_id = c.id
            WHERE q.student_id = %s AND q.course_id = %s
            ORDER BY q.asked_at DESC;
        """
        rows = self.cm.select_all(sql, (student_id, course_id))

        for r in rows:
            r["query_id"] = str(r["query_id"])
            if r.get("course_id"):
                r["course_id"] = str(r["course_id"])
            if "asked_at" in r and r["asked_at"]:
                r["asked_at"] = str(r["asked_at"])

        return rows