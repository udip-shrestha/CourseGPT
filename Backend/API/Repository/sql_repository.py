import base64
from typing import Optional, List, Dict, Any
from unittest import result
from API.Repository.postgres_connection_manager import PostgresConnectionManager
from API.Repository.i_sql_repository import ISQLRepository
from fastapi import HTTPException, status


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
            INSERT INTO documents (course_id, file_name, file_data, file_type_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """
        return self.cm.insert_one(sql, (course_id, file_name, file_bytes, file_type_id))

    def read_document(self, course_id: str, doc_id: str) -> Optional[dict]:
        sql = """
            SELECT 
                d.file_name,
                d.file_data,
                ft.mime_type
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
            "documents": results
        }


    # ======================================================
    # INSTRUCTORS
    # ======================================================
    def create_instructor(self, name: str, title: str, university: str, email: str, encrypted_password: str) -> str:
        existing = self.read_instructor_by_email(email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Instructor with email={email} already exists."
            )

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

        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields provided for update."
            )

        # Build dynamic SET clause
        set_clause = ", ".join([f"{key} = %s" for key in updates.keys()])
        values = list(updates.values()) + [instructor_id]

        sql = f"""
            UPDATE instructors
            SET {set_clause}, updated_at = NOW()
            WHERE id = %s
            RETURNING id, name, title, university, email, 
                        (SELECT role_name FROM instructor_roles WHERE id = role_id) AS role,
                        created_at, updated_at;
        """

        updated = self.cm.select_one(sql, tuple(values))
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Instructor with id={instructor_id} not found."
            )

        return updated

    # ======================================================
    # COURSES
    # ======================================================
    def create_course(self, instructor_id: str, name: str, institution: str, semester_id: int, year: int, rag_strategy_id: Optional[int] = None) -> str:
        existing_sql = """
            SELECT id FROM courses
            WHERE name = %s AND institution = %s AND year = %s AND semester_id = %s;
        """
        existing = self.cm.select_one(existing_sql, (name, institution, year, semester_id))
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Course '{name}' at '{institution}' for {year} semester {semester_id} already exists."
            )

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

    def read_course(self, course_id: str) -> Optional[dict]:
        sql = """
            SELECT 
                c.id, c.name, c.institution, c.semester_id, c.year, c.created_at,
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
                c.semester_id, c.year, c.created_at, i.name AS instructor_name,
                rs.id AS rag_strategy_id, rs.type_name AS rag_strategy_name
            FROM courses c
            LEFT JOIN instructors i ON c.instructor_id = i.id
            LEFT JOIN rag_strategies rs ON c.rag_strategy_id = rs.id
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
    

    def update_course(self, course_id: str, updates: dict) -> dict:
        """
        Dynamically update course fields and return the updated record.
        """
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields provided for update."
            )

        # Build dynamic SQL set clause
        set_clause = ", ".join([f"{key} = %s" for key in updates.keys()])
        values = list(updates.values()) + [course_id]

        sql = f"""
            UPDATE courses
            SET {set_clause}
            WHERE id = %s
            RETURNING id, name, institution, semester_id, year,
                        instructor_id, created_at;
        """

        updated = self.cm.select_one(sql, tuple(values))
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course with id={course_id} not found."
            )

        return updated

    # ======================================================
    # STUDENTS
    # ======================================================
    def create_student(self, name: str, discord_id: str, course_id: str) -> str:
        # Step 1: Check if the student already exists by Discord ID
        existing_sql = "SELECT id FROM students WHERE discord_id = %s;"
        existing = self.cm.select_one(existing_sql, (discord_id,))

        if existing:
            student_id = existing["id"]

            # Step 2: Check if already registered for this course
            link_sql = "SELECT 1 FROM student_courses WHERE student_id = %s AND course_id = %s;"
            linked = self.cm.select_one(link_sql, (student_id, course_id))

            if not linked:
                # Register this student in the new course
                self.cm.execute(
                    "INSERT INTO student_courses (student_id, course_id) VALUES (%s, %s);",
                    (student_id, course_id),
                )
            # Either way, return the same ID (no error)
            return str(student_id)

        # Step 3: Student doesn’t exist yet → create and link
        sql_insert_student = """
            INSERT INTO students (name, discord_id)
            VALUES (%s, %s)
            RETURNING id;
        """
        student_id = self.cm.insert_one(sql_insert_student, (name, discord_id))
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
