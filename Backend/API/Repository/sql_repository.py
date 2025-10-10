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
        sql = "SELECT * FROM documents WHERE id = %s;"
        return self.cm.select_one(sql, (doc_id,))

    def delete_document(self, doc_id: str) -> None:
        sql = "DELETE FROM documents WHERE id = %s;"
        self.cm.execute(sql, (doc_id,))

    def read_all_documents(
        self,
        course_id: Optional[str] = None,
        file_type_id: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
        order_by: str = "uploaded_at",
        order_dir: str = "desc",
    ) -> List[dict]:
        filters = []
        params = []

        if course_id:
            filters.append("course_id = %s")
            params.append(course_id)
        if file_type_id:
            filters.append("file_type_id = %s")
            params.append(file_type_id)

        where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
        sql = f"""
            SELECT *
            FROM documents
            {where_clause}
            ORDER BY {order_by} {order_dir}
            LIMIT %s OFFSET %s;
        """
        params.extend([limit, offset])
        return self.cm.select_all(sql, tuple(params))
