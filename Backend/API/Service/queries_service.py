from fastapi import HTTPException, status
from typing import Dict, List, Optional

from API.Repository.i_sql_repository import ISQLRepository
from API.Service.rag_service import RAGService
from API.Util.decorators import clean_service


class QueryService:
    """
    Handles student queries and question history within a course.

    Responsibilities:
      1️⃣ Running the RAG pipeline to answer questions.
      2️⃣ Persisting Q/A interactions in SQL.
      3️⃣ Retrieving all queries for a student.
      4️⃣ Retrieving all queries for a course (all students).
      5️⃣ Reading a single query by ID.
      6️⃣ Deleting a query.

    Mirrors the structure and interface style of DocumentService for consistency.
    """

    def __init__(self, sql_repo: ISQLRepository, rag_service: RAGService):
        self.sql_repo = sql_repo
        self.rag_service = rag_service

    @clean_service
    def ask_question(
        self,
        course_id: str,
        course: dict,
        student_id: Optional[str],
        question: str
    ) -> dict:
        """
        Executes the RAG pipeline:
          1. Validates course existence.
          2. Sends the question to the RAG strategy.
          3. Saves the resulting Q/A pair to SQL.
        """

        if not question.strip():
            return {"answer": "Question cannot be empty.", "sources": ""}

        # --- Run RAG strategy (automatically logs query in DB) ---
        return self.rag_service.query(
            course_id=course_id,
            course=course,
            student_id=student_id,
            question=question
        )

    @clean_service
    def get_student_queries(
        self,
        course_id: str,
        student_id: str,
        limit: int = 10,
        offset: int = 0,
        order_by: str = "asked_at",
        order_dir: str = "desc"
    ) -> dict:
        """
        Fetch paginated queries for a specific student in a specific course.
        Returns total count + paginated query list.
        """

        return self.sql_repo.read_queries_for_student_course(
            student_id=student_id,
            course_id=course_id,
            limit=limit,
            offset=offset,
            order_by=order_by,
            order_dir=order_dir,
        )

    @clean_service
    def get_course_queries(
        self,
        course_id: str,
        limit: int = 10,
        offset: int = 0,
        order_by: str = "asked_at",
        order_dir: str = "desc",
    ) -> dict:
        """
        Fetch paginated queries made by ANY student in the course.

        Mirrors DocumentService.read_all_documents:
          • Supports limit/offset
          • Supports ordering
          • Returns {"total": X, "queries": [...]}
        """
        return self.sql_repo.read_all_queries_for_course(
            course_id=course_id,
            limit=limit,
            offset=offset,
            order_by=order_by,
            order_dir=order_dir,
        )

    @clean_service
    def get_query(self, course_id: str, query_id: str) -> dict:
        """
        Retrieve a specific query record (Q/A pair) by ID.
        Enforces course ownership for safety.
        """

        query = self.sql_repo.read_query(course_id, query_id)
        if not query:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Query with id={query_id} not found in course={course_id}"
            )

        return query

    @clean_service
    def delete_query(self, course_id: str, query_id: str) -> dict:
        """
        Permanently deletes a query/Q&A record.
        Validates existence before deleting.
        """

        existing = self.sql_repo.read_query(course_id, query_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Query with id={query_id} not found."
            )

        self.sql_repo.delete_query(course_id, query_id)

        return {
            "status": "deleted",
            "course_id": course_id,
            "query_id": query_id
        }
