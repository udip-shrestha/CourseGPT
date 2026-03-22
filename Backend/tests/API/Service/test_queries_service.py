import pytest
from fastapi import HTTPException, status
from API.Service.queries_service import QueryService
from API.Service.rag_service import RAGService
from API.Repository.i_sql_repository import ISQLRepository


# ==========================================================
# ASK QUESTION
# ==========================================================

def test_ask_question_success(query_service: QueryService, mock_rag_service: RAGService):
    """Should call rag_service.query and return its result."""
    mock_rag_service.query.return_value = {"answer": "Hi", "sources": ["s1"]}

    result = query_service.ask_question(
        course_id="c1",
        course={"id": "c1", "rag_strategy_id": 1},
        student_id="stu1",
        question="Hello?"
    )

    mock_rag_service.query.assert_called_once_with(
        course_id="c1",
        course={"id": "c1", "rag_strategy_id": 1},
        question="Hello?",
        validate=False,
        student_id="stu1"
    )

    assert result == {"answer": "Hi", "sources": ["s1"]}


def test_ask_question_empty(query_service: QueryService):
    """Empty questions should return a user message instead of calling RAG."""
    result = query_service.ask_question(
        course_id="c1",
        course={"id": "c1", "rag_strategy_id": 1},
        student_id=None,
        question="   "
    )

    assert result["answer"] == "Question cannot be empty."
    assert result["sources"] == ""


# ==========================================================
# READ QUERY (single)
# ==========================================================

def test_get_query_success(query_service: QueryService, mock_sql_repo: ISQLRepository):
    """Should return a query record when found."""
    mock_sql_repo.read_query.return_value = {"id": "q1", "course_id": "c1"}

    q = query_service.get_query("c1", "q1")

    mock_sql_repo.read_query.assert_called_once_with("c1", "q1")
    assert q["id"] == "q1"


def test_get_query_not_found(query_service: QueryService, mock_sql_repo: ISQLRepository):
    """Should raise 404 when query does not exist."""
    mock_sql_repo.read_query.return_value = None

    with pytest.raises(HTTPException) as exc:
        query_service.get_query("c1", "missing")

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in exc.value.detail.lower()


# ==========================================================
# READ QUERIES FOR STUDENT
# ==========================================================

def test_get_student_queries(query_service: QueryService, mock_sql_repo: ISQLRepository):
    """Should fetch queries for a specific student/course."""
    mock_sql_repo.read_queries_for_student_course.return_value = {
        "total": 1,
        "queries": [{"id": "q1", "text": "hi"}]
    }

    data = query_service.get_student_queries("c1", "stu1")

    mock_sql_repo.read_queries_for_student_course.assert_called_once()
    assert data["total"] == 1
    assert len(data["queries"]) == 1


# ==========================================================
# READ QUERIES FOR COURSE
# ==========================================================

def test_get_course_queries(query_service: QueryService, mock_sql_repo: ISQLRepository):
    """Should retrieve paginated queries for a course."""
    mock_sql_repo.read_all_queries_for_course.return_value = {
        "total": 2,
        "queries": [{"id": "q1"}, {"id": "q2"}]
    }

    result = query_service.get_course_queries("c1")

    mock_sql_repo.read_all_queries_for_course.assert_called_once()
    assert result["total"] == 2
    assert len(result["queries"]) == 2


# ==========================================================
# DELETE QUERY
# ==========================================================

def test_delete_query_success(query_service: QueryService, mock_sql_repo: ISQLRepository):
    """Should delete an existing query."""
    mock_sql_repo.read_query.return_value = {"id": "q1"}

    result = query_service.delete_query("c1", "q1")

    mock_sql_repo.delete_query.assert_called_once_with("c1", "q1")
    assert result == {"status": "deleted", "course_id": "c1", "query_id": "q1"}


def test_delete_query_not_found(query_service: QueryService, mock_sql_repo: ISQLRepository):
    """Should raise 404 if trying to delete a query that does not exist."""
    mock_sql_repo.read_query.return_value = None

    with pytest.raises(HTTPException) as exc:
        query_service.delete_query("c1", "missing")

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in exc.value.detail.lower()
