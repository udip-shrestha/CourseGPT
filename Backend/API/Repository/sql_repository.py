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

    def read_all_file_types(self) -> List[Dict[str, Any]]:
        sql = """
            SELECT * 
            FROM file_types;
        """
        return self.cm.select_all(sql)


    # ======================================================
    # RAG STRATEGIES
    # ======================================================
    def read_rag_strategy_by_type(self, type_name: str) -> Optional[Dict[str, Any]]:
        sql = """
            SELECT *
            FROM rag_strategies
            WHERE LOWER(type_name) = LOWER(%s);
        """
        return self.cm.select_one(sql, (type_name,))

    def read_all_rag_strategies(self) -> List[Dict[str, Any]]:
        sql = """
            SELECT *
            FROM rag_strategies
            ORDER BY id;
        """
        return self.cm.select_all(sql)


    # ======================================================
    # DOCUMENTS
    # ======================================================
    def create_document(self, course_id: str, file_name: str, file_bytes: bytes, file_type_id: str) -> str:
        sql = """
            INSERT INTO documents (course_id, file_name, file_data, file_type_id, processing_status_id)
            VALUES (
                %s, %s, %s, %s,
                (SELECT id FROM processing_statuses WHERE name = 'PROCESSING')
            )
            RETURNING id;
        """
        return self.cm.insert_one(sql, (course_id, file_name, file_bytes, file_type_id))

    def read_document(self, course_id: str, doc_id: str) -> Optional[dict]:
        sql = """
            SELECT 
                d.file_name,
                d.file_data,
                ft.mime_type,
                ft.can_preview,
                ft.native_preview
            FROM documents d
            LEFT JOIN file_types ft ON d.file_type_id = ft.id
            WHERE d.id = %s AND d.course_id = %s;
        """

        return self.cm.select_one(sql, (doc_id, course_id))

    def delete_document(self, course_id: str, doc_id: str) -> None:
        sql = "DELETE FROM documents WHERE id = %s AND course_id = %s;"
        self.cm.execute(sql, (doc_id, course_id))

    def read_all_documents(
        self,
        course_id: str,
        file_type_id: Optional[str] = None,
        file_name: Optional[str] = None,
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
            filters.append("d.file_type_id = %s")
            params.append(file_type_id)
        if file_name:
            filters.append("d.file_name ILIKE %s")
            params.append(f"%{file_name}%")

        where_clause = f"WHERE {' AND '.join(filters)}"

        # --- Count total matching records
        count_sql = f"SELECT COUNT(*) AS total FROM documents d {where_clause};"
        total_row = self.cm.select_one(count_sql, tuple(params))
        total_count = total_row["total"] if total_row else 0

        # --- Fetch paginated results
        data_sql = f"""
            SELECT 
                d.id,
                d.course_id,
                d.file_name,
                d.uploaded_at,
                d.file_type_id,
                ft.can_preview,
                ps.name AS processing_status
            FROM documents d
            LEFT JOIN file_types ft ON d.file_type_id = ft.id
            LEFT JOIN processing_statuses ps ON d.processing_status_id = ps.id
            {where_clause}
            ORDER BY {order_by} {order_dir}
            LIMIT %s OFFSET %s;
        """
        data_params = params + [limit, offset]
        results = self.cm.select_all(data_sql, tuple(data_params))

        return {
            "total": total_count,
            "documents": results
        }

    def update_document_processing_status_completed(self, doc_id: str) -> None:
        sql = """
            UPDATE documents
            SET processing_status_id = ( SELECT id FROM processing_statuses WHERE name = 'COMPLETED' )
            WHERE id = %s;
        """
        self.cm.execute(sql, (doc_id,))

    def update_document_processing_status_failed(self, doc_id: str) -> None:
        sql = """
            UPDATE documents
            SET processing_status_id = ( SELECT id FROM processing_statuses WHERE name = 'FAILED' )
            WHERE id = %s;
        """
        self.cm.execute(sql, (doc_id,))

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
            filters.append("i.role_id = %s")
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
                i.role_id, r.role_name AS role, 
                i.created_at, i.updated_at
            FROM instructors i
            LEFT JOIN instructor_roles r ON i.role_id = r.id
            {where_clause}
            ORDER BY i.{order_by} {order_dir}
            LIMIT %s OFFSET %s;
        """
        data_params = tuple(params + [limit, offset])
        results = self.cm.select_all(data_sql, data_params)

        return {"total": total_count, "instructors": results}

    def delete_instructor(self, instructor_id: str) -> None:
        """Delete an instructor by their UUID."""
        sql = """
            DELETE FROM instructors
            WHERE id = %s;
        """
        self.cm.execute(sql, (instructor_id,))

    def update_instructor(self, instructor_id: str, updates: dict) -> dict:
        """
        Update instructor fields dynamically based on provided key-value pairs.
        Returns the updated instructor record.
        """
        # Build dynamic SET clause
        set_clause = ", ".join([f"{key} = %s" for key in updates.keys()])
        values = list(updates.values()) + [instructor_id]

        sql = f"""
            UPDATE instructors
            SET {set_clause}, updated_at = NOW()
            WHERE id = %s
            RETURNING *;
        """
        return self.cm.select_one(sql, tuple(values))

    def update_instructor_password(self, instructor_id: str, encrypted_password: str) -> None:
        sql = """
            UPDATE instructors
            SET password = %s, updated_at = NOW()
            WHERE id = %s;
        """
        self.cm.execute(sql, (encrypted_password, instructor_id))

    # ======================================================
    # PASSWORD RESET CODES
    # ======================================================
    def create_password_reset_code(self, instructor_id: str, code: str) -> None:
        sql = """
            INSERT INTO password_reset_codes (instructor_id, code, created_at, expires_at)
            VALUES (%s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '1 hour')
            ON CONFLICT (instructor_id)
            DO UPDATE SET
                code = EXCLUDED.code,
                expires_at = CURRENT_TIMESTAMP + INTERVAL '1 hour',
                created_at = CURRENT_TIMESTAMP;
        """
        self.cm.execute(sql, (instructor_id, code))

    def read_password_reset_code(self, instructor_id: str) -> Optional[dict]:
        sql = """
            SELECT code
            FROM password_reset_codes
            WHERE instructor_id = %s aND expires_at > NOW();
        """
        return self.cm.select_one(sql, (instructor_id,))
    
    # ======================================================
    # COURSES
    # ======================================================
    def create_course(self, instructor_id: str, name: str, institution: str, semester_id: int, year: int, rag_strategy_id: Optional[int] = None) -> str:
        columns = ["instructor_id", "name", "institution", "semester_id", "year"]
        values = [instructor_id, name, institution, semester_id, year]

        if rag_strategy_id is not None:
            columns.append("rag_strategy_id")
            values.append(rag_strategy_id)

        col_str = ", ".join(columns)
        placeholder_str = ", ".join(["%s"] * len(values))
        sql = f"""
            INSERT INTO courses ({col_str})
            VALUES ({placeholder_str})
            RETURNING id;
        """
        return self.cm.insert_one(sql, tuple(values))

    def read_course_by_name(self, name: str, instructor_id: str) -> dict | None:
        sql = """
            SELECT id, name, institution, year, semester_id, instructor_id, rag_strategy_id
            FROM courses
            WHERE name = %s AND instructor_id = %s;
        """
        return self.cm.select_one(sql, (name, instructor_id))

    def read_course(self, course_id: str) -> Optional[dict]:
        sql = """
            SELECT 
                c.id, c.name, c.institution, c.semester_id, c.year, c.created_at,
                c.canvas_course_id, c.canvas_context_id,
                i.id AS instructor_id, i.name AS instructor_name, i.email AS instructor_email,
                rs.id AS rag_strategy_id, rs.type_name AS rag_strategy_name,
                s.name AS semester_name
            FROM courses c
            LEFT JOIN instructors i ON c.instructor_id = i.id
            LEFT JOIN semesters s ON c.semester_id = s.id
            LEFT JOIN rag_strategies rs ON c.rag_strategy_id = rs.id
            WHERE c.id = %s;
        """
        return self.cm.select_one(sql, (course_id,))

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
            filters.append("c.instructor_id = %s")
            params.append(instructor_id)
        if institution:
            filters.append("c.institution ILIKE %s")
            params.append(f"%{institution}%")
        if name:
            filters.append("c.name ILIKE %s")
            params.append(f"%{name}%")
        if semester_id:
            filters.append("c.semester_id = %s")
            params.append(semester_id)
        if rag_strategy_id:
            filters.append("c.rag_strategy_id = %s")
            params.append(rag_strategy_id)

        where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""

        # --- Count total matching records ---
        count_sql = f"SELECT COUNT(*) AS total FROM courses c {where_clause};"
        total_row = self.cm.select_one(count_sql, tuple(params))
        total_count = total_row["total"] if total_row else 0

        # --- Fetch paginated results ---
        data_sql = f"""
            SELECT 
                c.id, c.name, c.year, c.created_at, c.institution, 
                c.instructor_id, i.name AS instructor_name,
                c.rag_strategy_id, rs.type_name AS rag_strategy_name,
                c.semester_id, s.name AS semester_name
            FROM courses c
            LEFT JOIN instructors i ON c.instructor_id = i.id
            LEFT JOIN rag_strategies rs ON c.rag_strategy_id = rs.id
            LEFT JOIN semesters s ON c.semester_id = s.id
            {where_clause}
            ORDER BY c.{order_by} {order_dir}
            LIMIT %s OFFSET %s;
        """
        data_params = tuple(params + [limit, offset])
        results = self.cm.select_all(data_sql, data_params)

        return {
            "total": total_count,
            "courses": results
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

    def read_course_by_canvas_id(self, canvas_course_id: str) -> Optional[dict]:
        """Find a course by its linked Canvas course identifier."""
        sql = "SELECT * FROM courses WHERE canvas_course_id = %s LIMIT 1;"
        return self.cm.select_one(sql, (canvas_course_id,))

    def read_student_by_canvas(self, canvas_user_id: str) -> Optional[dict]:
        """Retrieve a student record by their Canvas user id."""
        sql = "SELECT id, name, discord_id, canvas_user_id FROM students WHERE canvas_user_id = %s LIMIT 1;"
        return self.cm.select_one(sql, (canvas_user_id,))
    
    def update_course(self, course_id: str, updates: dict) -> dict:
        set_clause = ", ".join([f"{key} = %s" for key in updates.keys()])
        values = list(updates.values()) + [course_id]

        sql = f"""
            UPDATE courses
            SET {set_clause}, updated_at = NOW()
            WHERE id = %s
            RETURNING *;
        """
        return self.cm.select_one(sql, tuple(values))


    # ======================================================
    # STUDENTS
    # ======================================================
    def create_student(
        self,
        name: str,
        discord_id: str | None,
        course_id: str,
        canvas_user_id: str | None = None,
    ) -> str:
        # Step 1: See if a student already exists by discord or canvas id
        existing_sql = "SELECT id, discord_id, canvas_user_id FROM students WHERE " \
                       "(discord_id IS NOT NULL AND discord_id = %s) OR " \
                       "(canvas_user_id IS NOT NULL AND canvas_user_id = %s);"
        existing = self.cm.select_one(existing_sql, (discord_id, canvas_user_id))

        if existing:
            student_id = existing["id"]

            # Update missing identifiers if provided
            if canvas_user_id and not existing.get("canvas_user_id"):
                self.cm.execute(
                    "UPDATE students SET canvas_user_id=%s WHERE id=%s;",
                    (canvas_user_id, student_id),
                )
            if discord_id and not existing.get("discord_id"):
                self.cm.execute(
                    "UPDATE students SET discord_id=%s WHERE id=%s;",
                    (discord_id, student_id),
                )

            # Step 2: Check if already registered for this course
            link_sql = "SELECT 1 FROM student_courses WHERE student_id = %s AND course_id = %s;"
            linked = self.cm.select_one(link_sql, (student_id, course_id))

            if not linked:
                # Register this student in the new course
                self.cm.execute(
                    "INSERT INTO student_courses (student_id, course_id) VALUES (%s, %s);",
                    (student_id, course_id),
                )
            return str(student_id)

        # Student doesn’t exist yet → create and link
        sql_insert_student = """
            INSERT INTO students (name, discord_id, canvas_user_id)
            VALUES (%s, %s, %s)
            RETURNING id;
        """
        student_id = self.cm.insert_one(sql_insert_student, (name, discord_id, canvas_user_id))
        self.cm.execute("INSERT INTO student_courses (student_id, course_id) VALUES (%s, %s);",
                        (student_id, course_id))
        return str(student_id)

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

    def read_student_by_discord(self, discord_id: str) -> Optional[dict]:
        """
        Retrieve a student by their Discord ID.
        """
        sql = "SELECT * FROM students WHERE discord_id = %s;"
        return self.cm.select_one(sql, (discord_id,))

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

    def remove_student_from_course(self, student_id: str, course_id: str) -> bool:
        """
        Deletes a record linking a student to a course in the junction table.
        Returns True if a row was deleted, False if no link existed.
        """
        check_sql = """
            SELECT 1 FROM student_courses 
            WHERE student_id = %s AND course_id = %s LIMIT 1;
        """
        try:
            exists = self.cm.select_one(check_sql, (student_id, course_id))
        except Exception as e:
            print("[DEBUG] remove_student_from_course check error:", e)
            raise

        if not exists:
            # No link existed
            return False
    
        delete_query = """
            DELETE FROM student_courses
            WHERE student_id = %s AND course_id = %s;
        """
        try:
            self.cm.execute(delete_query, (student_id, course_id))
            return True
        except Exception as e:
            print("[DEBUG] remove_student_from_course error:", e)
            raise


    # ======================================================
    # QUERIES (Student Questions)
    # ======================================================
    def create_query(self, student_id: Optional[str], course_id: str, query_text: str, response_text: Optional[str]) -> str:
        sql = """
            INSERT INTO queries (student_id, course_id, query_text, response_text)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """
        return self.cm.insert_one(sql, (student_id, course_id, query_text, response_text))

    def read_query(self, course_id: str, query_id: str) -> Optional[dict]:
        sql = """
            SELECT 
                id, student_id, course_id, query_text, 
                response_text, asked_at
            FROM queries
            WHERE id = %s AND course_id = %s;
        """
        return self.cm.select_one(sql, (query_id, course_id))

    def read_queries_for_student_course(
        self,
        student_id: str,
        course_id: str,
        limit: int = 10,
        offset: int = 0,
        order_by: str = "asked_at",
        order_dir: str = "desc"
    ) -> dict:
        # --- Allowed sorting fields ---
        allowed_order_by = {"asked_at", "id", "query_text", "response_text"}
        allowed_order_dir = {"asc", "desc"}

        # Validate sorting inputs
        if order_by not in allowed_order_by:
            order_by = "asked_at"
        if order_dir.lower() not in allowed_order_dir:
            order_dir = "desc"

        # --- WHERE clause and base params ---
        filters = ["student_id = %s", "course_id = %s"]
        params = [student_id, course_id]

        where_clause = f"WHERE {' AND '.join(filters)}"

        # --- 1. Count total rows (before pagination) ---
        count_sql = f"""
            SELECT COUNT(*) AS total
            FROM queries
            {where_clause};
        """
        total_row = self.cm.select_one(count_sql, tuple(params))
        total_count = total_row["total"] if total_row else 0

        # --- 2. Fetch paginated results ---
        data_sql = f"""
            SELECT
                id,
                query_text,
                response_text,
                asked_at
            FROM queries
            {where_clause}
            ORDER BY {order_by} {order_dir}
            LIMIT %s OFFSET %s;
        """

        data_params = params + [limit, offset]
        results = self.cm.select_all(data_sql, tuple(data_params))

        return {
            "total": total_count,
            "queries": results
        }

    def read_all_queries_for_course(
        self,
        course_id: str,
        limit: int = 10,
        offset: int = 0,
        order_by: str = "asked_at",
        order_dir: str = "desc",
    ) -> dict:
        allowed_order_by = {"asked_at", "id", "student_id", "query_text", "response_text"}
        allowed_order_dir = {"asc", "desc"}

        if order_by not in allowed_order_by:
            order_by = "asked_at"

        if order_dir.lower() not in allowed_order_dir:
            order_dir = "desc"

        filters = ["course_id = %s"]
        params = [course_id]

        where_clause = f"WHERE {' AND '.join(filters)}"

        count_sql = f"""
            SELECT COUNT(*) AS total
            FROM queries
            {where_clause};
        """
        total_row = self.cm.select_one(count_sql, tuple(params))
        total_count = total_row["total"] if total_row else 0

        data_sql = f"""
            SELECT
                id,
                student_id,
                query_text,
                response_text,
                asked_at
            FROM queries
            {where_clause}
            ORDER BY {order_by} {order_dir}
            LIMIT %s OFFSET %s;
        """

        data_params = params + [limit, offset]
        results = self.cm.select_all(data_sql, tuple(data_params))

        return {
            "total": total_count,
            "queries": results
        }

    def delete_query(self, course_id: str, query_id: str) -> None:
        sql = "DELETE FROM queries WHERE id = %s AND course_id = %s;"
        self.cm.execute(sql, (query_id, course_id))

    # ======================================================
    # FEEDBACK
    # ======================================================
    def create_feedback(self, course_id: str, feedback_text: str, received_at: Optional[str] = None) -> str:
        """
        Insert a new feedback record for a course and return its id.
        If `received_at` is not provided, database default NOW() will be used.
        """
        if received_at:
            sql = """
                INSERT INTO feedback (course_id, feedback_text, received_at)
                VALUES (%s, %s, %s)
                RETURNING id;
            """
            return self.cm.insert_one(sql, (course_id, feedback_text, received_at))

        sql = """
            INSERT INTO feedback (course_id, feedback_text, received_at)
            VALUES (%s, %s, NOW())
            RETURNING id;
        """
        return self.cm.insert_one(sql, (course_id, feedback_text))

    # ======================================================
    # FEEDBACK
    # ======================================================
    def create_feedback(self, course_id: str, feedback_text: str, received_at: Optional[str] = None) -> str:
        """
        Insert a new feedback record for a course and return its id.
        If `received_at` is not provided, database default NOW() will be used.
        """
        if received_at:
            sql = """
                INSERT INTO feedback (course_id, feedback_text, received_at)
                VALUES (%s, %s, %s)
                RETURNING id;
            """
            return self.cm.insert_one(sql, (course_id, feedback_text, received_at))

        sql = """
            INSERT INTO feedback (course_id, feedback_text, received_at)
            VALUES (%s, %s, NOW())
            RETURNING id;
        """
        return self.cm.insert_one(sql, (course_id, feedback_text))
    
    def read_all_feedback(self, limit: int = 50, offset: int = 0, order_by: str = "received_at", order_dir: str = "desc") -> dict:
        # Standardize sorting
        sort_dir = "ASC" if order_dir.lower() == "asc" else "DESC"
        
        count_sql = "SELECT COUNT(*) AS total FROM feedback;"
        total_row = self.cm.select_one(count_sql)
        total = total_row["total"] if total_row else 0

        data_sql = f"""
            SELECT f.id, f.course_id, c.name as course_name, f.feedback_text, f.received_at
            FROM feedback f
            JOIN courses c ON f.course_id = c.id
            ORDER BY f.{order_by} {sort_dir}
            LIMIT %s OFFSET %s;
        """
        results = self.cm.select_all(data_sql, (limit, offset))
        return {"total": total, "feedback": results}

    def read_all_feedback_for_course(self, course_id: str, limit: int = 50, offset: int = 0, order_by: str = "received_at", order_dir: str = "desc") -> dict:
        sort_dir = "ASC" if order_dir.lower() == "asc" else "DESC"

        count_sql = "SELECT COUNT(*) AS total FROM feedback WHERE course_id = %s;"
        total_row = self.cm.select_one(count_sql, (course_id,))
        total = total_row["total"] if total_row else 0

        data_sql = f"""
            SELECT id, course_id, feedback_text, received_at
            FROM feedback
            WHERE course_id = %s
            ORDER BY {order_by} {sort_dir}
            LIMIT %s OFFSET %s;
        """
        results = self.cm.select_all(data_sql, (course_id, limit, offset))
        return {"total": total, "feedback": results}

    def create_answer_feedback(self, course_id: str, student_id: str, query_id: str, vote: str) -> str:
        sql = """
            INSERT INTO answer_feedback (query_id, course_id, student_id, vote)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """
        return self.cm.insert_one(sql, (query_id, course_id, student_id, vote))

    def read_course_satisfaction(self, course_id: str) -> dict:
        sql = """
            SELECT
                course_id,
                COUNT(*) FILTER (WHERE vote = 'up') AS upvotes,
                COUNT(*) FILTER (WHERE vote = 'down') AS downvotes,
                COUNT(*) AS total_votes,
                (COUNT(*) FILTER (WHERE vote = 'up')::float / COUNT(*)) * 5.0 AS satisfaction_score
            FROM answer_feedback
            WHERE course_id = %s
            GROUP BY course_id;
        """
        result = self.cm.select_one(sql, (course_id,))
        if not result:
            return {
                "course_id": course_id,
                "upvotes": 0,
                "downvotes": 0,
                "total_votes": 0,
                "satisfaction_score": 0.0,
            }
        return result

    # ======================================================
    # DISCORD ADMINS
    # ======================================================
    def create_discord_admin(self, discord_id: str) -> str:
        sql = """
            INSERT INTO discord_admins (discord_id)
            VALUES (%s)
            RETURNING id;
        """
        return self.cm.insert_one(sql, (discord_id,))

    def read_discord_admin(self, discord_id: str) -> Optional[Dict[str, Any]]:
        sql = """
            SELECT id, discord_id, created_at
            FROM discord_admins
            WHERE discord_id = %s;
        """
        return self.cm.select_one(sql, (discord_id,))

    def read_all_discord_admins(self, limit: int = 50, offset: int = 0) -> dict:
        count_sql = "SELECT COUNT(*) AS total FROM discord_admins;"
        total_row = self.cm.select_one(count_sql)
        total = total_row["total"] if total_row else 0

        data_sql = """
            SELECT id, discord_id, created_at
            FROM discord_admins
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s;
        """
        results = self.cm.select_all(data_sql, (limit, offset))
        return {"total": total, "admins": results}

    def delete_discord_admin(self, discord_id: str) -> None:
        sql = "DELETE FROM discord_admins WHERE discord_id = %s;"
        self.cm.execute(sql, (discord_id,))

    # ======================================================
    # ANALYTICS
    # ======================================================

    def read_course_query_stats(self, course_id: str, days: Optional[int] = None) -> Optional[Dict[str, Any]]:
        date_filter = ""
        params: List[Any] = []

        if days:
            date_filter = f"AND q.asked_at >= NOW() - (%s * INTERVAL '1 day')"

        sql = f"""
            SELECT
                (SELECT COUNT(*) FROM queries q
                WHERE q.course_id = %s {date_filter}) AS total_queries,

                (SELECT COUNT(DISTINCT q.student_id)
                FROM queries q
                WHERE q.course_id = %s {date_filter}) AS active_users,

                (SELECT COUNT(*)
                FROM student_courses sc
                WHERE sc.course_id = %s) AS total_enrolled;
        """

        # Correct param order: match placeholders exactly
        params.append(course_id)
        if days:
            params.append(days)

        params.append(course_id)
        if days:
            params.append(days)

        params.append(course_id)

        row = self.cm.select_one(sql, tuple(params))
        if not row:
            return None

        active = row["active_users"] or 0
        total = row["total_enrolled"] or 0

        return {
            "totalQueries": row["total_queries"] or 0,
            "activeUsers": active,
            "totalEnrolled": total,
            "engagementRate": int((active / total) * 100) if total > 0 else 0,
        }

    def read_top_questions(self,course_id: str,limit: int, days: Optional[int] = None) -> List[Dict[str, Any]]:
        filters = ["course_id = %s"]
        params: List[Any] = [course_id]

        if days:
            filters.append("asked_at >= NOW() - (%s * INTERVAL '1 day')")
            params.append(days)

        where_clause = f"WHERE {' AND '.join(filters)}"

        sql = f"""
            SELECT
                query_text AS "queryText",
                COUNT(*) AS count
            FROM queries
            {where_clause}
            GROUP BY query_text
            ORDER BY count DESC
            LIMIT %s;
        """

        params.append(limit)
        return self.cm.select_all(sql, tuple(params))

    def read_top_keywords(self,course_id: str, limit: int, days: Optional[int] = None) -> List[Dict[str, Any]]:
        filters = ["course_id = %s"]
        params: List[Any] = [course_id]

        if days:
            filters.append("asked_at >= NOW() - (%s * INTERVAL '1 day')")
            params.append(days)

        where_clause = f"WHERE {' AND '.join(filters)}"

        sql = f"""
            SELECT
                LOWER(word) AS keyword,
                COUNT(*) AS count
            FROM (
                SELECT
                    unnest(regexp_split_to_array(query_text, '\s+')) AS word
                FROM queries
                {where_clause}
            ) t
            WHERE length(word) > 2
            GROUP BY LOWER(word)
            ORDER BY count DESC
            LIMIT %s;
        """

        params.append(limit)
        return self.cm.select_all(sql, tuple(params))

    def read_engagement_stats(self, course_id: str) -> Dict[str, Any]:

        sql = """
            SELECT
                COUNT(DISTINCT sc.student_id) AS total_students,
                COUNT(DISTINCT q.student_id) AS active_students
            FROM student_courses sc
            LEFT JOIN queries q
                ON sc.student_id = q.student_id
                AND sc.course_id = q.course_id
            WHERE sc.course_id = %s;
        """

        row = self.cm.select_one(sql, (course_id,))

        total = row["total_students"] if row else 0
        active = row["active_students"] if row else 0

        return {
            "totalStudents": total or 0,
            "activeStudents": active or 0,
            "engagementRate": int((active / total) * 100) if total > 0 else 0,
        }